from geopy.geocoders import Nominatim
import time

if __name__ == '__main__':
    geolocator = Nominatim(user_agent="Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0")

    with open('geo.txt', 'r', encoding='utf-8') as file:
        for line in file:
            location = geolocator.geocode(line, timeout=30)
            if location:
                print(location)
                print('{}|{},{}'.format(line.strip(), location.latitude, location.longitude))
                time.sleep(0.5)