import struct
from ctypes import create_string_buffer


def common_getattr(c, name):
	'''
	Decodes parameter layout to class member variables

	:param c: Class object
	:type c: object
	:param name: Name of paramter
	:type name: str
	:return:
	:rtype:
	'''
	# Get offset for parameter
	i = c._vk[name]
	# Get format for parameter
	fmt = c._kv[i][1]
	# Unpack parameter value as bytearray from buffer
	cnt = struct.unpack_from(fmt, c._buf, i + c._i)[0]
	# Sets attribute to object
	setattr(c, name, cnt)
	return cnt

def class2str(c, s):
	"Enumera in tabella nomi e valori dal layout di una classe"
	keys = list(c._kv.keys())
	keys.sort()
	for key in keys:
		o = c._kv[key][0]
		v = getattr(c, o)
		if type(v) in (type(0), type(0)):
			v = hex(v)
		s += '%x: %s = %s\n' % (key, o, v)
	return s