import logging
import os


class Disk():
    def __init__(self, filename, mode='rb', buffering=0):
        self.mode = mode
        self.pos = 0  # linear pos in the virtual stream
        self.si = 0  # disk sector index
        self.so = 0  # sector offset
        self.lastsi = 0  # last sector read from *disk*
        self.blocksize = 512
        self._file = open(filename, mode, buffering)
        self.size = os.stat(filename).st_size

        return

    def __str__(self):
        return "Filename: " + self._file.name + "\t Mode: " + self.mode + "\t Size: " + str(self.size)

    def seek(self, offset, whence=0):
        if whence == 1:
            self.pos += offset
        elif whence == 2:
            if self.size and offset < self.size:
                self.pos = self.size - offset
            elif self.size and offset >= self.size:
                self.pos = 0
        else:
            self.pos = offset
        self.si = int(self.pos / self.blocksize)
        self.so = self.pos % self.blocksize

        logging.debug("disk pointer to set @%Xh", self.si * self.blocksize)
        self._file.seek(self.si * self.blocksize)
        logging.debug("si=%Xh lastsi=%Xh so=%Xh", self.si, self.lastsi, self.so)

    def write(self, s):
        self._file.write(s)
        pass