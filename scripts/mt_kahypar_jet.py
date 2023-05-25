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
algorithm = "MT-KaHyPar-JET"
mt_kahypar = os.environ.get("MT_KAHYPAR")
assert (mt_kahypar != None), "check env.sh"
###################################

default_args = {
  "--r-lp-type": "do_nothing",
  "--r-jet-type": "precomputed_ordered",
  "--r-fm-type": "do_nothing",
  "--r-rebalancer-type": "jet_rebalancer",
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
  if arg_key not in args_list:
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
                                    "--instance-type=hypergraph",
                                    "--s-num-threads=" + str(args.threads),
                                    "--verbose=false",
                                    "--sp-process=true",
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

if mt_kahypar_proc.returncode == 0:
  # Extract metrics out of MT-KaHyPar output
  for line in out.split('\n'):
    s = str(line).strip()
    if "RESULT" in s:
      km1 = int(s.split(" km1=")[1].split(" ")[0])
      cut = int(s.split(" cut=")[1].split(" ")[0])
      total_time = float(s.split(" totalPartitionTime=")[1].split(" ")[0])
      imbalance = float(s.split(" imbalance=")[1].split(" ")[0])
elif mt_kahypar_proc.returncode == -signal.SIGTERM:
  total_time = args.timelimit
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
      args.threads,
      imbalance,
      total_time,
      args.objective,
      km1,
      cut,
      failed,
      sep=",")
