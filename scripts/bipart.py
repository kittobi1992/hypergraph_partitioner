#!/usr/bin/python3
import subprocess
import ntpath
import argparse
import time
import re
import math
import os
import os.path
import glob
from threading import Timer
import signal

###################################
# SETUP ENV
###################################
algorithm = "BiPart"
bipart = os.environ.get("BIPART")
evaluator = os.environ.get("BIPART_EVALUATOR")
assert (bipart != None and evaluator != None), "check env.sh"
###################################

parser = argparse.ArgumentParser()
parser.add_argument("graph", type=str)
parser.add_argument("threads", type=int)
parser.add_argument("k", type=int)
parser.add_argument("epsilon", type=float)
parser.add_argument("seed", type=int)
parser.add_argument("objective", type=str)
parser.add_argument("timelimit", type=int)

args = parser.parse_args()

# Run BiPart
bipart_output_file = str(args.graph) + ".bipart.k" + str(args.k) + ".seed" + str(args.seed) + ".t" + str(args.threads) + ".epsilon" + str(args.epsilon) + ".partition"
start = time.time()
bipart_proc = subprocess.Popen([bipart,
                                '--balance=' + str(args.epsilon),
                                '-t=' + str(args.threads),
                                '-hMetisGraph',
                                '--output',
                                '--outputFile=' + str(bipart_output_file),
                                str(args.graph),
                                '25', # size of coarsest hypergraph (Default in Paper)
                                '2', # Maximum Refinement Iterations (Default in Paper)
                                str(args.k)],
                                stdout=subprocess.PIPE, universal_newlines=True)

def kill_proc():
	bipart_proc.terminate() #signal.SIGTERM

t = Timer(args.timelimit, kill_proc)
t.start()
out, err = bipart_proc.communicate()
t.cancel()
end = time.time()

total_time = end - start
cut = 2147483647
km1 = 2147483647
imbalance = 1.0
timeout = "no"
failed = "no"

if bipart_proc.returncode == 0:
  for line in out.split('\n'):
    s = str(line).strip()
    if "Timer_0" in s:
      total_time = float(s.split('Timer_0, ')[1].split(', ')[1]) / 1000.0

  out, err = subprocess.Popen([evaluator,
                               '-h' + str(args.graph),
                               '-b' + str(bipart_output_file),
                               '-k' + str(args.k)],
                              stdout=subprocess.PIPE, universal_newlines=True).communicate()

  # Extract metrics out of Mondriaan Evaluator output
  for line in out.split('\n'):
    s = str(line).strip()
    if "cut" in s:
      cut = int(s.split('cut=')[1].split(' ')[0])
    if "km1" in s:
      km1 = int(s.split('km1=')[1].split(' ')[0])
    if "imbalance" in s:
      imbalance = float(s.split('imbalance=')[1].split(' ')[0])
elif bipart_proc.returncode == -signal.SIGTERM:
  timeout = "yes"
  total_time = 2147483647
else:
  failed = "yes"
  total_time = 2147483647

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