from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='screenpy',
    version='0.0.1',
    description='Analysis of big data perturbation screens.',
    long_description=readme(),
    url='https://github.com/dirmeier/screenpy',
    download_url='https://github.com/dirmeier/screenpy/tarball/0.0.1',
    author='Simon Dirmeier',
    author_email='simon.dirmeier@bsse.ethz.ch',
    license='GPLv3',
    keywords=['?'],
    packages=['screenpy'],
    install_requires=[
         'numpy>=1.11.0',
         'scipy>=0.18.0',
         'pytest>=2.9.2',
         'nose==1.3.7',
         'sphinx>=1.4.5',
         'scikit-learn >=0.17.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
