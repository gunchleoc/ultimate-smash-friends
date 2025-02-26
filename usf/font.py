################################################################################
# copyright 2010 Lucas Baudin <xapantu@gmail.com>                              #
#                                                                              #
# This file is part of UltimateSmashFriends                                    #
#                                                                              #
# UltimateSmashFriends is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation, either version 3 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# UltimateSmashFriends is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.#
################################################################################

#our modules

from usf import CONFIG

#standart imports
import xml.etree.ElementTree as xml
from os.path import join
from os import stat

#library import
import pygame

from usf.memoize import memoize

pygame.font.init()


@memoize
class FontList(object):

    def __init__(self):
        '''#TODO: documentation
        '''
        self.list = {}
        font_xml = xml.parse(join(CONFIG.system_path, "fonts", "fonts.xml"))
        for font in font_xml.findall("font"):

            #use theme fonts
            try:
                font_file = join(CONFIG.system_path, "gui",
                    CONFIG.general.THEME, font.get('file'))
                stat(font_file)
            #use default usf fonts
            except:
                font_file = join(CONFIG.system_path, "fonts", font.get('file'))

            self.list[font.get('name')] = (Font(font.get('name'),
                int(font.get('size')), font_file))

    def __getitem__(self, item):
        if item in self.list:
            return self.list[item]
        else:
            logging.info("No font named" + str(item))
            return self.list['sans']


@memoize
class Font(object):
    ''' #TODO documentation
    '''

    def __init__(self, name, size, font_file, bold="", italic="",
            bolditalic=""):
        self.size = {}
        self.font_file = font_file
        self.font = pygame.font.Font(font_file, 480/size)
        if bold != "":
            self.bold = pygame.font.Font(bold,
                480/size)
        if italic != "":
            self.italic = pygame.font.Font(italic,
                480/size)
        if bolditalic != "":
            self.bolditalic = pygame.font.Font(bolditalic,
                480/size)

    def __getitem__(self, item):
        if item == "normal":
            return self.font
        if item == "bold" and self.bold:
            return self.bold
        if item == "italic" and self.italic:
            return self.italic
        if item == "bolditalic" and self.bolditalic:
            return self.bolditalic
        if item not in self.size:
            self.size[item] = pygame.font.Font(self.font_file, 480/int(item))
        #logging.info("No font named : " + str(item))

        return self.size[item]

fonts = FontList()

