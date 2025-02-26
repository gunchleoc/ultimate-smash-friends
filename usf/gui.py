################################################################################
# copyright 2010 Lucas Baudin <xapantu@gmail.com>                              #
#                                                                              #
# This file is part of Ultimate Smash Friends                                  #
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
'''
The Gui module provide interfaces to build custom screens with widgets and
callback to use them.

'''

import os
import time
import pygame
from pygame.locals import QUIT

# Our modules
from usf.font import fonts
from usf.game import Game
from usf.screens.about import About
from usf.screens.characters import Characters
from usf.screens.configure import Configure
from usf.screens.keyboard import Keyboard
from usf.screens.level import Level
from usf.screens.main_screen import MainScreen
from usf.screens.resume import Resume
from usf.screens.display import Display
from usf.screens.audio import Audio
from usf.screens.network_screen import NetworkScreen
from usf.screens.network_join_screen import NetworkJoinScreen
from usf.screens.network_game_conf_screen import NetworkGameConfScreen
from usf.skin import Skin
from usf.translation import _
from usf.widgets.widget import optimize_size
from usf import loaders
from usf import CONFIG


class Gui(object):
    """
    Main class of the GUI. Init and maintain all menus and widgets.

    """

    def __init__(self, surface):
        self.screen = surface
        self.game = None
        self.screens = {}
        self.screen_history = []

        self.screens['main_screen'] = MainScreen('main_screen', self.screen)
        self.screens['configure'] = Configure('configure', self.screen)
        self.screens['about'] = About('about', self.screen)
        self.screens['resume'] = Resume('resume', self.screen)
        self.screens['sound'] = Audio('sound', self.screen)
        self.screens['display'] = Display('display', self.screen)
        self.screens['keyboard'] = Keyboard('keyboard', self.screen)
        self.screens['level'] = Level('level', self.screen)
        self.screens['characters'] = Characters('characters', self.screen)
        self.screens['network'] = NetworkScreen('network', self.screen)
        self.screens['network_join'] = NetworkJoinScreen(
                'network_join', self.screen)
        self.screens['network_game_conf_screen'] = NetworkGameConfScreen(
                'network_game_conf_screen', self.screen)

        self.current_screen = 'main_screen'
        self.skin = Skin()
        self.last_event = time.time()
        self.image = 0
        self.focus = None
        self.state = "menu"
        self.cursor = loaders.image(
                CONFIG.system_path + os.sep + 'cursor.png')[0]
        self.update_youhere()

    def update(self):
        """
        Update the GUI, it draws the mouse, and the menu.
        """

        #draw the background
        self.skin.get_background()

        self.screens[self.current_screen].update()

        while(True):
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                pygame.event.post(pygame.event.Event(QUIT))
                break

            elif event.type != pygame.NOEVENT:
                if event.type == pygame.KEYDOWN:
                    self.handle_keys(event)
                elif (event.type == pygame.MOUSEBUTTONUP or
                    event.type == pygame.MOUSEBUTTONDOWN or
                    event.type == pygame.MOUSEMOTION):
                    self.handle_mouse(event)

            else:
                break
        #draw the '> you are here :' dialog
        #update the mouse position
        x, y = pygame.mouse.get_pos()
        #x += self.cursor.get_height()
        #y += self.cursor.get_width()
        self.screen.blit(self.cursor, (x, y))

        #if we have a game instance and the state is menu...
        if self.game and self.state != "ingame":
            self.state = "ingame"
            return True, self.game

        return False, None

    def handle_mouse(self, event):
        """
        This function handles mouse event which are send from the update
        function.
        """
        if not self.focus:
            event.dict['pos'] = (
              event.dict['pos'][0] - self.screens[self.current_screen].widget.x,
              event.dict['pos'][1] - self.screens[self.current_screen].widget.y)

            (query, self.focus) = (
                self.screens[self.current_screen].widget.handle_mouse(event))

        else:
            (query, focus) = self.focus.handle_mouse(event)
            if not focus:
                self.focus = None

        if  query:
            reply = self.screens[self.current_screen].callback(query)
            self.handle_reply(reply)
        #remove the event for performance, maybe it is useless
        del(event)

    def handle_keys(self, event):
        """
        This function handles keyboard event which are send from the update
        function.
        """
        #TODO : a complete navigation system with the keyboard.
        reply = False
        query = False

        if self.focus:
            (query, focus) = self.focus.handle_keys(event)
            if not focus:
                self.focus = None
            if query:
                reply = self.screens[self.current_screen].callback(query)
                self.handle_reply(reply)

        if not self.focus and (not reply and not query):
            if event.dict['key'] == pygame.K_ESCAPE:
                self.handle_reply({'goto': 'back'})
            else:
                (query, focus) = (
                        self.screens[self.current_screen].handle_keys(event))

                if not focus:
                    self.focus = None

                else:
                    self.focus = focus

                if  query:
                    reply = self.screens[self.current_screen].callback(query)
                    self.handle_reply(reply)

        #remove the event for performance, maybe it is useless
        del(event)

    def handle_reply(self, reply):
        """
        This function handles the callback return by the screens with the
        function event_callback().
        This callback needs to be a dictionary, otherwise, it will be ignored.

        The reply can be:
            {'goto': 'myscreen'}
                where my screen is the name of the screen loaded in __init__()
            {'goto': 'back'}
                go to the last menu, it is usually used for a back button
            {'game': 'new'}
                to start a new game
            {'game': 'new_server'}
                to start a new game in server mode
            {'game': 'join_server'}
                to join a network game
            {'game': 'continue'}
                to resume the game, it is used in the in-game menu
            {'game': 'stop' }
                to stop the game, it is used to qui the game in the
                in-game menu
        """
        if hasattr(reply, 'get'):
            sound = loaders.track(os.path.join(CONFIG.system_path,
                                  "sounds", "mouseClick2.wav"))
            sound.set_volume(CONFIG.audio.SOUND_VOLUME / 100.0)
            sound.play()

            # not using elifs so that replies may be complex
            if reply.get('goto'):

                if reply['goto'] == 'back':
                    self.screen_back()
                else:
                    self.screen_history.append(self.current_screen)
                    self.current_screen = reply['goto']

            if reply.get('game'):
                if reply['game'] == 'new':
                    self.game = self.launch_game()
                    self.current_screen = 'resume'
                    self.screen_history = []
                    self.state = "menu"
                elif reply['game'] == 'new_server':
                    self.game = self.launch_game(server=True)
                    self.current_screen = 'resume'
                    self.screen_history = []
                    self.state = "menu"
                elif reply['game'] == 'join_server':
                    self.game = self.launch_game(
                            server=self.screens['network_join'].ip)
                    self.current_screen = 'resume'
                    self.screen_history = []
                    self.state = "menu"
                elif reply['game'] == 'continue':
                    self.current_screen = 'resume'
                    self.screen_history = []
                    self.state = "menu"
                elif reply['game'] == 'stop':
                    self.state = "menu"
                    self.game = None
                    self.current_screen = 'main_screen'
                    self.screen_history = []

    def screen_back(self):
        """
        Go to the last screen.
        """
        if len(self.screen_history) > 0:
            self.current_screen = self.screen_history[-1]
            self.screen_history.pop()
            return True

        return False

    def update_youhere(self):
        screen_list = ""
        for scr in self.screen_history:
            screen_list += scr + "/"

        screen_list += self.current_screen + "/"
        self.here = loaders.text("> " + _("you are here:") + screen_list,
            fonts['mono']['30'])

    def transition_slide(self, old_screen, old_surface, new_screen,
            new_surface):
        text = get_text_transparent(old_screen.name)

        for i in range(0, 10):
            time.sleep(1.00 / float(CONFIG.general.MAX_FPS))
            self.skin.get_background()
            text.set_alpha((i * -1 + 10) * 250 / 10)
            self.screen.blit(text,
                (old_screen.indent_title, 10))
            self.screen.blit(old_surface,
                (optimize_size((i * 8 * 10, 0))[0], old_screen.widget.y))

            pygame.display.update()

        text = get_text_transparent(new_screen.name)

        for i in range(0, 10):
            time.sleep(1.00 / float(CONFIG.general.MAX_FPS))
            self.skin.get_background()
            text.set_alpha(i * 250 / 10)
            self.screen.blit(text,
                    (self.screens[self.current_screen].indent_title, 10))
            self.screen.blit(new_surface,
                (optimize_size((i * 8 * 10 - 800, 0))[0],
                self.screens[self.current_screen].widget.y))

            pygame.display.update()

    def transition_fading(self, old_screen, old_surface, new_screen,
            new_surface):
        text = get_text_transparent(old_screen.name)

        for i in range(0, 5):
            back = self.skin.get_background().convert()
            time.sleep(1.00 / float(CONFIG.general.MAX_FPS))
            self.screen.blit(self.skin.get_background(), (0, 0))
            text.set_alpha((i * -1 + 5) * 250 / 5)
            self.screen.blit(text, (old_screen.indent_title, 10))

            #back.set_alpha( (i * (- 1) + 5) *250 / 5)
            back.set_alpha(i * 250 / 5)
            self.screen.blit(old_surface,
                    (old_screen.widget.x, old_screen.widget.y))
            self.screen.blit(back, (0, 0))

            pygame.display.update()

        text = get_text_transparent(new_screen.name)

        for i in range(0, 5):
            back = self.skin.get_background().convert()
            time.sleep(1.00 / float(CONFIG.general.MAX_FPS))
            self.screen.blit(self.skin.get_background(), (0, 0))
            text.set_alpha(i * 250 / 5)
            self.screen.blit(text,
                    (self.screens[self.current_screen].indent_title, 10))

            #new_surface.set_alpha(i  * 250 / 5)
            back.set_alpha((i * -1 + 5) * 250 / 5)
            self.screen.blit(new_surface,
                    (new_screen.widget.x, new_screen.widget.y))
            self.screen.blit(back, (0, 0))

            pygame.display.update()

    def launch_game(self, server=False):
        """
        Function to launch the game, use precedant user choices to initiate the
        game with level and characters selected.

        """
        players = []
        for i in range(0, len(self.screens["characters"].players)):
            if self.screens["characters"].players[i] != 0:
                file_name = (
                        self.screens["characters"].game_data['character_file']
                                [self.screens["characters"].players[i]])
                if self.screens["characters"].checkboxes_ai[i].get_value():
                    file_name = file_name.replace(
                            "characters/", "characters/AI")
                players.append(file_name)

        if len(players) > 1:
            game = Game(
                self.screen,
                self.screens["level"].get_level(),
                players)

            #thread.start_new_thread(self.loading, ())
            #self.goto_screen("ingame.usfgui", False)
            #self.state="game"
            return game


def get_text_transparent(name):
    text = loaders.text(name, fonts['mono']['15']).convert()
    text.fill(pygame.color.Color("black"))
    #TODO: the colorkey should be a property of the skin
    text.set_colorkey(pygame.color.Color("black"))
    text.blit(loaders.text(name, fonts['mono']['15']), (0, 0))
    return text
