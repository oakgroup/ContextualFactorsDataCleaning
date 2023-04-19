import os
import pandas as pd
import numpy as np
from scipy.stats import trim_mean, iqr


class CleanerExtractor():

    def __init__(
            self,
            path: str,
            folder_path: str,
            threshold: float
            ) -> None:

        # path for csv file that has: 
        # timestamp, patient, day, cohort, step per sec, indoor prob        
        self.data_path = path
        self.folder_path = folder_path
        self.threshold = threshold
        self.df = pd.DataFrame([])
        
        self._daily_step_count = []
        self._daily_stats = []
        self._hot_to_cold_daily_stats = []

        self.extracted_df = pd.DataFrame([])
        self.full_df = pd.DataFrame([])


    def _load_dataframe(self):
        self.df = pd.read_csv(self.data_path)

        #we are just interested in outdoor envs
        self.df.drop(self.df[self.df.IndoorProb != 100].index, inplace=True)
        return self


    def _extract_daily_step_count(self, count_df):
        num_days = list(range(1,8))
        step_count = []
        nan_step_count = []

        for i,group in count_df.groupby('Day'):
            step_count.append(
                (i,sum(group['StepPerSec'].values))
                )
            num_days.remove(int(i[-1]))
        if num_days:
            for d in num_days:
                # we use NaN to deal with missing days from the subject self.path
                nan_step_count.append((f'Day{d}', 'NaN'))
                
        self._daily_step_count = step_count + nan_step_count
        return self
    

    def _extract_weather_statistics(self):
        daily_stats = []
        non_valid_stats = []
        
        num_days = list(range(1,8))
        for f in os.listdir(self.folder_path):
            if f.startswith('weather') and f.endswith('.json'):
                w_file = pd.read_json(os.path.join(self.folder_path, f))

                # we remove every seen day
                day = f.split('-')[3]
                num_days.remove(int(day[-1]))

                daily_stats.append((day,
                    w_file['data'][0]['temp'],
                    w_file['data'][0]['wind_speed'],
                    w_file['data'][0]['wind_dir'],
                    w_file['data'][0]['precip']))
                #format: day, temp, wind speed, wind dir, precip, snow

        if num_days:
            for d in num_days:
                # we use NaN to deal with missing days from the subject self.path.
                # These NaNs are related to the features of each missing day.
                non_valid_stats.append((f'Day{d}', 'NaN', 'NaN', 'NaN', 'NaN'))

        self._hot_to_cold_daily_stats = sorted(daily_stats, key=lambda x: x[1], reverse=True)
        self._daily_stats = daily_stats + non_valid_stats
        return self
    

    def _extract_daily_stats(self, feat, day=None):
        d_df = self.df[self.df['Day']==day] if day is not None else self.df
        return np.array([
            [np.mean(d_df[feat])],
            [np.median(d_df[feat])],
            [np.std(d_df[feat])],
            [np.max(d_df[feat])],
            [np.min(d_df[feat])],
            [iqr(self.df[feat])],
            [trim_mean(self.df[feat], 0.1)]
        ])
    

    def extract(self, df, id, counts):
        self._extract_weather_statistics()

        step_level = ['StepPerSec', 'StepPerMin']
        stats = [
            'mean', 
            'median', 
            'std', 
            'max', 
            'min', 
            'IQR', 
            'trim_mean10'
        ]
        
        #stats overall aggregate all the daily stats on step per sec and step per mins (cadence) without considering the daily stats
        stats_overall = pd.concat([
            pd.DataFrame(
                np.swapaxes(self._extract_daily_stats(df, s), 0,1), columns=[f'{s}_{i}' for i in stats]
            ) for s in step_level], axis=1)
        #stats daily aggregate all the daily stats on step per sec and step per mins (cadence) on the daily level
        stats_daily = pd.concat([
            pd.DataFrame(
                np.swapaxes(self._extract_daily_stats(df, s, f'Day{j}'), 0,1), columns=[f'Day{j}_{s}_{i}' for i in stats]
            ) for j in range(1,8) for s in step_level], axis=1)

        # we create mnaually a different dataset for weather
        weather_stats = pd.DataFrame(
            # data for dataframe below
            np.swapaxes(
                np.array(
                [[self._hot_to_cold_daily_stats[0][0]], 
                [self._hot_to_cold_daily_stats[0][1]], 
                [self._hot_to_cold_daily_stats[-1][0]], 
                [self._hot_to_cold_daily_stats[-1][1]]] 
                +[[self._daily_stats[i][j]] for i in range(7) for j in range(2,5)]
                +[[self._daily_stats[i][1]] for i in range(7)]), 0,1
            ), 
            # columns: hottest day, hottest temp, and coldest ones + daily wind speed, dir and precip.
            # columns name pipeline below
            columns=[
                'hottest_day', 'hottest_temp', 'coldest_day', 'coldest_temp'] \
                +[f'Day{i}_wind_speed' for i in range(1,8)]
                +[f'Day{i}_wind_dir' for i in range(1,8)]
                +[f'Day{i}_precip' for i in range(1,8)]
                +[f'Day{i}_temp' for i in range(1,8)
            ]
        )

        extracted_df = pd.concat([counts, pd.DataFrame([sum(df['StepPerSec'].values)], columns=['NumOfSteps']),\
            pd.DataFrame([id], columns=['ID']), stats_overall, weather_stats, stats_daily], axis=1)

        self.extracted_df.append(extracted_df)

        return self


    def fit(self):
        final_df = pd.DataFrame()
        for id, group in self.df.groupby('Patient'):
            walking = group[group['StepPerSec'] > self.threshold]
            walking.reset_index(inplace=True)
            walking['StepPerMin'] = [el*60 for el in walking['StepPerSec'].values]

            counts = self._extract_daily_step_count(walking)
            counts_df = pd.DataFrame(np.swapaxes(np.array([[counts[i][1]] for i in range(7)]), 0,1), columns=[f'Day{i}_stepcount' for i in range(1,8)])
            
            self.extract(walking, id, counts_df)
            self.full_df = pd.concat([final_df, self.extracted_df])
        
        return self
    

    def save_resuts(self, output_path):
        self.full_df.to_csv(output_path)