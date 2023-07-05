#!/usr/bin/python3
import subprocess
import ntpath
import argparse
import time
import re
import math
import os
import os.path
from threading import Timer
import signal
import hierarchical_process_mapping_helper

###################################
# SETUP ENV
###################################
algorithm = "KaFFPa-Eco"
kaffpa = os.environ.get("KAFFPA")
assert (kaffpa != None), "check env.sh"
###################################

parser = argparse.ArgumentParser()
parser.add_argument("graph", type=str)
parser.add_argument("k", type=int)
parser.add_argument("epsilon", type=float)
parser.add_argument("seed", type=int)
parser.add_argument("objective", type=str)
parser.add_argument("timelimit", type=int)
parser.add_argument("--hierarchy_parameter_string", type=str, default="")
parser.add_argument("--distance_parameter_string", type=str, default="")
parser.add_argument("--config", type=str, default = "")
parser.add_argument("--name", type=str, default = "")

args = parser.parse_args()

if args.name != "":
  algorithm = args.name

# Run KaFFPa
output_part_file = args.graph + ".part." + str(args.k) + "." + str(args.seed) + "." + algorithm
perform_process_mapping = args.hierarchy_parameter_string != "" and args.distance_parameter_string != ""
if perform_process_mapping:
  args.k = hierarchical_process_mapping_helper.get_number_of_blocks(args.hierarchy_parameter_string)
kaffpa_command = [kaffpa,
                  args.graph,
                  "--k=" + str(args.k),
                  "--seed=" + str(args.seed),
                  "--imbalance=" + str(args.epsilon * 100.0),
                  "--preconfiguration=eco",
                  "--output_filename=" + output_part_file]
if perform_process_mapping:
  kaffpa_command.extend(["--hierarchy_parameter_string=" + args.hierarchy_parameter_string,
                         "--distance_parameter_string=" + args.distance_parameter_string,
                         "--enable_mapping"])
kaffpa_proc = subprocess.Popen(kaffpa_command,
                               stdout=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid)

def kill_proc():
	os.killpg(os.getpgid(kaffpa_proc.pid), signal.SIGTERM)

t = Timer(args.timelimit, kill_proc)
t.start()
out, err = kaffpa_proc.communicate()
t.cancel()
end = time.time()

total_time = 2147483647
cut = 2147483647
km1 = 2147483647
process_mapping = 2147483647
imbalance = 1.0
timeout = "no"
failed = "no"

if kaffpa_proc.returncode == 0:
  # Extract metrics out of MT-KaHIP output
  for line in out.split('\n'):
    s = str(line).strip()
    if "cut" in s:
      cut = int(s.split('cut')[1])
      km1 = int(s.split('cut')[1])
    if "balance" in s:
      imbalance = float(s.split('balance')[1]) - 1.0
    if "time spent for partitioning" in s:
      total_time = float(s.split('time spent for partitioning')[1])
  if perform_process_mapping:
     process_mapping = hierarchical_process_mapping_helper.verify_process_mapping_partition(
        args.graph, output_part_file, "metis",
        args.hierarchy_parameter_string, args.distance_parameter_string,
        algorithm, args.k, args.epsilon, args.seed)
  if os.path.exists(output_part_file):
    os.remove(output_part_file)
elif kaffpa_proc.returncode == -signal.SIGTERM:
  timeout = "yes"
else:
  failed = "yes"

if not perform_process_mapping:
  # CSV format: algorithm,graph,timeout,seed,k,epsilon,num_threads,imbalance,totalPartitionTime,objective,km1,cut,failed
  print(algorithm,
        ntpath.basename(args.graph),
        timeout,
        args.seed,
        args.k,
        args.epsilon,
        1,
        imbalance,
        total_time,
        args.objective,
        km1,
        cut,
        failed,
        sep=",")
else:
  # CSV format: algorithm,graph,timeout,seed,k,epsilon,num_threads,imbalance,totalPartitionTime,objective,km1,cut,process_mapping_obj,failed
  print(algorithm,
        ntpath.basename(args.graph),
        timeout,
        args.seed,
        args.k,
        args.epsilon,
        1,
        imbalance,
        total_time,
        args.objective,
        km1,
        cut,
        process_mapping,
        failed,
        sep=",")
