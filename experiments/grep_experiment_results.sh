experiment_dir=$1
HEAD="algorithm,graph,timeout,seed,k,epsilon,num_threads,imbalance,totalPartitionTime,objective,km1,cut,failed,preprocessing,coarsening,initial_partitioning,refinement,jet,rebalance_jet,lp,fm,collect_border_nodes,find_moves,rollback,ufm_setup,rebalance_fm,rebalance_total"

mkdir experimental_results
for result_folder in $experiment_dir/*_results;
do
  result_file="${result_folder/_results/.csv}"
  rm -f $result_file
  echo "$HEAD" >> $result_file
  for instance_result_file in $result_folder/*.results;
  do
    tail -1 $instance_result_file >> $result_file
  done
  mv $result_file experimental_results/
done

tar -cvf experimental_results.tar experimental_results/*
rm -rf experimental_results