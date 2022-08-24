pip install -r requirements-dev.txt
mutatest -s caronte/src -y 'if' 'nc' 'ix' 'su' 'bs' 'bc' 'bn' -x 60 -n 1000 -t 'pytest'