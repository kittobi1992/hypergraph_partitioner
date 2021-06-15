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

###################################
# SETUP ENV
###################################
algorithm = "KaHyPar-K-IPW"
kahypar_k = os.environ.get("KAHYPAR_IPW")
kahypar_k_config = os.environ.get("KAHYPAR_K_CONFIG")
assert (kahypar_k != None and kahypar_k_config != None), "check env.sh"
###################################

parser = argparse.ArgumentParser()
parser.add_argument("graph", type=str)
parser.add_argument("k", type=int)
parser.add_argument("epsilon", type=float)
parser.add_argument("seed", type=int)
parser.add_argument("objective", type=str)
parser.add_argument("timelimit", type=int)

args = parser.parse_args()

# Read hypergraph size/weight
with open(str(args.graph)) as hypergraph:
  total_weight = 0
  for line in hypergraph:
      hg_params = line.split()
      is_weighted = len(hg_params) >= 5 and hg_params[4] in ['1', '3']
      assert (not is_weighted)
      total_weight = int(hg_params[1])
      break
assert (total_weight > 0)
part_weight = math.ceil(float(1 + args.epsilon) * total_weight / args.k)
weight_list = [str(int(part_weight)) for _ in range(0, args.k)]

# Run KaHyPar-K
kahypar_k_proc = subprocess.Popen([kahypar_k,
                                   "-h" + args.graph,
                                   "-k" + str(args.k),
                                   "-e" + str(args.epsilon),
                                   "--seed=" + str(args.seed),
                                   "-o" + str(args.objective),
                                   "-mdirect",
                                   "-p" + kahypar_k_config,
                                   "--sp-process=true",
                                   "--use-individual-part-weights=true",
                                   "--part-weights"] + weight_list,
                                  stdout=subprocess.PIPE, universal_newlines=True)

def kill_proc():
	kahypar_k_proc.terminate() #signal.SIGTERM

t = Timer(args.timelimit, kill_proc)
t.start()
out, err = kahypar_k_proc.communicate()
t.cancel()
end = time.time()

total_time = 2147483647
cut = 2147483647
km1 = 2147483647
imbalance = 1.0
timeout = "no"
failed = "no"

if kahypar_k_proc.returncode == 0:
  # Extract metrics out of KaHyPar-CA output
  for line in out.split('\n'):
    s = str(line).strip()
    if "RESULT" in s:
      km1 = int(s.split(" km1=")[1].split(" ")[0])
      cut = int(s.split(" cut=")[1].split(" ")[0])
      total_time = float(s.split(" totalPartitionTime=")[1].split(" ")[0])
      imbalance = float(s.split(" imbalance=")[1].split(" ")[0])
elif kahypar_k_proc.returncode == -signal.SIGTERM:
  timeout = "yes"
else:
  failed = "yes"

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