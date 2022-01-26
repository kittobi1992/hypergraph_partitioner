# Install hMetis
cd partitioner

if [[ ! -d "metis" ]]
then
  curl -o metis.tar.gz http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz
  tar -xvf metis.tar.gz
  rm -f metis.tar.gz
  mv metis-5.1.0 metis
  cd metis
  make config
  make
  cd ..
fi

cd ..