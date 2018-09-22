# Helper file for creating new, clear image file

import argparse

def createImageFile(filename, size = 256 << 20):

    # Creates empty file with given filename and size
    f = open(filename, "wb")
    f.seek(size)
    f.truncate()
    f.close()

if __name__ == "__main__":
    # execute only if run as a script
    parser = argparse.ArgumentParser(description="Create blank image file")
    parser.add_argument("filename", help="filename of blank image file")
    parser.add_argument("size", help="size of image file", type=int)
    parser.add_argument("sizetype", help="KB (0), MB (1) or GB (3)", type=int, choices=[0, 1, 2])
    args = parser.parse_args()

    size = 0
    if args.sizetype == 0:
        size = args.size << 10 # in KB
    elif args.sizetype == 1:
        size = args.size << 20 # in MB
    elif args.sizetype == 2:
        size = args.size << 30 # in GB
    else:
        size = args.size << 20

    createImageFile(args.filename, size)