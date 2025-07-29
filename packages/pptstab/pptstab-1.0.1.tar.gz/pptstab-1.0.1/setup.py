# setup.py
from setuptools import setup, find_packages
from setuptools import setup, Extension
from setuptools import  find_namespace_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
    name='pptstab',
    version='1.0.1',
    description='PPTStab: Designing of thermostable proteins with a desired melting temperature',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license_files = ('LICENSE.txt',),
    author='G.P.S. Raghava',
    author_email='raghava@iiitd.ac.in',
    url='https://github.com/raghavalab/pptstab',
    packages=find_namespace_packages(where="src"),
    package_dir={'':'src'},
    package_data={'pptstab.models':['**/*']},
    entry_points={'console_scripts' : ['pptstab = pptstab.python_script.pptstab:main']},
    include_package_data=True,
    python_requires='>=3.6',
    install_requires= [ 'numpy', 'pandas', 'joblib','tqdm' ,'torch', 'onnxruntime', 'tensorflow', 'scikit-learn','transformers']
)

