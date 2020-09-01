#!/usr/bin/python3
import json
import argparse
import os
import subprocess
##############################
HMETIS_TO_PATOH = "/home/nikolai/hypergraph_partitioner/partitioner/kahypar/build/tools/HgrToPaToH"
HMETIS_TO_MTX = "/home/nikolai/hypergraph_partitioner/partitioner/kahypar/build/tools/HgrToMtx"
##############################
parser = argparse.ArgumentParser()
parser.add_argument("experiment", type=str)

args = parser.parse_args()

with open(args.experiment) as json_experiment:
    config = json.load(json_experiment)
    hmetis_dir = config["hmetis_instance_folder"]
    patoh_dir = config["patoh_instance_folder"]
    mondriaan_dir = config["mondriaan_instance_folder"]

    for hg in os.listdir(hmetis_dir):
        instance = hmetis_dir + "/" + hg

        # convert to patoh format
        patoh_file = str(patoh_dir + "/" + hg)
        patoh_proc = subprocess.Popen([HMETIS_TO_PATOH, str(instance), patoh_file], stdout=subprocess.PIPE, universal_newlines=True)
        if patoh_proc.wait() != 0:
            raise Exception('Could not convert hypergraph: {}'.format(instance))

        # convert to mondriaan format
        mondriaan_file = str(mondriaan_dir + "/" + hg + ".mondriaan.mtx")
        mondriaan_proc = subprocess.Popen([HMETIS_TO_MTX, str(instance), mondriaan_file], stdout=subprocess.PIPE, universal_newlines=True)
        if mondriaan_proc.wait() != 0:
            raise Exception('Could not convert hypergraph: {}'.format(instance))
