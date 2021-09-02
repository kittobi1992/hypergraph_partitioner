#!/usr/bin/python3
import json
import argparse
import datetime
import os
import os.path
import ntpath
import subprocess

partitioner_mapping = { "hMetis-R": "hmetis_rb",
                        "hMetis-K": "hmetis_k",
                        "PaToH-S": "patoh_s",
                        "PaToH-D": "patoh_d",
                        "PaToH-Q": "patoh_q",
                        "KaHyPar-CA": "kahypar_ca",
                        "KaHyPar-K": "kahypar_k",
                        "KaHyPar-R": "kahypar_r",
                        "Mondriaan": "mondriaan",
                        "Hype": "hype",
                        "Parkway": "parkway",
                        "Zoltan": "zoltan",
                        "BiPart": "bipart",
                        "MT-KaHyPar": "mt_kahypar",
                        "MT-KaHyPar-D": "mt_kahypar_d",
                        "MT-KaHyPar-Q": "mt_kahypar_q",
                        "MT-KaHIP": "mt_kahip",
                        "MT-Metis": "mt_metis",
                        "KaFFPa-Strong": "kaffpa_strong",
                        "KaFFPa-StrongS": "kaffpa_strongs",
                        "KaFFPa-Strong*": "kaffpa_strong_opt",
                        "KaFFPa-StrongS*": "kaffpa_strongs_opt",
                        "ParHIP": "parhip" }

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = "\033[1;92m" + fill * filledLength + "\033[0m" + ' ' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix} ({iteration}/{total})', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

parser = argparse.ArgumentParser()
parser.add_argument("experiment", type=str)

args = parser.parse_args()

with open(args.experiment) as json_experiment:
    config = json.load(json_experiment)

    now = datetime.datetime.now()
    experiment_dir = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "_" + config["name"]
    workload_file = experiment_dir + "/workload.txt"
    num_lines = sum(1 for line in open(workload_file))

    with open(workload_file) as workload:
      lines = workload.readlines()
      lines = [line.rstrip() for line in lines]
      i = 0
      for partitioner_call in lines:
        printProgressBar(i, num_lines, prefix = "Progress:", suffix = "Completed")
        os.system(partitioner_call)
        i = i + 1
      printProgressBar(num_lines, num_lines, prefix = "Progress:", suffix = "Completed")

    for partitioner in config['partitioner']:
      partitioner_name = partitioner_mapping[partitioner]
      result_file = experiment_dir + "/" + partitioner_name + ".csv"
      if os.path.exists(result_file):
        os.remove(result_file)
      os.system("echo 'algorithm,graph,timeout,seed,k,epsilon,num_threads,imbalance,totalPartitionTime,objective,km1,cut,failed' >> " + result_file)
      os.system("cat " + experiment_dir + "/" + partitioner_name + "_results/* >> " + result_file)


