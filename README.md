This folder contains scripts and notebooks to process healthy control MC10 sensor data
for activity recognition classification.

Note:
- HC01 and HC02 datasets had battery issues so data is missing compared to the other datasets.

`requirements.txt`
1. List of package and version requirments that need to be installed to run scripts.
1. To install dependencies run: `pip install -r requirements.txt`
1. To create new dependencies file run in correct directory: `pip freeze > requirements.txt`

`activityrec.ipynb`




`meta_and_raw_data.ipynb`
1. `meta_and_raw_data_functions.py` has the functions that the notebook needs and
it is called in the notebook.
1. Summary:
    1. Loads pickle files for healthy controls
    1. Unstacks the nested dictionary data structure of the raw data
    1. Adds meta data columns to the raw data.
    1. Saves as pickle files by subject in the `.\biostamp_data\meta_and_raw_data` directory
1. Once the features are created, the feature matrix can be added to this matrix then used 
for machine learning models.





Remove
```
PreprocessFcns.py
- clip generating function (gen_clips)
- 37 feature extraction function (feature_extraction)
- includes high, band, low pass filters

TestFeatures.ipynb
- input: activity dictionary
- use gen_clips
- use feature_extraction
- check 'features'

data structure of clipped data
- using nested dictionary: example[trial][sensor]
  - trial: 0, 1, etc
  - sensor: accel, gyro
  - data
  - clip_len
```