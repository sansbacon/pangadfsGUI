# -*- coding: utf-8 -*-
"""
setup.py

installation script

"""

from setuptools import setup, find_packages

PACKAGE_NAME = "pangadfs_gui"


def run():
    setup(name=PACKAGE_NAME,
          version="0.1",
          description="GUI for pangadfs optimizer",
          author="Eric Truett",
          author_email="eric@erictruett.com",
          license="MIT",
          packages=find_packages('src'),
          package_dir={'': 'src'},
          include_package_data=True,          
          zip_safe=False
        )


if __name__ == '__main__':
    run()
