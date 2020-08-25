# Install KaHyPar

cd partitioner/kahypar
git submodule init
git submodule update

mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=RELEASE -DKAHYPAR_USE_MINIMAL_BOOST=ON
make mini_boost -j4
make KaHyPar
make VerifyPartition
make EvaluateMondriaanPartition
make RemoveHeavyNodes
make CalculateRelaxedEpsilon
cd ../../..
