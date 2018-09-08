import struct
from ctypes import create_string_buffer


def common_getattr(c, name):
	"Decodifica e salva un attributo in base al layout di classe"
	buffer = create_string_buffer(8)
	i = c._vk[name]
	fmt = c._kv[i][1]
	cnt = struct.unpack_from(fmt, buffer)
	setattr(c, name,  cnt)
	return cnt