The data preparation is executed in the following notebooks:
1. `Prepare input data.ipynb` - this notebook prepares the input and gold data for the task - the partial version that was also annotated by students. This script uses the output prepared by another notebook called `Dump Data.ipynb`, found in the `AnnotatingEntityProfiles/analysis` project.
2. `Generate Full Data.ipynb` - this notebook prepares the input and gold data for the task - the FULL version that was not annotated by students but has bigger size.
3. `Analyses.ipynb` - various analysis useful when preparing the input data.
4. `Append EL data.ipynb` - this notebook attempts to append data from EL datasets that increases the existing ambiguity (not used in the current version of the data)

Moreover, the python script `evaluate.py` is used to compute the Adjusted Rand Index scores between the clusters in the gold data and those of the system output.
