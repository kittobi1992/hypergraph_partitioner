# Install MT-Metis
cd partitioner

if [[ ! -d "mt-metis" ]]
then
  curl -o mt-metis.tar.gz https://dlasalle.github.io/mt-metis/releases/mt-metis-0.7.2.tar.gz
  tar -xvf mt-metis.tar.gz
  rm -f mt-metis.tar.gz
  mv mt-metis-0.7.2 mt-metis
fi

cd mt-metis
mkdir build
./configure --prefix=build
make -j4
cd ../..

