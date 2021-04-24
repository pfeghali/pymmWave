cd pymmWave_pkg
cp -R src/pymmWave/. build/lib/pymmWave/ 
cd src
stubgen pymmWave
cd ..
python setup.py bdist_wheel
cd ..