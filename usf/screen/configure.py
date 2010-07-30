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

from screen import Screen
from usf import widgets
import copy


class configure(Screen):
    def init(self):
        self.add(widgets.VBox())
        self.set_name(_("configure"))

        #I18N:option screen
        self.widget.add(widgets.Button(_('Audio')),
                        margin=50,
                        margin_left=290)

        self.widget.add(widgets.Button(_('Screen')),
                        margin_left=290)

        self.widget.add(widgets.Button(_('Keyboard')),
                        margin_left=290)
    
        self.widget.add(widgets.Button(_('Back')),
                        margin_left=20,
                        margin=100)

    def callback(self,action):
        if action.text == _('Audio'):
            return "goto:sound"
        if action.text == _('Screen'):
            return "goto:screen_screen"
        if action.text == _('Keyboard'):
            return "goto:keyboard"
        if action.text == _('Back'):
            return "goto:back"
