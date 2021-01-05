# install BiPart
cd partitioner/bipart
git submodule init
git submodule update
mkdir build

if [[ ! -d "fmt" ]]
then
  git clone https://github.com/fmtlib/fmt.git
  cd fmt
  cmake CMakeLists.txt
  make -j8
fi

cmake -S $PWD -B $PWD/build -Dfmt_DIR=$PWD/fmt/build/ -DCMAKE_BUILD_TYPE=Release
cd build/lonestar/analytics/cpu/bipart/
make -j8

cd ../../../../../../../