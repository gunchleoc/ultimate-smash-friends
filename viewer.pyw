#!/usr/bin/env python
################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>
#
# This file is part of ultimate-smash-friends
#
# ultimate-smash-friends is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ultimate-smash-friends is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ultimate-smash-friends.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

import pygame
import os, sys
import getopt
import time
from xml.parsers.expat import ExpatError
import logging

try:
    import pygtk
    #pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtksourceview2
    import gtk.glade
    import gobject
except:
    sys.exit(1)

# our modules
from usf.config import Config

from usf.animations import EmptyAnimationException
from usf.game import Game, NetworkServerGame, NetworkClientGame
from usf.entity import Entity
from usf.debug_utils import draw_rect
from usf import entity_skin
from usf import loaders

config = Config()

# thanks to Samuel Abels
# http://csourcesearch.net/python/fidC15F2CB91333517E23E41191CFCDA6155BDC8B7B.aspx?s=cdef%3Atree+mdef%3Ainsert
def add_filters(filechooser):
    filter = gtk.FileFilter()
    filter.set_name("All XML files")
    filter.add_mime_type("text/xml")
    filechooser.add_filter(filter)

def create_filechooser_open():
    buttons     = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                   gtk.STOCK_OPEN,   gtk.RESPONSE_OK)
    filechooser = gtk.FileChooserDialog(
        "Open...",
        None,
        gtk.FILE_CHOOSER_ACTION_OPEN,
        buttons
        )
    add_filters(filechooser)
    return filechooser


def create_filechooser_save():
    buttons = (
        gtk.STOCK_CANCEL,
        gtk.RESPONSE_CANCEL,
        gtk.STOCK_SAVE,
        gtk.RESPONSE_OK
        )
    filechooser = gtk.FileChooserDialog(
        "Save...",
        None,
        gtk.FILE_CHOOSER_ACTION_SAVE,
        buttons
        )
    filechooser.set_do_overwrite_confirmation(True)
    add_filters(filechooser)
    return filechooser


# thanks to Seo Sanghyeon
# http://sparcs.kaist.ac.kr/~tinuviel/devel/gtksdl.py
def pygame_hack(widget):
    handle = widget.window.xid
    size = widget.size_request()
    os.environ['SDL_WINDOWID'] = str(handle)
    pygame.mixer.init()
    pygame.display.init()
    pygame.display.set_mode(size)
    #def callback(widget, *args):
        #handle = widget.window.xid
        #size = widget.size_request()
        #os.environ['SDL_WINDOWID'] = str(handle)
        #pygame.mixer.init()
        #pygame.display.init()
        #pygame.display.set_mode(size)
    #widget.connect('map-event', callback)

def update_pygame_widget(widget, game=None):
    screen = pygame.display.get_surface()
    # TODO
    screen.fill(pygame.Color("#CCCCFF"))
    if game.entity == None:
        screen.blit(
            loaders.image(os.path.join(config.sys_data_dir,'items','trunk','trunk.png'))[0],
            (time.time()*100%200,0)
            )
    else:
        #logging.debug((game.entity.place, game.entity.entity_skin.animation.rect))
        screen.blit(
            loaders.image(game.entity.entity_skin.animation.image)[0], (
                game.entity.place[0] - game.entity.entity_skin.animation.rect[2]/2,
                game.entity.place[1] - game.entity.entity_skin.animation.rect[3],
                )
            )
        draw_rect(screen, game.level)
    pygame.display.flip()

class NotGame(Game):
    """
    This object has the purpose of just containing informations to simulate a
    game for the character preview.

    """
    def __init__(self, gametime):
        self.gametime = 0
        self.events = []
        self.level = pygame.Rect(0,250, 250, 50)
        #self.level.moving_blocs = []
        self.entity = None

    def update(self, dt):
        for event in self.events:
            if not event.update(dt, self.gametime):
                self.events.remove(event)

        if self.entity is not None:
            logging.debug(dt)
            self.entity.entity_skin.update(time.time(), self.entity.reversed)

            self.entity.move(
                self.entity.vector[0] * dt,
                self.entity.vector[1] * dt
                )
            self.entity.vector[0] -= (
                config.general['AIR_FRICTION'] * self.entity.vector[0] * dt
                )
            self.entity.vector[1] -= (
                config.general['AIR_FRICTION'] * self.entity.vector[1] * dt
                )
            self.entity.place[0] %= 250
            self.entity.place[1] = max(
                self.entity.entity_skin.animation.rect[3],
                self.entity.place[1]
                )

            if self.entity.place[1] > 250:
                self.entity.place[1] = 250
                self.entity.vector[1] *= -.5
            else:
                self.entity.vector[1] += config.general['GRAVITY']

