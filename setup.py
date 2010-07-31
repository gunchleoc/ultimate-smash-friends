#!/usr/bin/env python
from __future__ import with_statement

""" The files method was adapted from the AutoDataDiscovery solution in the
    official Distutils Cookbook:
    http://wiki.python.org/moin/Distutils/Cookbook/AutoDataDiscovery

"""

import sys, os, platform, imp
from os import environ, sep
from os.path import abspath, join, splitext, isdir, isfile
from sys import exit
from distutils.core import setup
OS = platform.system().lower()
if OS == 'windows':
    import py2exe

    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    def isSystemDLL(pathname):
           if os.path.basename(pathname).lower() in ["sdl_ttf.dll", "libogg-0.dll"]:
                   return 0
           return origIsSystemDLL(pathname)
    py2exe.build_exe.isSystemDLL = isSystemDLL
    OS = platform.system().lower()

"""
if OS == 'windows' or 'bdist_wininst' in sys.argv:
    print ('This script was not meant to be run under windows. If you want '
          'to create a package for windows, please install InnoSetup and use'
          'the included setup.iss script, thanks.')
    sys.exit(1)
"""
def files(path):
    """ Return all non-python-file filenames in path """
    result = []
    all_results = []
    module_suffixes = [info[0] for info in imp.get_suffixes()]
    ignore_dirs = ['cvs']
    for item in os.listdir(path):
        name = join(path, item)
        if (
            isfile(name) and
            splitext(item)[1] not in module_suffixes
            ):
            result.append(name)
        elif isdir(name) and item.lower() not in ignore_dirs:
            all_results.extend(files(name))
    if result:
        all_results.append([path, result])
    return all_results

if OS != 'windows':
    data = [(join('share', 'ultimate-smash-friends') + sep + item[0], item[1])
            for item in files('data')]
    data.append((join('share', 'ultimate-smash-friends') + sep + 'data', ['CREDITS.txt']))
else:
    data = [(item[0], item[1])
            for item in files('data')]
    data.append('CREDITS.txt')

    
doc = [(join('share', 'doc', 'ultimate-smash-friends') +
       item[0].replace('doc', ''), item[1]) for item in files('doc')]
doc[-1][-1].append('COPYING.txt')
doc[-1][-1].append('CREDITS.txt')
doc[-1][-1].append('README.txt')
doc[-1][-1].append('README.fr.txt')

config = [(sep + join('etc', 'ultimate-smash-friends'), ['system.cfg'])]

icon = [(join('share', 'applications'), 
              ['ultimate-smash-friends.desktop'])]

scripts = ['ultimate-smash-friends',
               'viewer.pyw', 'utils/togimpmap.py', 
               'utils/tolevel.py', 
               'utils/xml_text_extractor.py']

setup(name='ultimate-smash-friends',
      version='0.1.3',
      description=('A 2d arcade fight game, based on the gameplay of super '
                   'smash bros, from nintendo.'),
      author='Gabriel Pettier',
      author_email='gabriel.pettier@gmail.com',
      maintainer='Lucas Baudin (xapantu)',
      maintainer_email='xapantu@gmail.com',
      url='http://usf.tuxfamily.org/',
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Operating System :: OS Independent',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Topic :: Games/Entertainment :: Arcade'
                  ],
      packages=['usf', 'usf.widgets', 'usf.screen'],
      scripts=scripts,
      requires=['pygame (>=1.6)', 'python (>=2.5)'],
      data_files=(data + doc + config + icon),
	  windows=[{"script" : "ultimate-smash-friends", "icon_resources" : [(1, "data/icon/icon.ico")]}]
     )
