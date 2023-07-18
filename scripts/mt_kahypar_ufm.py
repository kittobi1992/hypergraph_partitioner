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
algorithm = "MT-KaHyPar-UFM"
mt_kahypar = os.environ.get("MT_KAHYPAR_UFM")
assert (mt_kahypar != None), "check env.sh"
###################################

default_args = {
  "--instance-type": "graph",
  "--input-file-format": "metis",
  "--r-jet-type": "do_nothing",
  "--r-lp-type": "label_propagation",
  "--r-lp-unconstrained": 1,
  "--r-lp-rebalancing": 0,
  "--r-lp-relative-improvement-threshold": "0.001",
  "--r-fm-type": "cooling",
  "--r-fm-unconstrained-rounds": 7,
  "--r-fm-rollback-balance-violation-factor": "1.0",
  "--r-fm-imbalance-penalty-min": "0.2",
  "--r-fm-imbalance-penalty-max": "1.0",
  "--r-fm-activate-unconstrained-dynamically": 1,
  "--r-fm-unconstrained-min-improvement": "0.002",
  "--r-fm-update-penalty-locally-reverted": 1,
  "--r-fm-threshold-border-node-inclusion": "0.7",
  "--r-rebalancer-type": "rebalancer",
}

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

args_list = shlex.split(args.args)

for arg_key in default_args:
  if not any(arg for arg in args_list if (arg_key in arg)):
    args_list.append(f"{arg_key}={default_args[arg_key]}")

# Run MT-KaHyPar
mt_kahypar_proc = subprocess.Popen([mt_kahypar,
                                    "-h" + args.graph,
                                    "-k" + str(args.k),
                                    "-e" + str(args.epsilon),
                                    "--seed=" + str(args.seed),
                                    "-o" + str(args.objective),
                                    "-mdirect",
                                    "--preset-type=default",
                                    "--s-num-threads=" + str(args.threads),
                                    "--verbose=false",
                                    "--sp-process=true",
                                    "--show-detailed-timing=true",
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
preprocessing = 2147483647
coarsening = 2147483647
initial_partitioning = 2147483647
refinement = 2147483647
jet = 2147483647
rebalance_jet = 2147483647
lp = 2147483647
rebalance_lp = 2147483647
fm = 2147483647
collect_border_nodes = 2147483647
find_moves = 2147483647
rollback = 2147483647
ufm_setup = 2147483647
rebalance_fm = 2147483647
rebalance_total = 2147483647

if mt_kahypar_proc.returncode == 0:
  # Extract metrics out of MT-KaHyPar output
  for line in out.split('\n'):
    s = str(line).strip()
    if "RESULT" in s:
      km1 = int(s.split(" km1=")[1].split(" ")[0])
      cut = int(s.split(" cut=")[1].split(" ")[0])
      total_time = float(s.split(" totalPartitionTime=")[1].split(" ")[0])
      imbalance = float(s.split(" imbalance=")[1].split(" ")[0])
      preprocessing = float(s.split(" preprocessing=")[1].split(" ")[0])
      coarsening = float(s.split(" coarsening=")[1].split(" ")[0])
      initial_partitioning = float(s.split(" initial_partitioning=")[1].split(" ")[0])
      refinement = float(s.split(" refinement=")[1].split(" ")[0])
      jet = 0
      rebalance_jet = 0
      if " jet=" in s:
        jet = float(s.split(" jet=")[1].split(" ")[0]) + float(s.split(" initialize_jet_refiner=")[1].split(" ")[0])
        if " rebalance_jet=" in s:
          rebalance_jet = float(s.split(" rebalance_jet=")[1].split(" ")[0])
      lp = 0
      rebalance_lp = 0
      if " label_propagation=" in s:
        lp = float(s.split(" label_propagation=")[1].split(" ")[0]) + float(s.split(" initialize_lp_refiner=")[1].split(" ")[0])
        if " rebalance_lp=" in s:
          rebalance_lp = float(s.split(" rebalance_lp=")[1].split(" ")[0])

      fm = 0
      collect_border_nodes = 0
      find_moves = 0
      rollback = 0
      ufm_setup = 0
      rebalance_fm = 0
      if " fm=" in s:
        fm = float(s.split(" fm=")[1].split(" ")[0]) + float(s.split(" initialize_fm_refiner=")[1].split(" ")[0])
        collect_border_nodes = float(s.split(" collect_border_nodes=")[1].split(" ")[0])
        find_moves = float(s.split(" find_moves=")[1].split(" ")[0])
        rollback = float(s.split(" rollback=")[1].split(" ")[0])
        if " precompute_unconstrained=" in s:
          ufm_setup = float(s.split(" initialize_data_unconstrained=")[1].split(" ")[0]) + float(s.split(" precompute_unconstrained=")[1].split(" ")[0])
        if " rebalance_fm=" in s:
          rebalance_fm = float(s.split(" rebalance_fm=")[1].split(" ")[0])

      rebalance_total = rebalance_lp + rebalance_jet + rebalance_fm
      if " rebalance=" in s:
        rebalance_total += float(s.split(" rebalance=")[1].split(" ")[0])
elif mt_kahypar_proc.returncode == -signal.SIGTERM:
  total_time = args.timelimit
  timeout = "yes"
else:
  failed = "yes"

# CSV format: algorithm,graph,timeout,seed,k,epsilon,num_threads,imbalance,totalPartitionTime,objective,km1,cut,failed,
#             preprocessing,coarsening,initial_partitioning,refinement,jet,rebalance_jet,lp,rebalance_lp,fm,collect_border_nodes,
#             find_moves,rollback,ufm_setup,rebalance_fm,rebalance_total
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
      preprocessing, coarsening, initial_partitioning, refinement,
      jet, rebalance_jet, lp, rebalance_lp,
      fm, collect_border_nodes, find_moves, rollback, ufm_setup, rebalance_fm,
      rebalance_total,
      sep=",")