class usf_character_creator(object):
    """
    This is a gtk application to create and edit characters for
    ultimate-smash-friends, because designers are to weak for plain XML.

    """
    def __init__(self):
        self.gladefile = os.path.join(config.sys_data_dir, 'glade','usf_character_creator.glade')
        self.wTree = gtk.glade.XML(self.gladefile,'window1')

        self.window = self.wTree.get_widget("window1")
        if self.window:
            dic = {
                "on_open1_activate": self.open_character_loader,
                "on_quit1_activate": gtk.main_quit,
                "on_save1_activate": self.save,
                "on_window1_destroy": gtk.main_quit,
                "on_button_play_clicked": self.play_pygame,
                "on_button_pause_clicked": self.pause_pygame,
                "refresh_pygame_widget": self.pygame_load_character_from_buffer,
                "on_combobox_animations_changed": self.pygame_update_animation,
                }

            self.wTree.signal_autoconnect(dic)

        self.pygame_widget = self.wTree.get_widget('pygame_widget')
        self.pygame_widget.set_size_request(300,300)
        self.pygame_update = None
        self.play_pygame()

        self.language_manager = gtksourceview2.LanguageManager()
        lang = self.language_manager.get_language('xml')
        buffer = gtksourceview2.Buffer(language=lang)
        buffer.set_max_undo_levels(1000)
        self.buffer = buffer

        view = gtksourceview2.View()
        view.set_buffer(buffer)
        view.set_show_line_numbers(True)
        view.set_indent_on_tab(True)

        self.game = NotGame(time.time())

        self.character_dir = None

        self.wTree.get_widget("scrolledwindow_source").add(view)
        view.show()
        pygame_hack(self.pygame_widget)
        #self.wTree.get_widget("xml_text").set_auto_indent(True)

        self.last_refresh = time.time()

    def save(self, *args, **kwargs):
        try:
            file = open(self.character_filename)
            file.write(
                self.buffer.get_text(
                    self.buffer.get_start_iter(),self.buffer.get_end_iter()
                    )
                )
            file.close()
            self.wTree.get_widget('label_source').set_text('OK')

        except Exception, e:
            self.wTree.get_widget('label_source').set_text(e.message)

    def pygame_update_animation(self, *args, **kwargs):
        logging.debug('change animation '+self.wTree.get_widget(
                'combobox_animations').get_active_text())
        self.game.entity.entity_skin.change_animation(
            self.wTree.get_widget('combobox_animations').get_active_text(),
            self.game,
            params={
                'entity': self.game.entity,
                'world': self.game
                }
            )

    def pygame_load_character_from_buffer(self, *args, **kwargs):
        if self.character_dir is not None:
            self.game.entity = Entity( 0,
                                       self,
                                       entity_skinname=None,
                                       place=[100, 100]
                                       )
            try:
                self.game.entity.entity_skin = entity_skin.Entity_skin(
                    dir_name=self.character_dir,
                    xml_from_str = self.buffer.get_text(
                        self.buffer.get_start_iter(),self.buffer.get_end_iter()
                        )
                    )
                self.wTree.get_widget('label_source').set_text('OK')
                self.game.entity.entity_skin.current_animation =\
                    self.game.entity.entity_skin.animations.keys()[0]
                self.wTree.get_widget('combobox_animations').get_model().clear()
                for i in self.game.entity.entity_skin.animations.keys():
                    self.wTree.get_widget(
                        'combobox_animations'
                        ).get_model().append([i])
                for i in os.listdir(
                    os.sep.join(
                        self.character_filename.split(os.sep)[:-1]
                        )
                    ):
                    if '.png' in i:
                        self.wTree.get_widget(
                            'comboboxentry_images'
                            ).get_model().append([i])

            except (pygame.error, ExpatError, EmptyAnimationException), e:
                self.wTree.get_widget('label_source').set_text(e.message)
                #raise

    def play_pygame(self, *args, **kwargs):
        if self.pygame_update is None:
            self.pygame_update = gobject.idle_add(self.refresh)

    def pause_pygame(self, *args, **kwargs):
        if self.pygame_update is not None:
            gobject.source_remove(self.pygame_update)
            self.pygame_update = None

    def open_character_loader(self, *args, **kwargs):
        self.pause_pygame()
        file_loader = create_filechooser_open()
        if file_loader.run() == gtk.RESPONSE_OK:
            file = open(file_loader.get_filename())
            self.character_dir = os.sep.join(
                file_loader.get_filename().split( os.sep)[:-1]
                )
            self.character_filename = file_loader.get_filename()
            self.buffer.set_text(file.read())
            file.close()
            self.pygame_load_character_from_buffer()
        file_loader.destroy()
        self.play_pygame()

    def refresh(self):
        if time.time() - self.last_refresh < .03:
            pass
        else:
            self.last_refresh = self.game.gametime
            self.game.gametime = time.time()
            self.game.update(self.game.gametime - self.last_refresh)
            update_pygame_widget(self.pygame_widget, self.game)
        return True

    def create_frame(self):
        pass

    def delete_frame(self):
        pass

    def update_frame_time(self):
        pass

    def update_frame_skin(self):
        pass

    def add_vector(self):
        pass

    def update_vector(self):
        pass

    def del_vector(self):
        pass

    def add_aggressiv_point(self):
        pass

    def del_aggressive_point(self):
        pass

    def update_aggressiv_point(self):
        pass

    def add_event(self):
        pass

    def update_event(self):
        pass

    def del_event(self):
        pass

    def move_event_up(self):
        pass

    def move_event_down(self):
        pass

if __name__ == '__main__':
    ucc = usf_character_creator()
    gtk.main()

