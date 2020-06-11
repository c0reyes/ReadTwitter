from geopy.geocoders import Nominatim
import time
import getopt
import sys

def usage():
    print("options: ")
    print("\t-f | --file <filename>")
    
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:", ["file="])
        if len(opts) == 0:
            usage()
            sys.exit()
    except getopt.GetoptError as err:
        usage()
        sys.exit(2)

    file = None

    for o, a in opts:
        if o in ("-f", "--file"):
            file = a
        else:
            assert False, "unhandled option"

    geolocator = Nominatim(user_agent="Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0")

    with open(file, 'r', encoding='utf-8') as file:
        for line in file:
            location = geolocator.geocode(line, timeout=30)
            if location:
                print(location)
                print('{}|{},{}'.format(line.strip(), location.latitude, location.longitude))
                time.sleep(0.5)
