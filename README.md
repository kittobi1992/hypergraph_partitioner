# Hypergraph Partitioner Collection

This repository contains a collection of common used (hyper)graph partitioner and simplifies and unifies setup and execution of them.

## Installation

Simply execute:

```bash
git submodule init
git submodule update
./install.sh
```

## Execution

Before you can use the python interface scripts for each partitioner (see folder `scripts`), please make sure that `env.sh` contains the correct paths to each subprogram required for execution. If so, execute `source env.sh` to make changes visible for the python interaces. Afterwards, you can start a partitioner by executing the following command:

```bash
<partitioner>.py <graph/hypergraph-file> <number-of-threads> <number-of-blocks> <epsilon> <seed> <objective> <timelimit>
```