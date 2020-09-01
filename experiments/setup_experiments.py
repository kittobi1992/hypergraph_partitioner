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
serial_partitioner = [ "hMetis-R", "hMetis-K", "PaToH-S", "PaToH-D", "PaToH-Q",
                       "KaHyPar-CA", "KaHyPar-K", "KaHyPar-R", "Mondriaan", "Hype",
                       "KaFFPa-Strong", "KaFFPa-StrongS", "KaFFPa-Strong*", "KaFFPa-StrongS*" ]
parallel_partitioner = [ "Parkway", "Zoltan", "MT-KaHyPar", "MT-KaHIP", "MT-Metis", "ParHIP" ]

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
                        "MT-KaHyPar": "mt_kahypar",
                        "MT-KaHIP": "mt_kahip",
                        "MT-Metis": "mt_metis",
                        "KaFFPa-Strong": "kaffpa_strong",
                        "KaFFPa-StrongS": "kaffpa_strongs",
                        "KaFFPa-Strong*": "kaffpa_strong_opt",
                        "KaFFPa-StrongS*": "kaffpa_strongs_opt",
                        "ParHIP": "parhip" }

format_mapping = { "hMetis-R": "hmetis_instance_folder",
                   "hMetis-K": "hmetis_instance_folder",
                   "PaToH-S": "patoh_instance_folder",
                   "PaToH-D": "patoh_instance_folder",
                   "PaToH-Q": "patoh_instance_folder",
                   "KaHyPar-CA": "hmetis_instance_folder",
                   "KaHyPar-K": "hmetis_instance_folder",
                   "KaHyPar-R": "hmetis_instance_folder",
                   "Mondriaan": "mondriaan_instance_folder",
                   "Hype": "hmetis_instance_folder",
                   "Parkway": "hmetis_instance_folder",
                   "Zoltan": "zoltan_instance_folder",
                   "MT-KaHyPar": "hmetis_instance_folder",
                   "MT-KaHIP": "graph_instance_folder",
                   "MT-Metis": "graph_instance_folder",
                   "KaFFPa-Strong": "graph_instance_folder",
                   "KaFFPa-StrongS": "graph_instance_folder",
                   "KaFFPa-Strong*": "graph_instance_folder",
                   "KaFFPa-StrongS*": "graph_instance_folder",
                   "ParHIP": "graph_instance_folder" }

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

def get_stripped_benchmark_instances(partitioner, config):
  config_instance_type = format_mapping[partitioner]
  dir = config[config_instance_type]
  return [dir + "/" + hg for hg in os.listdir(dir) if 'stripped' in hg]

def serial_partitioner_call(partitioner, instance, k, epsilon, seed, objective, timelimit):
  return partitioner_script_folder + "/" + partitioner_mapping[partitioner] + ".py " + instance + " " + str(k) + " " + str(epsilon) + " " + str(seed) + " " + str(objective) + " " + str(timelimit)

def parallel_partitioner_call(partitioner, instance, threads, k, epsilon, seed, objective, timelimit):
  return partitioner_script_folder + "/" + partitioner_mapping[partitioner] + ".py " + instance + " " + str(threads) + " " + str(k) + " " + str(epsilon) + " " + str(seed) + " " + str(objective) + " " + str(timelimit)

def partitioner_dump(result_dir, instance, threads, k, seed):
  return os.path.abspath(result_dir) + "/" + ntpath.basename(instance) + "." + str(threads) + "." + str(k) + "." + str(seed) + ".results"

def append_partitioner_calls(config, partitioner_calls, partitioner, instance, k, epsilon, result_dir, base_k):
  objective = config["objective"]
  timelimit = config["timelimit"]
  is_serial_partitioner = partitioner in serial_partitioner

  for threads in config["threads"]:
    if is_serial_partitioner and threads > 1:
      continue
    for seed in config["seeds"]:
      if is_serial_partitioner:
        partitioner_call = serial_partitioner_call(partitioner, instance, k, epsilon, seed, objective, timelimit)
      else:
        partitioner_call = parallel_partitioner_call(partitioner, instance, threads, k, epsilon, seed, objective, timelimit)
      partitioner_call = partitioner_call + " >> " + partitioner_dump(result_dir, instance, threads, base_k, seed)
      partitioner_calls.extend([partitioner_call])

def select_instance(partitioner, hg_name, k, separate, all_instances):
  candidates = [instance for instance in all_instances if (hg_name in instance) and (not separate or "k_{}".format(k) in instance)]
  if len(candidates) != 1:
    raise Exception('No unique instance found for {}, k={}: {}\nCandidates found: {}'.format(partitioner, k, hg_name, candidates))
  return candidates[0]

def append_calls_from_metadata(config, data, partitioner_calls, partitioner, result_dir):
  all_instances = get_stripped_benchmark_instances(partitioner, config)
  separate = bool(data["separate"])

  for hg_name, values in data["instances"].items():
    for k in config["k"]:
      instance_data = values[str(k)]
      instance = select_instance(partitioner, hg_name, k, separate, all_instances)
      append_partitioner_calls(config, partitioner_calls, partitioner, instance, instance_data["k"], instance_data["epsilon"], result_dir, k)


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
    has_metadata = False
    if "metadata" in config:
       has_metadata = True
       with open(config["metadata"]) as metadata:
          data = json.load(metadata)

    # Setup experiments
    for partitioner in config["partitioner"]:
      result_dir = experiment_dir + "/" + partitioner_mapping[partitioner] + "_results"
      os.makedirs(result_dir, exist_ok=True)
      partitioner_calls = []
      if not has_metadata:
        # Usual case
        for instance in get_all_benchmark_instances(partitioner, config):
          for k in config["k"]:
            append_partitioner_calls(config, partitioner_calls, partitioner, instance, k, epsilon, result_dir, k)
      else:
        # Case with node weights
        append_calls_from_metadata(config, data, partitioner_calls, partitioner, result_dir)

      # Write partitioner calls to workload file
      with open(experiment_dir + "/" + partitioner_mapping[partitioner] + "_workload.txt", "w") as partitioner_workload_file:
        partitioner_workload_file.write("\n".join(partitioner_calls))
        partitioner_workload_file.write("\n")

      with open(workload_file, "a") as global_workload_file:
        global_workload_file.write("\n".join(partitioner_calls))
        global_workload_file.write("\n")


