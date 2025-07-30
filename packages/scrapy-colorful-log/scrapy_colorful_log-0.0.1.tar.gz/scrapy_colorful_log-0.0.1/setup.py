from setuptools import setup, find_packages


MAJOR =0
MINOR =0
PATCH =1
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"

setup(
  name="scrapy-colorful-log",
  version=VERSION,
  author="Nan",
  author_email="",
  long_description_content_type="text/markdown",
  url='https://github.com/Manjusaka-N/scrapy-colorful-log.git',
  description='A lightweight scrapy log customize module',
  long_description=open('README.md', encoding="utf-8").read(),
  python_requires=">=3.6",
  # install_requires=get_install_requires(),
  packages=find_packages(),
  license='Apache',
  classifiers=[
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ],
  # package_data={'': ['*.csv', '*.txt', '.toml']},  # 这个很重要
  include_package_data=True  # 也选上

)
