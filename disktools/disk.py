import logging
import os, sys, atexit
import io
from ctypes import *


class Disk(object):
    def __init__(self, filename, mode='rb', buffering=0):
        self.mode = mode
        self.pos = 0  # linear pos in the virtual stream
        self.si = 0  # disk sector index
        self.so = 0  # sector offset
        self.buf = None # Read buffer
        self.rawcache = bytearray(1024<<10)
        self.cache = memoryview(self.rawcache)
        self.cache_index = 0  # offset of next cache slot
        self.cache_hits = 0  # sectors retrieved from cache
        self.cache_misses = 0  # sectors not retrieved
        self.cache_extras = 0  # direct, non-cacheable I/O
        self.cache_dirties = {}  # dirty sectors
        self.cache_table = {}  # { sector: cache offset }
        self.cache_tableR = {}  # reversed: { cache offset:sector }
        self.lastsi = 0  # last sector read from *disk*
        self.blocksize = 512
        self._file = open(filename, mode, buffering)
        self.size = os.stat(filename).st_size
        atexit.register(self.cache_flush)
        return

    def __str__(self):
        return "Filename: " + self._file.name + "\t Mode: " + self.mode + "\t Size: " + str(self.size)

    def seek(self, offset, whence=0, force=0):
        if whence == 1:
            self.pos += offset
        elif whence == 2:
            if self.size and offset < self.size:
                self.pos = self.size - offset
            elif self.size and offset >= self.size:
                self.pos = 0
        else:
            self.pos = offset
        self.si = int(self.pos // self.blocksize)
        self.so = int(self.pos % self.blocksize)

        logging.debug("disk pointer to set @%Xh", self.si * self.blocksize)
        if force == 1:
            self._file.seek(self.pos)
        else:
            self._file.seek(self.si * self.blocksize)
        logging.debug("si=%Xh lastsi=%Xh so=%Xh", self.si, self.lastsi, self.so)

    def write(self, s):
        logging.debug("request to write %d bytes @%Xh", len(s), int(self.pos))
        if len(s) == 0: return
        # If we have to complete a sector...
        if self.so:
            j = min(self.blocksize - self.so, len(s))
            logging.debug("writing middle sector %d[%d:%d]", self.si, self.so, self.so + j)
            self.asize = 512
            if not self.cache_retrieve():
                self.cache_readinto()
            # We assume buf is pointing to rawcache
            self.buf[self.so: self.so + j] = s[:j]
            s = s[j:]  # slicing penalty if buffer?
            logging.debug("len(s) is now %d", len(s))
            self.cache_dirties[self.si] = True
            self.pos += j
            self.seek(self.pos)
        # if we have full sectors to write...
        if len(s) > self.blocksize:
            full_blocks = len(s) // 512
            logging.debug("writing %d sector(s) directly to disk", full_blocks)
            # Directly write full sectors to disk
            # ~ self._file.seek(self.si*self.blocksize)
            # Invalidate eventually cached data
            for si in range(self.si, self.si + full_blocks):
                if si in self.cache_table:
                    logging.debug("removing sector #%d from cache", si)
                    Ri = self.cache_table[si]
                    del self.cache_tableR[Ri]
                    del self.cache_table[si]
                    if si in self.cache_dirties:
                        logging.debug("removing sector #%d from dirty sectors", si)
                        del self.cache_dirties[si]
            self._file.write(s[:full_blocks * 512])
            self.pos += full_blocks * 512
            self.seek(self.pos)
            s = s[full_blocks * 512:]  # slicing penalty if buffer?
            logging.debug("len(s) is now %d", len(s))
        if len(s):
            logging.debug("writing sector %d[%d:%d] from start", self.si, self.so, self.so + len(s))
            self.asize = 512
            if not self.cache_retrieve():
                self.cache_readinto()
            self.buf[self.so: self.so + len(s)] = s
            self.cache_dirties[self.si] = True
            self.pos += len(s)
        self.seek(self.pos)
        self.lastsi = self.si
        pass

    def read(self, size: int =-1, offset = 0):
        #logging.debug("read(%d) bytes @%Xh", size, self.pos)
        self.seek(self.pos)
        size = int(size)
        # If size is negative
        if size < 0:
            size = 0
            if self.size: size = self.size
        # If size exceeds disk size
        if self.size and self.pos + size > self.size:
            size = self.size - self.pos
        se = int((self.pos + size) / self.blocksize)
        if (self.pos + size) % self.blocksize:
            se += 1
        self.asize = (se - self.si) * self.blocksize  # full sectors to read in
        # If sectors are already cached...
        if self.cache_retrieve():
            logging.debug("%d bytes read from cache", self.asize)
            self.lastsi = self.si
            self.pos += size
            return self.buf[self.so: self.so + size]
        # ...else, read them from disk...
        # if larger than cache limit, read directly into a new buffer
        if self.asize > self.blocksize:
            self.buf = bytearray(self.asize)
            self._file.seek(self.si * self.blocksize)
            logging.debug("reading %d bytes directly from disk @%Xh", self.asize, self._file.tell())
            self._file.readinto(self.buf)
            # Direct read (bypass) DON'T advance lastsi? Or file pointer?
            self.si += self.asize / self.blocksize  # 11.01.2016: fix mkexfat flaw
            self.pos += size
            self.cache_extras += 1
            return self.buf[self.so: self.so + size]
        # ...else, update the cache
        self.cache_readinto()
        self.lastsi = self.si
        self.pos += size
        return self.buf[self.so: self.so + size]

        # self.seek(offset, force=1)
        # self.buf = bytearray(size)
        # self._file.seek(offset)
        # logging.debug("Reading %d bytes from disk @%Xh", size, self._file.tell())
        # self._file.readinto(self.cache[offset:offset+size])
        # self.buf = self.cache[offset:offset+size]
        # return self.buf[0:size]

    def cache_retrieve(self):
        "Retrieve a sector from cache. Returns True if hit, False if missed."
        # If we are retrieving a single block...
        if self.asize == self.blocksize:
            if self.si not in self.cache_table:
                self.cache_misses += 1
                logging.debug("%s: cache_retrieve missed #%d", self, self.si)
                return False
            self.cache_hits += 1
            i = self.cache_table[self.si]
            self.buf = self.cache[i:i + self.asize]
            logging.debug("%s: cache_retrieve hit #%d", self, self.si)
            return True

        # If we are retrieving multiple blocks...
        for i in range(int(self.asize / self.blocksize)):
            # If one block is not cached...
            if self.si + i not in self.cache_table:
                logging.debug("%s: cache_retrieve (multisector) miss-not cached %d", self, self.si + i)
                self.cache_misses += 1
                continue
            # If one block is dirty, first flush it...
            if self.si + i in self.cache_dirties:
                logging.debug("%s: cache_retrieve (multisector) flush %d", self, self.si + i)
                self.cache_flush(self.si + i)
                logging.debug("%s: seeking back @%Xh after flush", self, self.pos)
                self.seek(self.pos)
                continue
        return False  # consider a miss

    def cache_readinto(self):
        # If we should read beyond the cache's end...
        if self.cache_index + self.asize > len(self.cache):
            # Free space, flushing dirty sectors & updating cache index
            self.cache_flush()
            self.cache_index = 0
            self.seek(self.pos)
        pos = self.cache_index
        # ~ log("loading disk sector #%d into cache[%d] from offset %Xh", self.si, pos/512, self._file.tell())
        logging.debug("loading disk sector #%d into cache[%d]", self.si, pos / 512)
        self._file.readinto(self.cache[pos:pos + self.asize])
        self.buf = self.cache[pos:pos + self.asize]
        # ~ if self.si == 50900:
        # ~ log("Loaded sector #50900:\n%s", hexdump.hexdump(self.cache[pos:pos+self.asize],'return'))
        self.cache_index += self.asize
        # Update dictionary of cached sectors and their position
        # Invalidate accordingly if we are recycling pool from zero?
        k = self.si
        v = pos
        # If a previously cached sector is pointing to the same buffer,
        # unlink it
        if v in self.cache_tableR:
            del self.cache_table[self.cache_tableR[v]]
        self.cache_table[k] = v
        self.cache_tableR[v] = k
        return pos

    def cache_stats(self):
        logging.debug("Cache items/hits/misses: %d/%d/%d", len(self.cache_table), self.cache_hits,
                          self.cache_misses)

    def cache_flush(self, sector=None):
        self.cache_stats()
        if not self.cache_dirties:
            # 21.04.17: must ANYWAY reset (read-only) cache, or higher cached slots could get silently overwritten!
            logging.debug("resetting cache (no dirty sectors)")
            self.cache_table = {}
            self.cache_tableR = {}
            return
        if sector != None:  # assume it is called by cache_retrieve only, with the right sector #
            self._file.seek(sector * self.blocksize)
            i = self.cache_table[sector]
            self._file.write(self.cache[i:i + self.blocksize])
            del self.cache_dirties[sector]
            logging.debug("%s: dirty sector #%d committed to disk from cache[%d]", self, sector, i / 512)
            return
            logging.debug("%s: committing %d dirty sectors to disk", self, len(self.cache_dirties))
        for sec in sorted(self.cache_dirties):
            self._file.seek(sec * self.blocksize)
            try:
                i = self.cache_table[sec]
                self._file.write(self.cache[i:i + self.blocksize])
            except:
                logging.debug("ERROR! Sector %d in cache_dirties not in cache_table!", sec)
                if sec in self.cache_tableR.values():
                    logging.debug("(but sector %d is in cache_tableR)", sec)
                else:
                    logging.debug("(and sector %d is neither in cache_tableR)", sec)
                continue
        self.cache_dirties = {}
        self.cache_table = {}
        self.cache_tableR = {}

    def tell(self):
        return self.pos
