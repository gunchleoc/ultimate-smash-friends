import os
from xml.dom.minidom import parse


class CharacterProject:
    def __init__(self, path):
        self.frames = None
        self.nb = None

        self.doc = parse(path)
        self.root = self.doc.getElementsByTagName('character')[0]
        self.mov = self.doc.getElementsByTagName('movement')[0]
        self.duration = int(self.mov.getAttribute('duration'))
        self.directory = os.path.dirname(path) + '/'

        # movements
        self.movements = []
        for mov in self.doc.getElementsByTagName('movement'):
            self.movements.append(mov.getAttribute('name'))

    def get_picture(self, nb=0):
        self.mov = self.doc.getElementsByTagName('movement')[nb]
        self.duration = int(self.mov.getAttribute('duration'))
        img = self.mov.getElementsByTagName('frame')[0].getAttribute('image')
        return self.directory + img

    def get_frames(self, nb=0):
        if self.frames and self.nb == nb:
            return self.frames
        self.nb = nb
        self.mov = self.doc.getElementsByTagName('movement')[nb]
        self.duration = int(self.mov.getAttribute('duration'))
        self.frames = []
        frames_e = self.mov.getElementsByTagName('frame')
        i = 0
        for frame in frames_e:
            i += 1
            #attributes = []
            if i == len(frames_e):
                time = self.duration - float(frame.getAttribute('time'))
            else:
                time = float(frames_e[i].getAttribute('time'))
            self.frames.append([
                time / 1000,
                frame.getAttribute('image'),
                frame.getAttribute('hardshape')
            ])
        return self.frames
