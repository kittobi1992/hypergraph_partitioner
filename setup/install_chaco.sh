# Install hMetis
cd partitioner

if [[ ! -d "chaco" ]]
then
  curl -o chaco.tar.gz https://www3.cs.stonybrook.edu/~algorith/implement/chaco/distrib/Chaco-2.2.tar.gz
  tar -xvf chaco.tar.gz
  rm -f chaco.tar.gz
  mv Chaco-2.2 chaco
  cd chaco/code
  make
  cd ../..
fi

cd ..