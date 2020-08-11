#!/usr/bin/python3
import json
import argparse
import os
import os.path
import re
import subprocess

remove_heavy_nodes_tool = os.environ.get("REMOVE_HEAVY_NODES")
calculate_epsilon_tool = os.environ.get("CALCULATE_EPSILON")
assert (remove_heavy_nodes_tool != None and calculate_epsilon_tool != None), "check env.sh"

strip_hgr = re.compile('([^\s]*)\.hgr')
get_k = re.compile('k=\s*([^\s]*)')
get_epsilon = re.compile('epsilon=\s*([^\s]*)')

def get_all_hypergraph_instances(dir):
    return [dir + "/" + hg for hg in os.listdir(dir) if hg.endswith('.hgr')]

def remove_nodes(in_file, out_file, k):
    # Run tool for removing heavy nodes
    remove_nodes_proc = subprocess.Popen([remove_heavy_nodes_tool,
        str(in_file), str(out_file), str(k)],
        stdout=subprocess.PIPE, universal_newlines=True)
    out, err = remove_nodes_proc.communicate()

    if remove_nodes_proc.returncode == 0:
        for line in out.split('\n'):
            s = str(line).strip()
            if ("k=" in s):
                new_k = int(str(get_k.findall(s)[0]))
                return new_k
    raise Exception('Could not calculate value for k: {}'.format(in_file))

def calculate_epsilon(instance, k, epsilon):
    # Run tool to calculate epsilon
    epsilon_proc = subprocess.Popen([calculate_epsilon_tool,
        str(instance), str(k), str(epsilon)],
        stdout=subprocess.PIPE, universal_newlines=True)
    out, err = epsilon_proc.communicate()

    if epsilon_proc.returncode == 0:
        for line in out.split('\n'):
            s = str(line).strip()
            if ("epsilon" in s):
                new_epsilon = float(str(get_epsilon.findall(s)[0]))
                return new_epsilon
    raise Exception('Could not calculate value for epsilon: {}'.format(instance))

def calculate_metadata(data, instance, ks, epsilon):
    path, file_name = os.path.split(instance)
    hg_name = str(strip_hgr.findall(file_name)[0])
    print("Processing hypergraph: {} ...".format(hg_name))

    instance_data = {}
    for k in ks:
        out_file = instance + ".stripped.k_{}".format(k)
        new_k = int(remove_nodes(instance, out_file, k))
        new_epsilon = float(calculate_epsilon(out_file, k, epsilon))
        instance_data[str(k)] = {
            'k' : new_k,
            'epsilon' : new_epsilon,
        }
    data[hg_name] = instance_data

parser = argparse.ArgumentParser()
parser.add_argument("experiment", type=str)
parser.add_argument("output_file", nargs='?', type=str, default="metadata.json")

args = parser.parse_args()

with open(args.experiment) as json_experiment:
    config = json.load(json_experiment)
    instance_dir = config["hmetis_instance_folder"]
    epsilon = config["epsilon"]
    ks = config["k"]
    data = {
        'separate' : True,
        'instances' : {}
    }

    for instance in get_all_hypergraph_instances(instance_dir):
        calculate_metadata(data['instances'], instance, ks, epsilon)
    with open(args.output_file, 'w', encoding='utf-8') as metadata_file:
        json.dump(data, metadata_file, ensure_ascii=False, indent=4)
    print("... results written to {}".format(args.output_file))
    print("")
    print("Attention: The created instances need to be converted to different partitioner formats!")

