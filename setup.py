from setuptools import setup, find_packages
from sys import version_info, exit

if version_info[0] == 2:
    exit("Sorry, Python 2 is not supported. Move to Python 3 already.")


def readme():
    with open('README.rst') as fl:
        return fl.read()


setup(
  name='pybda',
  version='0.0.3',
  description='Big Data analytics powered by Apache Spark',
  long_description=readme(),
  url='https://github.com/cbg-ethz/koios',
  author='Simon Dirmeier',
  author_email='simon.dirmeier@bsse.ethz.de',
  license='GPLv3',
  keywords='bigdata analysis pipeline workflow spark pyspark machinelearning',
  packages=find_packages(),
  scripts=['scripts/pybda'],
  include_package_data=True,
  python_requires='>=3',
  install_requires=[
      'pyspark>=2.3.0',
      'numpy>=1.15.0',
      'scipy>=1.0.0',
      'pandas>=0.23.3',
      'click>=6.7',
      'pytest>=3.6.2',
      'matplotlib>=2.2.3',
      'snakemake>=5.2.2',
      'joypy>=0.1.9',
      'uuid>=1.3.0',
      'sparkhpc>=0.3.post4',
      'seaborn>=0.9.0'
  ],
  classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Intended Audience :: End Users/Desktop',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7'
  ]
)
