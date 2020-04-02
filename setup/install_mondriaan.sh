# Install Mondriaan
cd partitioner

if [[ ! -d "mondriaan" ]]
then
  curl -o mondriaan.tar.gz http://www.staff.science.uu.nl/~bisse101/Mondriaan/mondriaan_v4.2.1.tar.gz
  tar -xvf mondriaan.tar.gz
  rm -f mondriaan.tar.gz
  mv mondriaan-master mondriaan
  cd mondriaan
  patch tools/Mondriaan.c < ../mondriaan.patch
  make
fi

cd ../..