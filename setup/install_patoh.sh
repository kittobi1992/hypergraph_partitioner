# Install PaToH
cd partitioner

if [[ ! -d "patoh" ]]
then
  curl -o patoh.tar.gz https://www.cc.gatech.edu/~umit/PaToH/patoh-Linux-x86_64.tar.gz
  tar -xvf patoh.tar.gz
  rm -f patoh.tar.gz
  mv build patoh
  mv patoh/Linux-x86_64/* patoh/
  rm -rf patoh/Linux-x86_64
fi

cd ..