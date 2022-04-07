# Install hMetis
cd partitioner

if [[ ! -d "scotch" ]]
then
  curl -o scotch.tar.gz https://gitlab.inria.fr/scotch/scotch/-/archive/v6.1.3/scotch-v6.1.3.tar.gz
  tar -xvf scotch.tar.gz
  rm -f scotch.tar.gz
  mv scotch-v6.1.3 scotch
  cd scotch/src
  cp Make.inc/Makefile.inc.x86-64_pc_linux2 Makefile.inc
  make -j8
  cp ../../pt_scotch_makefile.inc Makefile.inc
  make ptscotch -j8
  cp Make.inc/Makefile.inc.x86-64_pc_linux2 Makefile.inc
  cd ../..
fi

cd ..