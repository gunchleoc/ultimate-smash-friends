###############################################################################
# copyright 2010 Edwin Marshall (aspidites) <aspidties@gmx.com>               #
#                                                                             #
# This file is part of UltimateSmashFriends                                   #
#                                                                             #
# UltimateSmashFriends is free software: you can redistribute it and/or       #
# modify it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# UltimateSmashFriends is distributed in the hope that it will be useful,     #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with UltimateSmashFriends.                                            # 
# If not, see <http://www.gnu.org/licenses/>.                                 #
###############################################################################

""" As of right now, non of the interface is abstracted, so the API mimicks
    SafeConfigParser's exactly:

    config.get(section, option) to fetch an option
    config.set(section, option, value) to set an option
    config.write(config_file) to save all options
    config.items(section) to list all options in a section

    I'm contemplating wrapping ConfigParser so that the following can be done:
    section.option to fetch an option
    section.option = value to set an option
    config.save() to save all options
    section.options to list all options in a section

    The primary benefit of wrapping ConfigParser is that less typing would be
    required. Compare:
    config.set('GENERAL', 'WALKSPEED', 200)
    GENERAL.WALKSPEED = 200
"""

from __future__ import with_statement

from os import environ, makedirs, path, stat
from sys import prefix
from ConfigParser import SafeConfigParser
import platform
import logging

OS = platform.system().lower()

class Option(dict):
    def __init__(self, args, **kwargs):
        self.name = kwargs['name']
        del kwargs['name']

        self.__parser = kwargs['parser']
        del kwargs['parser']

        self.__config = kwargs['config']
        del kwargs['config']

        dict.__init__(self, args, **kwargs)

    def __setitem__(self, option, value):
        self.__parser.set(self.name, option, value)
        dict.__setitem__(self, option, value)
        with open(self.__config, 'wb') as config_file:
            self.__parser.write(config_file)


class Config(object):
    """ Object that implements automatic saving.
        
        Config first loads default settings from the system config file, then
        overwrites those with the ones found in the user config file. 
        
        Different config sections can be accessed as
        attributes (eg. Config().section), which would then return an Option 
        object, which acts virtually identical to the builtin dict type. As
        such, specific options can be accesed as keys
        (Config().section[option]).
    """
        
    def __init__(self):
        self.__parser = SafeConfigParser()
        self.__parser.optionxform=str

        (self.config_dir, self.sys_config_file, 
         self.user_config_file, self.data_dir) = self.__get_locations()

        # load sys config options and replace with defined user config options
        self.read([self.sys_config_file, self.user_config_file])
        self.save()

    def __get_locations(self):
        """ returns the appropriate locations of the config directory, system
            config file, user config file, and datadirectories according to the
            user's platform
        """

        # may need to expand once other platforms are tested
        if OS == 'windows':
            # set the config directory to the parent directory of this script
            config_dir = path.dirname(path.abspath(path.join(__file__, '..')))
            sys_config_file = path.join(config_dir, 'rc.config')
            user_config_file = sys_config_file
            data_dir = path.join(config_dir, 'data')
        else:
            try: 
                # determine if usf has been installed. If not, use config_dir as the data
                # dir, similar to windows
                data_dir = path.join(prefix, 'share', 
                                     'ultimate-smash-friends', 'data')
                stat(data_dir)
                sys_config_file = path.join(prefix, 'etc', 
                                            'ultimate-smash-frields', 
                                            'rc.config')

                if 'XDG_CONFIG_HOME' in environ.keys():
                    config_dir = path.join(environ['XDG_CONFIG_HOME'], 'usf')
                    user_config_file = path.join(config_dir, 'rc.config')
                else:
                    config_dir = path.join(environ['HOME'], '.config', 'usf')
                    user_config_file = path.join(config_dir, 'rc.config')
            except OSError:
                config_dir = path.dirname(path.abspath(path.join(__file__, '..')))
                sys_config_file = path.join(config_dir, 'rc.config')
                user_config_file = sys_config_file
                data_dir = path.join(config_dir, 'data')
        
        # create config directory and user config file
        try:
            logging.debug('creating new config directory')
            makedirs(config_dir)
        except OSError as (code, message):
           pass

        return config_dir, sys_config_file, user_config_file, data_dir

    def save(self):
        with open(self.user_config_file, 'wb') as config_file:
            self.__parser.write(config_file)

    def read(self, files):
        self.__parser.read(files)

        # dynamically create attributes based on sections in the config file,
        # then assign a dictionary of the form "option: value" to each
        # attribute.

        for section in self.__parser.sections():
            setattr(self, section, Option(([item for item in
                    self.__parser.items(section)]),
                    parser=self.__parser,
                    config=self.user_config_file,
                    name=section))
            """
            setattr(self, section, 
                    Option(([[str(item) for item in tuple]
                            for tuple in self.__parser.items(section)]),
                            parser=self.__parser,
                            config=self.user_config_file,
                            name=section))
            """
