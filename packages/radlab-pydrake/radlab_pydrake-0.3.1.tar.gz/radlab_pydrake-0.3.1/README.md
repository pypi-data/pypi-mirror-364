Ok how to update package: 

rm -rf dist 
* CHANGE THE VERSION in setup.py 

python -m build 

pip install -e . 

 

THEN pip install radlab_pydrake --target=install/simulator/lib/python3.12/site-packages 

When trying to use RADLAB roboball simulation 

 

 