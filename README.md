# bike-sharing

## Data Collection
src/data-preprocessing

API requests to receive all current locations of bikes from nextbike, lidlbike and mobike in Berlin (inner circle) and store them into a single database.

Add config.py file to src/ with API Keys for Deutsche Bahn API (https://developer.deutschebahn.com/store/) and database credentials.

For access to lime bike API insert phone_no to config.py and follow steps in lime_access.py (three manual steps required).

Other open data on bikes system can be accessed on https://github.com/Liyubov/tidytuesday/tree/master/data/2019/2019-04-02

## Data Analysis
src/analysis

Jupyter Notebook to analyse data.

- preprocess.ipynb contains the preprossing steps of the raw data to a usable format. 
    - raw.csv contains the data from the database
    - preprocessed.csv contains the data with added columns and fixed lat / lng
    - routed.csv contains the data with distance and waypoints
    - cleaned.csv is the cleaned routed dataset (unplausible data is removed)
    - pseudonomysed.csv is the anonymized, cleaned data, following [this standard](https://data.louisvilleky.gov/dataset/dockless-vehicles) 
    - pseudonomysed_raw.csv ist the anonymized data (NOT cleaned).

- analysis.ipynb includes analysis about provider and bike specific data

- pseudonomysed.ipynb includes analysis using the anonymized dataset (without information on providers.)

In folder bike analysis trajectories we analyze bikes trajectories (work in progress).

Additional Jupyter Notebook on data analysis:

- analysis of trajectories is described in bikes_mobility_analysis_trajectories folder

The project on data analysis is updated on gitlab. Contact Liubov if you want to hear the details: liubov.tupikina (at) cri-paris.org
