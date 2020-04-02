# Hypergraph Partitioner Collection

This repository contains a collection of common used (hyper)graph partitioner and simplifies and unifies setup and execution of them.

## Installation

Simply execute:

```bash
git submodule init
git submodule update
./install.sh
```

## Execute a (Hyper)graph Partitioner

Before you can use the python interface scripts for each partitioner (see folder `scripts`), please make sure that `env.sh` contains the correct paths to each subprogram required for execution. If so, execute `source env.sh` to make changes visible for the python interaces. Afterwards, you can start a partitioner by executing the following command:

Serial Partitioner:
```bash
<partitioner>.py <graph/hypergraph-file> <number-of-blocks> <epsilon> <seed> <objective> <timelimit>
```

Parallel Partitioner
```bash
<partitioner>.py <graph/hypergraph-file> <number-of-threads> <number-of-blocks> <epsilon> <seed> <objective> <timelimit>
```

## Hypergraph Formats

__hMetis__, __KaHyPar__, __MT-KaHyPar__ and __Hype__ requires that the input hypergraph file is in *hMetis* format (see hMetis User Guide). __Parkway__ uses a binary representation of a already distributed hypergraph. However, our python interface expects that the hypergraph is also in *hMetis* format and the conversion to the internal *Parkway* format is done inside our python script. Please make sure that the helper tool *HgrToParkway* is built inside the __MT-KaHyPar__ partitioner (`make HgrToParkway`).

__Mondriaan__ uses a matrix representation as input hypergraph file. You can convert a hypergraph in *hMetis* format to *Mondriaan* form via tool *HgrToMondriaanMtx* inside the __KaHyPar__ partitioner (`make HgrToMondriaanMtx`). Please make sure that the corresponding *hMetis* hypergraph file is inside the same folder than the *Mondriaan* hypergraph file if you execute the mondriaan python interface script.

__PaToH__ and __Zoltan__ also uses different hypergraph file representations. You can convert a *hMetis* hypergraph file via *HgrToPatoh* (inside the __KaHyPar__ partitioner) resp. *HgrToZoltan* (inside the __MT-KaHyPar__ partitioner) to *PaToH* resp. *Zoltan* hypergraph file format. Please make sure that __Zoltan__ hypergraph file names ends with `.zoltan.hg`.