#i###############################################################################
# copyright 2009 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
#                                                                              #
# This file is part of Ultimate Smash Friends                                  #
#                                                                              #
# Ultimate Smash Friends is free software: you can redistribute it and/or      #
# modify it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or (at your   #
# option) any later version.                                                   #
#                                                                              #
# Ultimate Smash Friends is distributed in the hope that it will be useful, but#
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or#
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# You should have received a copy of the GNU General Public License along with #
# Ultimate Smash Friends.  If not, see <http://www.gnu.org/licenses/>.         #
################################################################################

import pygame
from pygame.locals import USEREVENT, QUIT
from math import sin, cos
from time import time
import os
import time
import xml.dom.minidom
import logging
import thread
# Our modules

from config import Config

config = Config()

import controls
import entity_skin
from game import Game
import controls
import loaders
# Gui modules
from widgets import (HBox, VBox, Label)
from skin import Skin
#translation
import translation
        

class NewGui(object):
    """
    Main class of the GUI. Init and maintain all menus and widgets.

    """
    def __init__(self, surface):
        self.screen = surface
        self.screens = {}
        #TODO : Use a config file
        screens = ['main_screen']
        for name in screens:
            exec("import screen." + name)
            exec('scr = screen.' + name + '.' + name + "('"+ name +"',self.screen)")
            self.screens[name] = scr
        self.screen_current = 'main_screen'
        self.skin = Skin()
        self.last_event = time.time()
        self.image = 0
        self.focus = None
    def update(self, first, second, third):
        #FIXME : it sould be in main.pyw
        time.sleep(1.00/float(config.general['MAX_FPS']))
        while(True):
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                pygame.event.post( pygame.event.Event(QUIT) )
                break
            elif event.type != pygame.NOEVENT:
                if self.focus != None:
                    pass
                else:
                    if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
                        self.handle_keys(event)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.handle_mouse(event)
            else:
                break
        #draw background
        self.screen.blit(loaders.image(
            config.sys_data_dir+
            os.sep+
            "gui"+
            os.sep +
            'japan'+
            os.sep+
            self.skin.background[0],
            scale=(config.general['WIDTH'],
            config.general['HEIGHT'])
            )[0], (0,0))
        self.screens[self.screen_current].update()
        return False, None
    def handle_mouse(self,event):
        query = self.screens[self.screen_current].widget.handle_mouse(event)
        if  query != False:
            print query
            self.screens[self.screen_current].callback(query)
        del(event)
    def handle_keys(self,event):
        print event









class Dialog(object):
    state = False
    image = None
    def __init__(self, screen, name):
        global skin
        self.background = loaders.image(
            config.sys_data_dir+
            os.sep+
            'gui'+
            os.sep+
            config.general['THEME']+
            os.sep+
            "background-dialog.png", scale=(skin.dialog['sizex'], skin.dialog['sizey'])
            )[0]
        self.background.set_alpha(150)
        self.screen = screen
    def draw(self):
        self.screen.blit(self.tmp_screen, (0,0))
        self.screen.blit(self.background, (skin.dialog['posx'], skin.dialog['posy']))
    def show(self):
        if self.state is False:
            self.state = True
            self.tmp_screen = self.screen.copy()
            cache = pygame.Surface((config.general['WIDTH'], config.general['HEIGHT']))
            cache.fill(pygame.color.Color("black"))
            cache.set_alpha(100)
            self.tmp_screen.blit(cache, (0,0))
        else:
            self.state = False
            self.tmp_screen = None
