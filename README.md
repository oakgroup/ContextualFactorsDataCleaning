# TheUniversityOfSheffield
Code for the internship @The University of Sheffield.

## How-to:
1) Run 'data_generation.py' which exploits 'data_generator.py' to generate data starting from the indicated subject folder. It relies on "data_generation_outlier_detection.ipynb" in the _notebooks_ folder
2) Run 'main.py' which exploits 'weather_analysis.py' to run a weather analysis on cadence etc, generating a statistics file in the _output path_ indicated as argument in the command line. It corresponds to _'weather_analysis.ipynb'_ experimental pipeline.

## Where-to:
* _notebooks_ contains the experimental notebooks that visually represent the pipeline to generate the files, step by step. _'10s_windowing.ipynb'_ is the first attempt to work with threshold detection, formalized in _'weather_analysis.py'_. Outlier detection pipeline can be visually exploited in 'data_generation_outlier_detection.ipynb'.
* _.py files_ are the files designated to work in a command-line fashion from your terminal.

If you are stucked in the _.py files_ please refer to the corresponding _notebooks_

## Requirements for python libraries:
* data_generator.py :
  * os, pandas, numpy, gzip, shutil

## Data
The data to be processed can be found on [GDrive](https://drive.google.com/drive/folders/14wI-6fR1POVeB2ua8qP1nlLnwliEY5pW?usp=share_link)

## Usage
TBD

