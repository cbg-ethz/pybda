from sys import version_info
from setuptools import setup, find_packages

if version_info[0] == 2:
    exit("Sorry, Python 2 is not supported. Move to Python 3 already.")


def readme():
    with open('README.rst') as fl:
        return fl.read()


test_deps = [
    'coverage',
    'findspark',
    'flake8',
    'pylint',
    'pytest>=3.6.2',
    'pytest-cov',
    'pytest-pep8',
    'scikit-learn',
    'yapf'
]

doc_deps = [
    'sphinx',
    'sphinx_fontawesome',
    'sphinxcontrib-fulltoc'
]

setup(
  name='pybda',
  version='0.1.0',
  description='Analysis of big biological data sets for distributed HPC clusters.',
  long_description=readme(),
  url='https://github.com/cbg-ethz/pybda',
  author='Simon Dirmeier',
  author_email='simon.dirmeier@web.de',
  license='GPLv3',
  keywords='bigdata analysis pipeline workflow spark pyspark machinelearning',
  packages=find_packages(),
  scripts=['scripts/pybda'],
  include_package_data=True,
  python_requires='>=3',
  install_requires=[
      'click>=6.7',
      'joypy>=0.1.9',
      'matplotlib>=2.2.3',
      'numpy>=1.15.0',
      'pandas>=0.23.3',
      'pyspark==2.4.0',
      'scipy>=1.0.0',
      'seaborn>=0.9.0',
      'snakemake>=5.2.2',
      'sparkhpc>=0.3.post4'
  ],
  test_requires=test_deps,
  extras_require={
      'test': test_deps,
      'doc': doc_deps,
      'dev': test_deps + doc_deps
  },
  classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Intended Audience :: End Users/Desktop',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5',
      'Programming Language :: Python :: 3.6'
  ]
)
