# Install MT-KaHIP
cd partitioner/KaHIP
git checkout add_parallel_local_search
git submodule init
git submodule update
scons program=kaffpa variant=optimized -j 4
cd ../..