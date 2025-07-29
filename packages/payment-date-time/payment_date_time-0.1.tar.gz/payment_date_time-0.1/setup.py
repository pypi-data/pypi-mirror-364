from setuptools import setup, find_packages

setup(
  name='payment_date_time',
  version='0.1',
  description='This is a simple Python package for showing payment current date and time.',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',
  author='Siddharth Manik',
  author_email=' x23289678@student.ncirl.ie',
  license='MIT',
  classifiers=[
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Programming Language :: Python :: 3'
],
  keywords='payment_date_time', 
  packages=find_packages(),
  python_requires=">=3.6"
)
