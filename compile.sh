cd pymmWave
cp -R src/mmWave/. build/lib/mmWave/ 
cd src
stubgen mmWave
cd ..
python setup.py bdist_wheel
cd ..