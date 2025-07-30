from setuptools import setup, find_packages

setup(
  name='sentiment_analysis_lib',
  version='1.1',
  description='This is a simple Python package for analysing sentiment of text data.',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',
  author='Hemanth',
  author_email=' x22183744@student.ncirl.ie',
  license='MIT',
  classifiers=[
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Programming Language :: Python :: 3'
],
  keywords='sentiment_analysis_lib', 
  packages=find_packages(),
  python_requires=">=3.6"
)
