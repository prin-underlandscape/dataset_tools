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
import json

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
            fingerprintFromURL(f['properties']['Foto'])
          ) if 'Foto' in f['properties']
          else 
          ( f['properties']['Titolo'].translate(dict.fromkeys(map(ord, '\\/'), "-")),
            f['properties']['Foto accesso'],
            f['properties']['ulsp_type'],
            fingerprintFromURL(f['properties']['Foto accesso'])
          ) if 'Foto accesso' in f['properties']
          else (f['properties']['Titolo'].translate(dict.fromkeys(map(ord, '\\/'), "-")),"",f['properties']['ulsp_type'],""), 
          geojson['features']))
          
missing = list(filter(lambda x: x[1] == "", l) )

l = list(filter(lambda x: x not in missing, l) )

present = list(filter(lambda x: x[0] + "-" + x[3] + ".jpg" in os.listdir(wd), l))

l = list(filter(lambda x: x not in present, l) )

print("Immagini mancanti:")
pprint(list(map(lambda x: x[0]+"("+x[2]+")", missing)))

print("Immagini già scaricate:")
pprint(list(map(lambda x: x[0]+"-"+x[3], present)))

print("Immagini da scaricare:")
pprint(list(map(lambda x: x[0]+"-"+x[3], l)))

print("====")
# Produce coppie URL, filename destinazione
dl = list(map(lambda x: (x[1], os.path.join(wd, x[0]+"-"+x[3]+".jpg")), l))

for download in dl:
  print(download[1])
  with request.urlopen(download[0]) as response:
    image=Image.open(io.BytesIO(response.read()))
    image.save(download[1])

