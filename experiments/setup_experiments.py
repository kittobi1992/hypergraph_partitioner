#!/usr/bin/python3
import json
import argparse
import datetime
import os
import os.path
import ntpath

def intersection(lst1, lst2):
  lst3 = [value for value in lst1 if value in lst2]
  return lst3

partitioner_script_folder = os.environ.get("PARTITIONER_SCRIPT_FOLDER")
serial_partitioner = [ "hMetis-R", "hMetis-K", "PaToH-S", "PaToH-D", "PaToH-Q", "Mondriaan" ]
parallel_partitioner = [ "Parkway", "Zoltan", "MT-KaHIP", "MT-Metis" ]

partitioner_mapping = { "hMetis-R": "hmetis_rb",
                        "hMetis-K": "hmetis_k",
                        "PaToH-S": "patoh_s",
                        "PaToH-D": "patoh_d",
                        "PaToH-Q": "patoh_q",
                        "Mondriaan": "mondriaan",
                        "Parkway": "parkway",
                        "Zoltan": "zoltan",
                        "MT-KaHIP": "mt_kahip",
                        "MT-Metis": "mt_metis" }

format_mapping = { "hMetis-R": "hmetis_instance_folder",
                   "hMetis-K": "hmetis_instance_folder",
                   "PaToH-S": "patoh_instance_folder",
                   "PaToH-D": "patoh_instance_folder",
                   "PaToH-Q": "patoh_instance_folder",
                   "Mondriaan": "hmetis_instance_folder",
                   "Parkway": "hmetis_instance_folder",
                   "Zoltan": "zoltan_instance_folder",
                   "MT-KaHIP": "graph_instance_folder",
                   "MT-Metis": "graph_instance_folder" }

def get_all_hypergraph_instances(dir):
  return [dir + "/" + hg for hg in os.listdir(dir) if hg.endswith('.hgr')]

def get_all_mondriaan_instances(dir):
  return [dir + "/" + mondriaan_hg for mondriaan_hg in os.listdir(dir) if mondriaan_hg.endswith('.mondriaan.mtx')]

def get_all_zoltan_instances(dir):
  return [dir + "/" + zoltan_hg for zoltan_hg in os.listdir(dir) if zoltan_hg.endswith('.zoltan.hg')]

def get_all_graph_instances(dir):
  return [dir + "/" + graph for graph in os.listdir(dir) if graph.endswith('.graph')]

def get_all_benchmark_instances(partitioner, config):
  config_instance_type = format_mapping[partitioner]
  instance_dir = config[config_instance_type]
  if partitioner == "Mondriaan":
    return get_all_mondriaan_instances(instance_dir)
  elif config_instance_type == "hmetis_instance_folder" or config_instance_type == "patoh_instance_folder":
    return get_all_hypergraph_instances(instance_dir)
  elif config_instance_type == "zoltan_instance_folder":
    return get_all_zoltan_instances(instance_dir)
  elif config_instance_type == "graph_instance_folder":
    return get_all_graph_instances(instance_dir)

def serial_partitioner_call(partitioner, instance, k, epsilon, seed, objective, timelimit):
  return partitioner_script_folder + "/" + partitioner_mapping[partitioner] + ".py " + instance + " " + str(k) + " " + str(epsilon) + " " + str(seed) + " " + str(objective) + " " + str(timelimit)

def parallel_partitioner_call(partitioner, instance, threads, k, epsilon, seed, objective, timelimit):
  return partitioner_script_folder + "/" + partitioner_mapping[partitioner] + ".py " + instance + " " + str(threads) + " " + str(k) + " " + str(epsilon) + " " + str(seed) + " " + str(objective) + " " + str(timelimit)

def partitioner_dump(result_dir, instance, threads, k, seed):
  return os.path.abspath(result_dir) + "/" + ntpath.basename(instance) + "." + str(threads) + "." + str(k) + "." + str(seed) + ".results"

parser = argparse.ArgumentParser()
parser.add_argument("experiment", type=str)

args = parser.parse_args()

with open(args.experiment) as json_experiment:
    config = json.load(json_experiment)

    now = datetime.datetime.now()
    experiment_dir = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "_" + config["name"]
    workload_file = experiment_dir + "/workload.txt"
    os.makedirs(experiment_dir, exist_ok=True)
    if os.path.exists(workload_file):
      os.remove(workload_file)

    epsilon = config["epsilon"]
    objective = config["objective"]
    timelimit = config["timelimit"]

    # Setup experiments
    for partitioner in config["partitioner"]:
      result_dir = experiment_dir + "/" + partitioner_mapping[partitioner] + "_results"
      os.makedirs(result_dir, exist_ok=True)
      partitioner_calls = []
      is_serial_partitioner = partitioner in serial_partitioner
      for instance in get_all_benchmark_instances(partitioner, config):
        for threads in config["threads"]:
          if is_serial_partitioner and threads > 1:
            continue
          for k in config["k"]:
            for seed in config["seeds"]:
              if is_serial_partitioner:
                partitioner_call = serial_partitioner_call(partitioner, instance, k, epsilon, seed, objective, timelimit)
              else:
                partitioner_call = parallel_partitioner_call(partitioner, instance, threads, k, epsilon, seed, objective, timelimit)
              partitioner_call = partitioner_call + " >> " + partitioner_dump(result_dir, instance, threads, k, seed)
              partitioner_calls.extend([partitioner_call])

      # Write partitioner calls to workload file
      with open(experiment_dir + "/" + partitioner_mapping[partitioner] + "_workload.txt", "w") as partitioner_workload_file:
        partitioner_workload_file.write("\n".join(partitioner_calls))
        partitioner_workload_file.write("\n")

      with open(workload_file, "a") as global_workload_file:
        global_workload_file.write("\n".join(partitioner_calls))
        global_workload_file.write("\n")


