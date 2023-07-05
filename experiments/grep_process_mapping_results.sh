experiment_dir=$1
HEAD="algorithm,graph,timeout,seed,k,epsilon,num_threads,imbalance,totalPartitionTime,totalMappingTime,totalTime,objective,km1,cut,process_mapping,approximation_factor,failed"

mkdir experimental_results
for result_folder in $experiment_dir/*_results;
do
  result_file="${result_folder/_results/.csv}"
  rm -f $result_file
  echo "$HEAD" >> $result_file
  for instance_result_file in $result_folder/*.process_mapping;
  do
    tail -1 $instance_result_file >> $result_file
  done
  mv $result_file experimental_results/
done

tar -cvf experimental_results.tar experimental_results/*
rm -rf experimental_results