import urllib.request
import io
import os
import sys
import shutil
import pathlib
from urllib.parse import urlparse
import json
# dependencies
from PIL import Image, ImageDraw, ImageFont
import qrcode
import datetime
import random

# https://github.com/PyGithub/PyGithub
# more: https://stackoverflow.com/questions/49458329/create-clone-and-push-to-github-repo-using-pygithub-and-pygit2
from github import Github
from github import Auth
import pygit2

from pprint import pprint

import sys 
sys.path.append('./libs')
import my_git
import colprint

summary = {
    "type": "umap",
    "geometry": {
        "type": "Point",
        "coordinates": [
            10.5266,
            44.0960
        ]
    },
    "properties": {
        "name": "Sommario",
        "zoom": 11,
        "easing": False,
        "licence": "",
        "miniMap": False,
#        "overlay": null,
        "slideshow": {

        },
        "tilelayer": {
          "tms": False,
          "name": "OSM OpenTopoMap",
          "maxZoom": 20,
          "minZoom": 1,
          "attribution": "Kartendaten: © [[https://openstreetmap.org/copyright|OpenStreetMap]]-Mitwirkende, [[http://viewfinderpanoramas.org/|SRTM]] | Kartendarstellung: © [[https://opentopomap.org/|OpenTopoMap]]    ([[https://creativecommons.org/licenses/by-sa/3.0/|CC-BY-SA]])",
          "url_template": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
        },
        "captionBar": False,
        "description": "",
        "limitBounds": {

        },
        "moreControl": True,
        "zoomControl": True,
        "captionMenus": True,
        "embedControl": True,
        "scaleControl": True,
        "searchControl": True,
        "scrollWheelZoom": True,
        "datalayersControl": True,
        "fullscreenControl": True,
        "displayPopupFooter": False,
        "permanentCreditBackground": True
    },
    "layers": []
}

def grab_image(url,filename):
  with urllib.request.urlopen(url) as response:
    image=Image.open(io.BytesIO(response.read()))
    image.thumbnail((config["vignette_size"],config["vignette_size"]))
    image.save(filename)

#grab_image(image_url,"image.jpg")

def cleanup():
  # Esce dal workspace
  os.chdir('..')
  shutil.rmtree(config['masterName'], ignore_errors=True)
  
def vignetteNameFromURL(url):
  if ( url.netloc == 'i.postimg.cc' ):
    key = url.path.split('/')[1]
    return "/vignettes/" + key + ".jpg"
  elif ( url.netloc == 'www.gaiagps.com' ):
    key = url.path.split('/')[4]
    return "/vignettes/" + key + ".jpg"
  elif ( url.netloc == 'underlandscape.cfs.unipi.it' ):
    key = url.path.split('/')[6]
    return "/vignettes/" + key + ".jpg"
  else:
    if ( url.netloc != "" ):
      raise("Invalid image URL")
    else:
      raise("No image URL")

# Read configuration and assets
with open("dataset-sync.config") as json_data:
  config = json.load(json_data)
with open("umapTemplate.json") as json_data:
  umapTemplate = json.load(json_data)
  
logo = Image.open("logoEle_v2.2_small.png").convert("RGBA")

colprint.emphprint("Clono il repository Master da github")
my_git.clone(config['masterName'])
os.chdir(config['masterName'])

# filtra i file con estensione geojson
geojson_files = list(
              filter(lambda fn: os.path.splitext(fn)[1] == ".geojson", os.listdir(".")) 
            )
#print(geojson_files)

for fn in geojson_files:
  with open(fn) as json_data:
      geojson = json.load(json_data)
  random.seed(sum(map(ord,fn)))
  color = hex(random.randint(0,16777215)).replace('0x','#');
  geojson["_umap_options"] = {
    "name": os.path.splitext(fn)[0],
    "editMode": "advanced",
    "browsable": True,
    "inCaption": True,
    "remoteData": {},
    "displayOnLoad": True,
    "iconClass": "Drop",
    "color": color,
    "popupShape": "Large",
    "popupTemplate": "Table"
  }
  
  for f in geojson['features']:
    f['properties']['Dataset'] = os.path.splitext(fn)[0]
# Compatibilità quando mancano le properties del dataset
    if 'properties' in geojson:
      f['properties']['Mappa'] = geojson['properties']['umapKey']
    if '_umap_options' not in f['properties']: f['properties']['_umap_options']={}
    if f['properties']['ulsp_type'] == 'Sito':
      f['properties']['_umap_options']['iconClass'] = 'Ball'
    elif f['properties']['ulsp_type'] == 'POI':
      f['properties']['_umap_options']['iconClass'] = 'Circle'
    elif f['properties']['ulsp_type'] == 'QRtag':
      f['properties']['_umap_options']['iconClass'] = 'Drop'
      f['properties']['_umap_options']['iconUrl']= "/uploads/pictogram/guidepost.svg"
#  print(color)
  summary['layers'].append(geojson)

with open("../summary.umap", 'w', encoding='utf-8') as f:  
  json.dump(summary, f , ensure_ascii=False, indent=2)
