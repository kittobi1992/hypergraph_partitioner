# Install MT-KaHIP
cd partitioner/mt-kahip
git checkout add_parallel_local_search
git submodule init
git submodule update
patch growt/data-structures/seqcircular.h < ../growt.patch
patch SConscript < ../mt_kahip.patch
scons program=kaffpa variant=optimized -j 4
cd ../..