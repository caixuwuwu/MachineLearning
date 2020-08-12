from setuptools import setup

with open('README.md') as f:
  long_description = f.read()

setup(
  name='machinelearningonspark',
  packages=['machinelearningonspark'],
  version='0.0.1',
  description='Machine learning on Apache Spark clusters',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Xuwu Cai',
  url='https://github.com/caixuwuwu/MachineLearning',
  keywords=['machinelearningonspark', 'tensorflow', 'spark', 'machine learning', 'xgboost', 'lightgbm'],
  install_requires=['packaging'],
  license='Apache 2.0',
  classifiers=[
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: Apache Software License',
    'Topic :: Software Development :: Libraries',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
  ]
)
