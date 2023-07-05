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
import shutil
import hierarchical_process_mapping_helper

###################################
# SETUP ENV
###################################
algorithm = "MT-KaHyPar-Graph-Q-F"
mt_kahypar = os.environ.get("MT_KAHYPAR")
assert (mt_kahypar != None), "check env.sh"
###################################

parser = argparse.ArgumentParser()
parser.add_argument("graph", type=str)
parser.add_argument("threads", type=int)
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

perform_process_mapping = args.hierarchy_parameter_string != "" and args.distance_parameter_string != ""
process_graph_file = ""
if perform_process_mapping:
  args.k = hierarchical_process_mapping_helper.get_number_of_blocks(args.hierarchy_parameter_string)
  process_graph_file_prefix = hierarchical_process_mapping_helper.get_process_graph_file_prefix(
    ntpath.basename(args.graph), algorithm, args.k, args.epsilon, args.seed)
  process_graph_file = hierarchical_process_mapping_helper.generate_hierarchical_process_graph(
    ntpath.dirname(args.graph), process_graph_file_prefix, args.hierarchy_parameter_string, args.distance_parameter_string)

# Run MT-KaHyPar
mt_kahypar_command = [mt_kahypar,
                      "-h" + args.graph,
                      "-k" + str(args.k),
                      "-e" + str(args.epsilon),
                      "--seed=" + str(args.seed),
                      "-mdirect",
                      "--preset-type=quality_flows",
                      "--instance-type=graph",
                      "--input-file-format=metis",
                      "--s-num-threads=" + str(args.threads),
                      "--verbose=true",
                      "--sp-process=true"]
if not perform_process_mapping:
  mt_kahypar_command.extend(["-o" + str(args.objective)])
else:
  mt_kahypar_command.extend(["-oprocess_mapping",
                             "--process-graph-file=" + process_graph_file])
mt_kahypar_proc = subprocess.Popen(mt_kahypar_command, stdout=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid)

def kill_proc():
	os.killpg(os.getpgid(mt_kahypar_proc.pid), signal.SIGTERM)

t = Timer(args.timelimit, kill_proc)
t.start()
out, err = mt_kahypar_proc.communicate()
t.cancel()
end = time.time()

total_time = 2147483647
cut = 2147483647
km1 = 2147483647
process_mapping = 2147483647
imbalance = 1.0
timeout = "no"
failed = "no"

if mt_kahypar_proc.returncode == 0:
  # Extract metrics out of MT-KaHyPar output
  for line in out.split('\n'):
    s = str(line).strip()
    if "RESULT" in s:
      km1 = int(s.split(" km1=")[1].split(" ")[0])
      cut = int(s.split(" cut=")[1].split(" ")[0])
      total_time = float(s.split(" totalPartitionTime=")[1].split(" ")[0])
      imbalance = float(s.split(" imbalance=")[1].split(" ")[0])
      if perform_process_mapping:
        process_mapping = int(s.split(" process_mapping=")[1].split(" ")[0])
elif mt_kahypar_proc.returncode == -signal.SIGTERM:
  total_time = args.timelimit
  timeout = "yes"
else:
  failed = "yes"

if not process_mapping:
  # CSV format: algorithm,graph,timeout,seed,k,epsilon,num_threads,imbalance,totalPartitionTime,objective,km1,cut,failed
  print(algorithm,
        ntpath.basename(args.graph),
        timeout,
        args.seed,
        args.k,
        args.epsilon,
        args.threads,
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
        args.threads,
        imbalance,
        total_time,
        args.objective,
        km1,
        cut,
        process_mapping,
        failed,
        sep=",")

if process_graph_file != "" and os.path.exists(process_graph_file):
  os.remove(process_graph_file)
