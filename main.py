from weather_analysis import CleanerExtractor
import argparse

def main(args):
    path = args.path # e.g., 'full_df.csv'
    threshold = args.threshold # e.g., 0.5
    output_path = args.output # e.g., 'weather_analysis_05_thresh.csv'

    cleaner = CleanerExtractor(path, threshold)
    cleaner.fit()
    cleaner.save_resuts(output_path)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run the cleaning analysis for step per second data.'
    )
    parser.add_argument('--path', 
                        required=True, 
                        action='store',
                        help='root of the data')
    
    parser.add_argument('--threshold', 
                        type=float,
                        action='store', 
                        default=0.0,
                        help='threshold to filter out step per seconds. Default: 0.0')
    
    parser.add_argument('--output', 
                        required=True, 
                        action='store',
                        help='root where to save the clean data')
    
    args = parser.parse_args()
    main(args)