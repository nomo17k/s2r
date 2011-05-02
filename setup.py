#!/usr/bin/env python2.6
"""
Baseball stats to MLB 11 the Show ratings conversion utility.
"""
import glob
import os
import sys


# BEFORE importing distutils, remove MANIFEST. distutils doesn't
# properly update it when the contents of directories change.
if os.path.exists('MANIFEST'): os.remove('MANIFEST')
from distutils.core import setup, Extension


__version__ = '20110501'
__author__ = 'nomo17k'
__author_email__ = 'nomo17k@gmail.com'


# Check installed Python version.
python_ver = (2, 6, 1, 'final', 0)
if not hasattr(sys, 'version_info') or sys.version_info < python_ver:
    raise SystemExit('Python %s or later required.'
                     % '.'.join([str(c) for c in python_ver[:3]]))


def make_descriptions(docstr=__doc__):
    """
    Make __doc__ into short and long package descriptions.
    """
    docstrs = docstr.strip().split("\n")
    description = docstrs[0].strip()
    long_description = "\n".join(docstrs[2:])
    return description, long_description


def get_scripts():
    """
    Return paths of scripts to install
    """
    paths = ['bin/s2r_lahman.py',]
    #paths.extend(glob.glob('bin/*.py')]
    return paths


def main():
    descr_short, descr_long = make_descriptions()

    setup(name='s2r',
          version=__version__,
          author=__author__,
          author_email=__author_email__,
          maintainer=__author__,
          maintainer_email=__author_email__,
          url='',
          description=descr_short,
          long_description=descr_long,
          download_url='',
          platforms=['Linux'],
          license='GPL',
          packages=['s2r'],
          package_dir={'s2r': 's2r'},
          scripts=get_scripts(),
          ext_modules=[],
          #requires=['numpy']
          )


if __name__ == "__main__":
    main()
