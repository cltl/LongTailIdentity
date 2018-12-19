# LongTailIdentity
Establishing identity of long tail entities and events from text 

### Project structure
The project consists of two main folders: 

1. `EntityIdentity`, containing the experiments for establishing identity of long-tail entities, and 
2. `EventIdentity`, containing the experiments for establishing identity of long-tail events.

The structure within each of these two folders is identical, and consists of the following folders:
* `data_preparation` contains scripts that prepare all the evaluation data needed for the experiment.
* `data` contains the original, input data, as well as the generated task data and the output data by the systems and the baselines. The folder `gold` contains two folders: `full` and `partial` - one per dataset, where the gold clusters are placed. The folder `input` has two foldes `full` and `partial` - one per dataset, each of which contains folders with annotation and text documents. The `system` folder has the output of all baselines, ready for evaluation against the gold data.
* `baselines` contains implementation of several baselines.
* `src` contains the code of the profiler.
