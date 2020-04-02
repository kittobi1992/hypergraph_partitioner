# Install KaHyPar
cd partitioner/kahypar
git submodule init
git submodule update
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=RELEASE
make KaHyPar
make VerifyPartition
make EvaluateMondriaanPartition
cd ../../..