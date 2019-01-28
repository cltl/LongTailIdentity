# LongTailIdentity
*The role of knowledge in establishing long-tail identity*

### Project structure
The project consists of these five folders: 
* `data_preparation` contains scripts that prepare all the evaluation data needed for the experiment.
* `data` contains the original, input data, as well as the generated task data and the output data by the systems and the baselines.
* `evaluation` contains scripts that evaluate the baselines and our system, by comparing the gold data and system data, both found in the `data` folder.
* `resources` has several resources that are used by the systems.
* `systems` contains implementation of several baselines, as well as of the clustering on top of our profiler run.
