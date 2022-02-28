# Install hMetis
cd partitioner

if [[ ! -d "parmetis" ]]
then
  curl -o parmetis.tar.gz http://glaros.dtc.umn.edu/gkhome/fetch/sw/parmetis/parmetis-4.0.3.tar.gz
  tar -xvf parmetis.tar.gz
  rm -f parmetis.tar.gz
  mv parmetis-4.0.3 parmetis
  cp parmetis.c parmetis/programs/parmetis.c
  cd parmetis
  make config prefix=app
  make -j8
  make install -j8
  cd ..
fi


cd ..