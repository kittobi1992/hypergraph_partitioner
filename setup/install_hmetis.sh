# Install hMetis
cd partitioner

if [[ ! -d "hmetis" ]]
then
  curl -o hmetis.tar.gz http://glaros.dtc.umn.edu/gkhome/fetch/sw/hmetis/hmetis-2.0pre1.tar.gz
  tar -xvf hmetis.tar.gz
  rm -f hmetis.tar.gz
  mv hmetis-2.0pre1/Linux-x86_64/hmetis2.0pre1 hmetis-2.0pre1/hmetis
  rm -rf hmetis-2.0pre1/Linux-x86_64
  rm -rf hmetis-2.0pre1/Linux-i686
  mv hmetis-2.0pre1 hmetis
fi

cd ..