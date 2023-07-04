#!/usr/bin/python3
import subprocess
import ntpath
import argparse
import time
import re
import math
import glob,os
import os.path
from threading import Timer
import signal
import shutil

partitioner_script_folder = os.environ.get("PARTITIONER_SCRIPT_FOLDER")
assert (partitioner_script_folder != None), "check env.sh"

def process_mapping_call(instance, result_file):
  return (partitioner_script_folder + "/one_to_one_process_mapping.py " + instance + " " + result_file)

parser = argparse.ArgumentParser()
parser.add_argument("instance_dir", type=str)
parser.add_argument("experiment_dir", type=str)

args = parser.parse_args()

partitioner_calls = []
for instance in os.listdir(args.instance_dir):
  if instance.endswith(".hgr"):
    instance_path = args.instance_dir + "/" + instance
    for result_dir in os.listdir(args.experiment_dir):
      if result_dir.endswith("_results"):
        results_path = args.experiment_dir + "/" + result_dir
        results = glob.glob(results_path + "/" + instance + "*.results")
        for result_file in results:
          partitioner_call = (process_mapping_call(instance_path, result_file) +
            " >> " + result_file.replace(".results", ".process_mapping"))
          partitioner_calls.extend([partitioner_call])

with open(args.experiment_dir + "/process_mapping_workload.txt", "w") as workload_file:
  workload_file.write("\n".join(partitioner_calls))
  workload_file.write("\n")