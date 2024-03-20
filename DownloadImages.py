###
# Dato un geojson in formato ulsp scarica tutte le "Foto" e "Foto accesso" collegate
###

import io
import os
import sys
import shutil
import pathlib
from urllib import parse, request
from PIL import Image
import piexif
import json
import datetime
import tzlocal
import iso8601

from pprint import pprint

def fingerprintFromURL(fotourl):
  url = parse.urlparse(fotourl)
  if ( url.netloc == 'i.postimg.cc' ):
    return url.path.split('/')[1][0:4]
  elif ( url.netloc == 'www.gaiagps.com' ):
    return url.path.split('/')[4][0:4]
  elif ( url.netloc == 'underlandscape.cfs.unipi.it' ):
    return url.path.split('/')[6][0:4]
  else:
    raise("Invalid image URL")

def exifFromFeature(feature):
  def deg_to_dms(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60000)
    return ((d, 1), (m, 1), (s, 1000))

  exif_dict = {"GPS": {}, 'Exif': {}, '0th': {} }

  if feature['properties']['ulsp_type'] == 'POI':
#aware_dt = iso8601.parse_date("2010-10-30T17:21:12Z") # some aware datetime object
    timestamp_utc = iso8601.parse_date(feature['properties']['Data']+" "+feature['properties']['Ora'])
    local_timezone = tzlocal.get_localzone()
    timestamp = str(timestamp_utc.astimezone(local_timezone).replace(tzinfo=None))
    print(timestamp)
    altitudine = feature['properties']['Altitudine']
    (longitudine,latitudine) = feature['geometry']['coordinates']
    exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = (altitudine, 1)
    exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = 'N'
    exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = deg_to_dms(latitudine)
    exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = 'E'
    exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = deg_to_dms(longitudine)
    exif_dict['0th'][piexif.ImageIFD.DateTime] = timestamp
    exif_dict['0th'][piexif.ImageIFD.ImageDescription] = feature['properties']['Titolo']
    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = timestamp
    exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = timestamp
    print(exif_dict)
    
  return exif_dict
  

# geojson content
with open(sys.argv[1]) as json_data:
  geojson = json.load(json_data)
# Working directory  
wd = os.path.dirname(sys.argv[1])

l = list(map(
  lambda f: 
          ( f['properties']['Titolo'].translate(dict.fromkeys(map(ord, '\\/'), "-")),
            f['properties']['Foto'],
            f['properties']['ulsp_type'],
            fingerprintFromURL(f['properties']['Foto']),
            exifFromFeature(f)
          ) if 'Foto' in f['properties']
          else 
          ( f['properties']['Titolo'].translate(dict.fromkeys(map(ord, '\\/'), "-")),
            f['properties']['Foto accesso'],
            f['properties']['ulsp_type'],
            fingerprintFromURL(f['properties']['Foto accesso']),
            exifFromFeature(f)
          ) if 'Foto accesso' in f['properties']
          else 
          ( f['properties']['Titolo'].translate(dict.fromkeys(map(ord, '\\/'), "-")),
            "",
            f['properties']['ulsp_type'],
            "" , 
            {}), 
          geojson['features']))
          
missing = list(filter(lambda x: x[1] == "", l) )

l = list(filter(lambda x: x not in missing, l) )

present = list(filter(lambda x: x[0] + "-" + x[3] + ".jpg" in os.listdir(wd), l))
#present = () # Forza scaricamento anche di quelle già presenti

l = list(filter(lambda x: x not in present, l) )

print("Immagini mancanti:")
pprint(list(map(lambda x: x[0]+"("+x[2]+")", missing)))

print("Immagini già scaricate:")
pprint(list(map(lambda x: x[0]+"-"+x[3], present)))

print("Immagini da scaricare:")
pprint(list(map(lambda x: x[0]+"-"+x[3], l)))

print("====")
# Produce 3-ple URL, filename destinazione, exif
dl = list(map(lambda x: (x[1], os.path.join(wd, x[0]+"-"+x[3]+".jpg"),x[4]), l))

for download in dl:
  print(download[1])
  with request.urlopen(download[0]) as response:
    image=Image.open(io.BytesIO(response.read()))
    image.save(download[1], exif=piexif.dump(download[2]) )

