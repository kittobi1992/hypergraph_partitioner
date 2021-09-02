#!/usr/bin/python3
import json
import argparse
import datetime
import os
import os.path
import ntpath

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

parser = argparse.ArgumentParser()
parser.add_argument("experiment", type=str)

args = parser.parse_args()

repo_dir = os.environ.get("HOME") + "/hypergraph_partitioner"
plot_dir = repo_dir + "/plots"

def write_header(file):
  file.write('setwd("' + plot_dir + '")\n')
  file.write('source("functions.R")\n')
  file.write('\n')

def load_csv_files(file, config, experiment_dir):
  for partitioner in config['partitioner']:
    partitioner_name = partitioner_mapping[partitioner]
    csv_file = experiment_dir + "/" + partitioner_name + ".csv"
    file.write(partitioner_name + ' <- aggreg_data(read.csv("' + csv_file + '", header = TRUE), timelimit = ' + str(config['timelimit']) + ', epsilon = ' + str(config['epsilon']) + ')\n')
  file.write("\n")

def write_algo_names(file, config):
  for partitioner in config['partitioner']:
    partitioner_name = partitioner_mapping[partitioner]
    file.write(partitioner_name + '$algorithm <- "' + partitioner + '"\n')
  file.write("\n")

def write_color_mapping(file, config):
  file.write('palette <- brewer.pal(n = 9, name = "Set1")\n')
  file.write('algo_color_mapping <- c(')
  nums = list(range(1, len(config['partitioner']) + 1))
  color_mapping = list(map(lambda name, i: '"' + name + '" <- palette[[' + str(i) + "]]", config['partitioner'], nums))
  file.write(",".join(color_mapping))
  file.write(')\n\n')

def write_running_time_boxplot(file, config):
  file.write('############# Running Time Box Plot ##############\n\n')
  file.write('order <- c(' + ",".join(list(map(lambda x: '"' + x + '"', config["partitioner"]))) +  ')\n')
  file.write('print(running_time_box_plot(list(' +
    ",".join(list(map(lambda x: partitioner_mapping[x], config["partitioner"]))) + '), order = order))\n')
  file.write("\n")

def write_performance_profile_plot(file, config):
  file.write('############# Performance Profile Plot ##############\n\n')
  file.write('print(performace_plot(list(' +
    ",".join(list(map(lambda x: partitioner_mapping[x], config["partitioner"]))) + ')))\n')
  file.write("\n")

with open(args.experiment) as json_experiment:
    config = json.load(json_experiment)
    now = datetime.datetime.now()
    experiment_dir = os.path.abspath(str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "_" + config["name"])
    r_filename = experiment_dir + "/results.R"
    if os.path.exists(r_filename):
      os.remove(r_filename)

    with open(r_filename, "a") as r_file:
      write_header(r_file)
      load_csv_files(r_file, config, experiment_dir)
      write_algo_names(r_file, config)
      write_color_mapping(r_file, config)
      write_running_time_boxplot(r_file, config)
      write_performance_profile_plot(r_file, config)



