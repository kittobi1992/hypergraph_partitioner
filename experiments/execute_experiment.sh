experiment_file=$1

./setup_experiments.py $1
./execute_experiments.py $1
./generate_r_scripts.py $1