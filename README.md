# LongTailIdentity
Establishing identity of long tail entities and events from text 

### Project structure
The project consists of two main folders: 

`EntityIdentity`, containing the experiments for establishing identity of long-tail entities, and 

`EventIdentity`, containing the experiments for establishing identity of long-tail events.

The structure within each of these two folders is identical, and consists of the following folders:
`data_preparation` contains scripts that prepare all the evaluation data needed for the experiment.
`data` contains the original, input data, as well as the generated task data and the output data by the systems and the baselines.
`baselines` contains implementation of several baselines.
`src` contains the code of the profiler.
