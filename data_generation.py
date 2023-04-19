from data_generator import DataGenerator
import argparse

def main(args):
    folder_path = args.folder_path # e.g., 'mobilised-contextual-factors-v1'
    info_path = args.info_path # e.g., 'CF_RWS_missingfiles-Sheet1.csv'
    output_path = args.output # e.g., 'full_df.csv'

    cleaner = DataGenerator(folder_path, info_path)
    cleaner.fit()
    cleaner.save_resuts(output_path)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run the data generation from raw data folder.'
    )
    parser.add_argument('--folder_path', 
                        required=True, 
                        action='store',
                        help="root of the subjects' contextualized factors data.")
    
    parser.add_argument('--info_path', 
                        required=True, 
                        action='store',
                        help="root of the statistics Excel file about missing data/files. Must be in .csv")
    
    parser.add_argument('--output', 
                        required=True, 
                        action='store',
                        help='root where to save the data to be used for weather analysis')
    
    args = parser.parse_args()
    main(args)