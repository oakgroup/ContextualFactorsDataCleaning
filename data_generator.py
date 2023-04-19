import os
import pandas as pd
import numpy as np
import gzip
import shutil


class DataGenerator():

    def __init__(
            self,
            folder_path:str,
            info_path:str,
            verbose:bool = False,  
                 ) -> None:
        
        self._folder_path = folder_path
        self._info_path = info_path
        self._verbose = verbose

        self._info_df = pd.DataFrame([])
        self._full_df = pd.DataFrame([])

        self._context_arr, self._steps_arr = self._create_context_data()


    def _extract_files(self):
        for p in os.listdir(self._folder_path):
            i=0
            subfold = os.path.join(self._folder_path, p)
            for f in os.listdir(subfold):
                i+=1
                if f.endswith('.gz'):
                    filename = os.path.join(subfold, f)
                    extr_filename = filename.split('.gz')[0]
                    with gzip.open(filename, 'rb') as f_in:
                        with open(extr_filename, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
            if self._verbose:
                print(f'Extracted {i} files for patient {p}')

    
    def _read_info_missing(self):
        self._info_df = pd.read_csv(self._info_path)
        self._info_df.drop(columns='Unique ID ', inplace=True)
        self._info_df.replace('-', np.nan, inplace=True)

        return self

    
    def _create_context_data(self):
        ctx_l, s_l = [], []

        for p in os.listdir(self._folder_path):
            try:
                cohort = self._info_df[self._info_df['ID']==int(p)]['Cohort'].values[0]
                print('Processing subject: ', p)
                subfold = os.path.join(self._folder_path, p)
                for f in os.listdir(subfold):
                    if 'Day' in f:
                        if f.endswith('.json') and 'step' in f:
                            steps_file = pd.read_json(os.path.join(subfold, f))
                            s_l.append([[p, cohort, f.split('-')[3], float(el)] for el in steps_file['data'][0]['steps']])
                        elif f.endswith('.json') and 'Context' in f:
                            json_ctx_file = pd.read_json(os.path.join(subfold, f))
                            ctx_l.append([
                                [k, json_ctx_file['data'][0]['contextValues'][k][0]] 
                                          for k in json_ctx_file['data'][0]['contextValues']])         
            except:
                continue
        
        return np.array(ctx_l), np.array(s_l)
    

    def _reshape_data(self, arr, last_shape):
        return (
            np.reshape(
                arr, 
                (arr.shape[0], arr.shape[1], last_shape))
        )


    def fit(self):
        ctx_df = pd.DataFrame(
            self._reshape_data(self._context_arr, 2), 
            columns=['Timestamp', 'IndoorProb'])
        step_df = pd.DataFrame(
            self._reshape_data(self._context_arr, 4), 
            columns=['Patient', 'Cohort', 'Day', 'StepPerSec'])

        self._full_df = pd.concat([step_df, ctx_df], axis=1)
        self._full_df.dropna(inplace=True)

        return self
    

    def save_results(self, output_path):
        self._full_df = self._full_df[self._full_df['IndoorProb']!=50]
        self._full_df['StepPerSec'] = self._full_df['StepPerSec'].astype('float32')
        self._full_df.to_csv(output_path)
