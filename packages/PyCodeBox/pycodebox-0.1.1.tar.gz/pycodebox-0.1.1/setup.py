from setuptools import setup, find_packages

setup(
  name='PyCodeBox',
  version='0.1.1',
  author='Zachary D Wallen',
  description="""A personal collection of convenience functions for styling data 
    displays and outputs, transforming and organizing data, performing statistical 
    analyses, and other commonly performed actions in data science projects.""",
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  license='MIT',
  packages=find_packages(),
  install_requires=[
    'IPython',
    'numpy',
    'openpyxl',
    'pandas',
    'plotnine>=0.10.1',
    'scipy',
  ],
  classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
  ],
  python_requires='>=3.9',
)
