# Hypergraph Partitioner Collection

This repository contains a collection of commonly used (hyper)graph partitioners and provides scripts to simplify setup and execution.

## Installation

Simply execute:

```bash
git submodule init
git submodule update
./install.sh
```

## Worflow for Running Experiments

This assumes you are using bash or a compatible shell.

- Create a folder that contains the graphs for the experiment (and preferably nothing else)
- Adjust the paths in `env.sh` as required and execute `source <path-to-repo>/env.sh`
- Create a folder for the experiments and an `experiment.json` file within it
- Define the experimental setup within `experiment.json` (you can use `experiments/example_experiment.json` as orientation). Specifically, the path to the graphs folder is set here
- Execute `<path-to-repo>/experiments/setup_experiments.py experiment.json` within the same folder. This will create a new subfolder with a file `workload.txt` that contains one line for each run of the experiment
- Run the workload, either directly or by using `<path-to-repo>/experiments/execute_experiments.py experiment.json`
- After the experiment is completed: Use `<path-to-repo>/experiments/grep_experiment_results.sh <generated-folder>` to collect the results into csv files

Notes:
- The partitioner calls are implemented by the python scripts in `scripts/`. The scripts can be extended, e.g. to collect additonal stats
- To add a new partitioner, an according script must be added and the mapping in `experiments/setup_experiments.py` (as well as `experiments/execute_experiments.py`) must be updated accordingly

## Executing a (Hyper)graph Partitioner as Standalone

Before you can use the python interface scripts for each partitioner (see folder `scripts`), please make sure that `env.sh` contains the correct paths to each subprogram required for execution. If so, execute `source env.sh` to make the changes visible for the python interfaces. Afterwards, you can start a partitioner by executing the following command:

Serial Partitioner:
```bash
<partitioner>.py <graph/hypergraph-file> <number-of-blocks> <epsilon> <seed> <objective> <timelimit>
```

Parallel Partitioner
```bash
<partitioner>.py <graph/hypergraph-file> <number-of-threads> <number-of-blocks> <epsilon> <seed> <objective> <timelimit>
```

## Hypergraph Formats

__hMetis__, __KaHyPar__, __MT-KaHyPar__, and __Hype__ require that the input hypergraph file is in *hMetis* format (see hMetis User Guide). __Parkway__ uses a binary representation of an already distributed hypergraph. However, our python interface expects the hypergraph in *hMetis* format and the conversion to the internal *Parkway* format is done inside our python script. Please make sure that the helper tool *HgrToParkway* is built inside the __MT-KaHyPar__ partitioner (`make HgrToParkway`).

__Mondriaan__ uses a matrix representation as input hypergraph file. You can convert a hypergraph in *hMetis* format to *Mondriaan* form via tool *HgrToMondriaanMtx* inside the __KaHyPar__ partitioner (`make HgrToMondriaanMtx`). Please make sure that the corresponding *hMetis* hypergraph file is inside the same folder than the *Mondriaan* hypergraph file if you execute the mondriaan python interface script.

__PaToH__ and __Zoltan__ also use different hypergraph file representations. You can convert a *hMetis* hypergraph file via *HgrToPatoh* (inside the __KaHyPar__ partitioner) resp. *HgrToZoltan* (inside the __MT-KaHyPar__ partitioner) to *PaToH* resp. *Zoltan* hypergraph file format. Please make sure that __Zoltan__ hypergraph file names ends with `.zoltan.hg`.
