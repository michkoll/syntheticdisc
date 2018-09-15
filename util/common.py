import struct
from ctypes import create_string_buffer


def common_getattr(c, name):
	"Decodifica e salva un attributo in base al layout di classe"
	i = c._vk[name]
	fmt = c._kv[i][1]
	cnt = struct.unpack_from(fmt, c._buf, i + c._i)[0]
	setattr(c, name, cnt)
	return cnt

def class2str(c, s):
	"Enumera in tabella nomi e valori dal layout di una classe"
	keys = c._kv.keys()
	keys.sort()
	for key in keys:
		o = c._kv[key][0]
		v = getattr(c, o)
		if type(v) in (type(0), type(0)):
			v = hex(v)
		s += '%x: %s = %s\n' % (key, o, v)
	return s