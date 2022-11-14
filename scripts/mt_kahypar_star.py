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
import shlex
import shutil

###################################
# SETUP ENV
###################################
algorithm = "MT-KaHyPar-Star-Partitioning"
mt_kahypar = os.environ.get("MT_KAHYPAR") + "Graph"
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
parser.add_argument("--name", type=str, default = "")
parser.add_argument("--args", type=str, default = "")

args = parser.parse_args()

if args.name != "":
  algorithm = args.name

dir_path = os.path.dirname(mt_kahypar)
args_list = shlex.split(args.args)

# Run MT-KaHyPar
mt_kahypar_proc = subprocess.Popen([mt_kahypar,
                                    "-h" + args.graph,
                                    "-k" + str(args.k),
                                    "-e" + str(args.epsilon),
                                    "--seed=" + str(args.seed),
                                    "-o" + str(args.objective),
                                    "-mdirect",
                                    "-p"+ f"{dir_path}/../../../config/default_preset.ini",
                                    "--s-num-threads=" + str(args.threads),
                                    "--verbose=false",
                                    "--sp-process=true",
                                    "--input-file-format=metis",
                                    *args_list],
                                   stdout=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid)

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
imbalance = 1.0
timeout = "no"
failed = "no"
num_nodes = 0
num_separated = 0
separated_weight = 0
num_separated_in_community_detection = 0
is_mesh_graph = False

if mt_kahypar_proc.returncode == 0:
  # Extract metrics out of MT-KaHyPar output
  for line in out.split('\n'):
    s = str(line).strip()
    if "RESULT" in s:
      km1 = int(s.split(" km1=")[1].split(" ")[0])
      cut = int(s.split(" cut=")[1].split(" ")[0])
      total_time = float(s.split(" totalPartitionTime=")[1].split(" ")[0])
      imbalance = float(s.split(" imbalance=")[1].split(" ")[0])
      num_nodes = int(s.split(" total_num_nodes=")[1].split(" ")[0])
      num_separated = int(s.split(" num_separated=")[1].split(" ")[0])
      separated_weight = int(s.split(" separated_weight=")[1].split(" ")[0])
      is_mesh_graph = bool(s.split(" is_mesh_graph=")[1].split(" ")[0])
elif mt_kahypar_proc.returncode == -signal.SIGTERM:
  total_time = args.timelimit
  timeout = "yes"
else:
  failed = "yes"

# CSV format: algorithm,graph,timeout,seed,k,epsilon,num_threads,imbalance,totalPartitionTime,objective,km1,cut,failed,num_nodes,num_separated,separated_weight,is_mesh_graph
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
      num_nodes,
      num_separated,
      separated_weight,
      num_separated_in_community_detection,
      is_mesh_graph,
      sep=",")
