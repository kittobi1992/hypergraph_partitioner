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

# Install MT-Metis
cd ..
cd mt-metis
mkdir build
./configure --prefix=build
make -j4

# Install Zoltan
cd ../zoltan
mkdir build
cd build
../configure --prefix=$PWD --with-gnumake --with-mpi-compiler=yes --enable-mpi --with-PACKAGE=yes
make everything -j4
make install

# Download PaToH
# curl -o patoh.tar.gz https://www.cc.gatech.edu/~umit/PaToH/patoh-Linux-x86_64.tar.gz
# tar -zxvf patoh.tar.gz
# mv build/Linux-x86_64/patoh.h build/Linux-x86_64/libpatoh.a partitioner/PaToHWrapper/extern/
# rm patoh.tar.gz
# rm -rf build/
# cd partitioner/PaToHWrapper
# mkdir release && cd release && cmake .. -DCMAKE_BUILD_TYPE=Release
# make PaToH
# cd ../../../
