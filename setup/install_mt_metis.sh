# Install MT-Metis
cd partitioner

if [[ ! -d "mt-metis" ]]
then
  curl -o mt-metis.tar.gz http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/mt-metis-0.6.0.tar.gz
  tar -xvf mt-metis.tar.gz
  rm -f mt-metis.tar.gz
  mv mt-metis-0.6.0 mt-metis
fi

cd mt-metis
mkdir build
./configure --prefix=build
make -j4
cd ../..