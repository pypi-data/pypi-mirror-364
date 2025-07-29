from setuptools import setup, find_packages

find_packages(where='src')

setup(
  name='wdsdk',
  version='0.0.1',
  description='A Python client library for using Workday Reports-as-a-Service APIs.',
  author='lessej',
  url='https://github.com/lessej/workday-raas-python',
  packages=['wdsdk'],
  package_dir={ 'wdsdk': 'src/wdsdk' },
  install_requires=['pyjwt']
)
