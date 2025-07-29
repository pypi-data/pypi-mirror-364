from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='rithlog',
  version='0.0.1',
  author='kolyax',
  author_email='abobus050413@gmail.com',
  description='This is the simplest module to log',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url="https://example.com",
  packages=find_packages(),
  install_requires=['requests>=2.25.1','rith>=0.0.11'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='log loger rith',
  project_urls={
    #'GitHub': 'your_github'
  },
  python_requires='>=3.6,<=3.11'
)
