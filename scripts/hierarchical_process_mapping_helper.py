#!/usr/bin/python3
import os
import os.path
import ntpath
import subprocess
import functools

generator = os.environ.get("HIERARCHICHAL_PROCESS_GRAPH_GENERATOR")
verify_partition = os.environ.get("VERIFY_PROCESS_GRAPH_PARTITION")
assert (generator != None), "check env.sh"
assert (verify_partition != None), "check env.sh"

def generate_hierarchical_process_graph(out_folder, filename_prefix, hierarchy_parameter_string, distance_parameter_string):
  generator_command = [generator,
                       "--out-folder=" + out_folder,
                       "--hierarchy=" + hierarchy_parameter_string,
                       "--communication-costs=" + distance_parameter_string,
                       "--filename-prefix=" + filename_prefix]
  generator_proc = subprocess.Popen(generator_command,
                                    stdout=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid)
  out, err = generator_proc.communicate()

  if generator_proc.returncode == 0:
    graph_file = ""
    for line in out.split('\n'):
      s = str(line).strip()
      if "Graph has been written to" in s:
        graph_file = s.split("'")[1]
    return graph_file
  else:
    return ""

def get_number_of_blocks(hierarchy_parameter_string):
  return functools.reduce(lambda a,b: a * b, map(lambda x: int(x), hierarchy_parameter_string.split(":")))

def get_process_graph_file_prefix(graph, algorithm, k, epsilon, seed):
  return graph + ".part" + str(k) + ".eps" + str(epsilon) + ".seed" + str(seed) + "." + algorithm + "."

def verify_process_mapping_partition(graph_file, partition_file, file_format,
                                     hierarchy_parameter_string, distance_parameter_string,
                                     algorithm, k, epsilon, seed):
  instance_dir = ntpath.dirname(graph_file)
  instance_name = ntpath.basename(graph_file)
  process_graph_prefix = get_process_graph_file_prefix(instance_name, algorithm, k, epsilon, seed)
  process_graph_file = generate_hierarchical_process_graph(instance_dir, process_graph_prefix,
                                                           hierarchy_parameter_string, distance_parameter_string)

  verify_command = [verify_partition,
                    "-h" + graph_file,
                    "-b" + partition_file,
                    "-p" + process_graph_file,
                    "--input-file-format=" + file_format,
                    "-v0"]

  verify_proc = subprocess.Popen(verify_command,
                                    stdout=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid)
  out, err = verify_proc.communicate()

  if os.path.exists(process_graph_file):
    os.remove(process_graph_file)

  if verify_proc.returncode == 0:
    for line in out.split('\n'):
      s = str(line).strip()
      if "RESULT" in s:
        process_mapping = int(s.split(" process_mapping=")[1].split(" ")[0])
        return process_mapping
  return 0