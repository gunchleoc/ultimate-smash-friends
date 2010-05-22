################################################################################
# copyright 2009 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
#                                                                              #
# This file is part of Ultimate Smash Friends.                                 #
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

# Our modules
from config import Config
config = Config()

class Screen(object):
    def __init__(self, name, screen):
        self.name = name
        self.screen = screen
        self.init()
        self.widget.update_size()
        self.widget.update_pos()
    def add(self, widget):
        self.widget = widget
        #define the position and the size of the top-level widget
        self.widget.setSize(config.general['WIDTH'],config.general['HEIGHT'])
        self.widget.x = 0
        self.widget.y = 0
    def update(self):
        self.screen.blit(self.widget.draw(), (0,0))
    def init(self):
        pass
    def callback(self, action):
        pass
        
