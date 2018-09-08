imagesize = 256 << 20 # in MB
#imagesize = 5 << 30 # in GB

imagename = "../tests/images/Testimage.img"

f = open(imagename, "wb")
f.seek(imagesize)
f.truncate()
f.close()