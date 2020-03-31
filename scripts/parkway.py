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

###################################
# SETUP ENV
###################################
algorithm = "Parkway"
parkway = os.environ.get("PARKWAY")
parkway_config = os.environ.get("PARKWAY_CONFIG")
metis_to_parkway_converter = os.environ.get("METIS_TO_PARKWAY_CONVERTER")
evaluator = os.environ.get("KAHYPAR_VERIFY_PARTITION")
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

# Convert hMetis hypergraph to Parkway format
parkway_file = args.graph + ".bin." + str(args.threads)
if not os.path.exists(parkway_file + "-0"):
  conversion_proc = subprocess.Popen([metis_to_parkway_converter,
                                      "-h" + args.graph,
                                      "-p" + str(args.threads)],
						                          stdout=subprocess.PIPE, universal_newlines=True)
# Run Parkway
parkway_proc = subprocess.Popen(["mpirun -N " +str(args.threads) + " " +
                                 parkway + " " +
                                 "-p" + str(args.k) + " " +
                                 "-c" + str(args.epsilon) + " " +
                                 "--recursive-bisection.number-of-runs=" + str(args.threads) + " " +
                                 "-o" + parkway_config + " " +
                                 "--hypergraph=" + parkway_file + " " +
                                 "--write-partitions-to-file"],
						                     stdout=subprocess.PIPE, universal_newlines=True, shell=True)

def kill_proc():
	proc.terminate() #signal.SIGTERM

t = Timer(args.timelimit, kill_proc)
t.start()
out, err = parkway_proc.communicate()
t.cancel()
end = time.time()

total_time = 0
cut = 0
km1 = 0
imbalance = 0.0
timeout = "no"
failed = "no"

if parkway_proc.returncode == 0:
  # Search for partition time in parkway output
  for line in out.split('\n'):
    s = str(line).strip()
    if "TOTAL TIME" in s:
      total_time = float(s.split('=')[1])

  # Evaluate Partition
  parkway_partition_file = parkway_file + ".part." + str(args.k) + "." + str(args.seed)
  evaluator_out, evaluator_err = subprocess.Popen([evaluator,
                                                  args.graph,
                                                  parkway_partition_file],
                                                  stdout=subprocess.PIPE, universal_newlines=True).communicate()

  # Extract metrics out of evaluator
  for line in evaluator_out.split('\n'):
    s = str(line).strip()
    if "cut" in s:
      cut = int(s.split('=')[1])
    if "km1" in s:
      km1 = int(s.split('=')[1])
    if "imbalance" in s:
      imbalance = float(s.split('=')[1])

elif parkway_proc.returncode == -signal.SIGTERM:
  timeout = "yes"
else:
  failed = "yes"

# CSV format: algorithm,graph,timeout,seed,k,epsilon,num_threads,imbalance,totalPartitionTime,objective,km1,cut,failed
print(algorithm,
      ntpath.basename(args.graph),
      timeout,
      args.seed,
      args.k,
      args.
      epsilon,
      args.threads,
      imbalance,
      total_time,
      args.objective,
      km1,
      cut,
      failed,
      sep=",")