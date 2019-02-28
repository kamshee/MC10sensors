This folder contains scripts and notebooks to process healthy control MC10 sensor data
for activity recognition classification. I've worked to improve documentation for the
code, modularized most functions for easy debugging, and hope that it will be easily
modifiable to different parts of the MC10 study. Happy coding! - Joe Lee

Note:
- HC01 and HC02 datasets had battery issues so data is missing compared to the other datasets.

`requirements.txt`
1. List of package and version requirments that need to be installed to run scripts.
1. To install dependencies run: `pip install -r requirements.txt`
1. To create new dependencies file run in correct directory: `pip freeze > requirements.txt`
1. If using Anaconda, don't use the pip method.

`1_data_extract.ipynb`
1. Requires `data_extract_functions.py` for functions.
1. Extracts raw data from health controls (HC), creates a nested dictionary structure,
and saves as a pickle file for each subject.
1. Some of the data is explored and visualized for activity recognition.
1. At the end, there is some code for clipping and sliding windows. This can be ignored.
It was an earlier idea, but we decided to use Ami's Matlab pipeline to segment the gait
cycles and possibly use DTW (dynamic time warping) to get better features.

`2_meta_and_raw_data.ipynb`
1. `meta_and_raw_data_functions.py` has the functions that the notebook needs and
it is called in the notebook.
1. Summary:
    1. Loads pickle files for healthy controls
    1. Unstacks the nested dictionary data structure of the raw data
    1. Adds meta data columns to the raw data.
    1. Saves as pickle files by subject in the `.\biostamp_data\meta_and_raw_data` directory
1. Once the features are created, the feature matrix can be added to this matrix then used 
for machine learning models.

`3_131_features.ipynb`
1. `131_features.py` contains all the functions from the notebook. They are here for
quick reference instead of going through the whole notebook.
1. This notebook converts the Matlab code from Megan's previous project using the 131
features. I've translated it into Python and tested in the notebook.
1. I've created functions to append the features to the meta and raw data matrix.
This will make it easier to load into ML models.



`PreprocessFcns.py` - You can ignore this. This was to be used for the sliding window
feature generation.
- clip generating function (gen_clips)
- 37 feature extraction function (feature_extraction)
- includes high, band, low pass filters