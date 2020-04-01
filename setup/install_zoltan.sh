# Install Zoltan
cd partitioner/zoltan
mkdir build
cd build
../configure --prefix=$PWD --with-gnumake --with-mpi-compiler=yes --enable-mpi --with-PACKAGE=yes
make everything -j4
make install
cd ../../..