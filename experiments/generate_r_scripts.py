#!/usr/bin/python3
import json
import argparse
import datetime
import os
import os.path
import ntpath
import glob
import csv
import re
import shutil

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
                        "MT-KaHyPar-D-F": "mt_kahypar_d_f",
                        "MT-KaHyPar-Q-F": "mt_kahypar_q_f",
                        "MT-KaHIP": "mt_kahip",
                        "MT-Metis": "mt_metis",
                        "Metis-R": "metis_rb",
                        "Metis-K": "metis_k",
                        "KaFFPa-Strong": "kaffpa_strong",
                        "KaFFPa-StrongS": "kaffpa_strongsocial",
                        "ParHIP": "parhip" }

parser = argparse.ArgumentParser()
parser.add_argument("experiment", type=str)

args = parser.parse_args()

repo_dir = os.environ.get("HOME") + "/hypergraph_partitioner"
plot_dir = repo_dir + "/plots"

def write_header(file):
  file.write('setwd("' + plot_dir + '")\n')
  file.write('source("functions.R")\n')
  file.write('\n')

def load_csv_files(file, config, csv_files, db_names, experiment_dir):
  for csv_file in csv_files:
    csv_filename = experiment_dir + "/" + csv_file + ".csv"
    file.write(db_names[csv_file] + ' <- aggreg_data(read.csv("' + csv_filename + '", header = TRUE), timelimit = ' + str(config['timelimit']) + ', epsilon = ' + str(config['epsilon']) + ')\n')
  file.write("\n")

def write_color_mapping(file, algo_names):
  file.write('palette <- brewer.pal(n = 9, name = "Set1")\n')
  file.write('algo_color_mapping <- c(')
  nums = list(range(1, len(algo_names) + 1))
  color_mapping = list(map(lambda name, i: '"' + name + '" <- palette[[' + str(i) + "]]", algo_names, nums))
  file.write(",".join(color_mapping))
  file.write(')\n\n')

def write_running_time_boxplot(file, csv_files, algo_names, db_names):
  file.write('############# Running Time Box Plot ##############\n\n')
  file.write('order <- c(' + ",".join(list(map(lambda x: '"' + x + '"', algo_names))) +  ')\n')
  file.write('print(running_time_box_plot(list(' +
    ",".join(list(map(lambda x: db_names[x], csv_files))) + '), order = order))\n')
  file.write("\n")

def write_performance_profile_plot(file, csv_files, db_names):
  file.write('############# Performance Profile Plot ##############\n\n')
  file.write('print(performace_plot(list(' +
    ",\n".join(list(map(lambda x: db_names[x], csv_files))) + '\n)))\n')
  file.write("\n")

with open(args.experiment) as json_experiment:
    config = json.load(json_experiment)
    now = datetime.datetime.now()
    reference_dir = "reference_csv"
    experiment_dir = os.path.abspath(str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "_" + config["name"])
    r_filename = experiment_dir + "/results.R"
    if os.path.exists(r_filename):
      os.remove(r_filename)

    for file in glob.glob(reference_dir + "/*.csv"):
      shutil.copy(file, experiment_dir)

    csv_files = list(map(lambda x: os.path.splitext(os.path.basename(x))[0], glob.glob(experiment_dir + "/*.csv")))
    algo_names = []
    db_names = dict()
    for csv_file in csv_files:
      csv_filename = experiment_dir + "/" + csv_file + ".csv"
      with open(csv_filename) as file:
        data = csv.reader(file, delimiter = ",")
        next(data, None)
        algo_name = next(data, None)[0]
        algo_names = algo_names + [ algo_name ]
        db_names[csv_file] = '_'.join(list(map(lambda x: x.lower(), re.split(' |-', algo_name))))

    with open(r_filename, "a") as r_file:
      write_header(r_file)
      load_csv_files(r_file, config, csv_files, db_names, experiment_dir)
      write_color_mapping(r_file, algo_names)
      write_running_time_boxplot(r_file, csv_files, algo_names, db_names)
      write_performance_profile_plot(r_file, csv_files, db_names)



