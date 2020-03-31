# Install Parkway
cd partitioner/parkway
./configure -DCMAKE_BUILD_TYPE=RELEASE
make -j4

# Install KaHyPar
cd ..
cd kahypar
git submodule init
git submodule update
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=RELEASE
make KaHyPar
make VerifyPartition

# Install MT-KaHIP
cd ../..
cd KaHIP
git checkout add_parallel_local_search
git submodule init
git submodule update
scons program=kaffpa variant=optimized -j 4