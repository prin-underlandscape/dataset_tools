# Takes a list of dataset names, possibly as paths to a filename, and,
# for each of them, uploads the generated uMap to the uMap referenced
# in the "umapKey" property in the dataset. The uMap map must already
# exist, and the "umapKey" property must be correctly set (using Off).
# New features properties are computed to be included in the feature
# description, like for dataset specific uMap maps. 
# After generating the uMap file, the script uploads the map to uMap.
# Since an API service is not available, the upload is implemented
# mimiking the user operation on uMap GUI with Selenium. Since the
# references inside the GUI change frequently, the script must be
# likely revised in the part that uses the Selenium library (mostly in
# the "umap_common" library).
# Debugged, tested and used in April 2025  

from os.path import basename, splitext
import time
import json
import math
from copy import deepcopy
from functools import reduce
from urllib.request import urlretrieve, urlopen

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import sys
sys.path.append('./libs')
from colprint import emphprint, failprint, warnprint
from umap_common import tag_options, dataset_template, umap_login, umap_sync

def generate_umap(geojson, dataset_name, umap_file):
  rn = geojson["properties"]["Nome"]
  try:
    umap=deepcopy(dataset_template)
    print("\u2022 Generazione del file umap")
    allowed_types = list(map(lambda l: l["_umap_options"]["name"], umap["layers"]))
# compute map center        
    points = list( [ feature["geometry"]["coordinates"] for feature in filter(lambda f: ( f["geometry"]["type"] == "Point" ), geojson["features"]) ] ) 
    ls = [ el for LineString in filter(lambda f: ( f["geometry"]["type"] == "LineString" ), geojson["features"]) for el in LineString["geometry"]["coordinates"] ]  
    mlslist = [ el for LineString in filter(lambda f: ( f["geometry"]["type"] == "MultiLineString" ), geojson["features"]) for el in LineString["geometry"]["coordinates"] ]  
    mls = [ el for Nested in mlslist for el in Nested ]
    points.extend(ls)
    points.extend(mls)
    c1=[item[0] for item in points]
    c2=[item[1] for item in points]
    
    center_long = reduce(lambda a, b: a + b, c1) / len(c1)
    center_lat = reduce(lambda a, b: a + b, c2) / len(c2) 
    center=[center_long,center_lat]
    umap["geometry"] = {
      "type": "Point",
      "coordinates": center
    }
# compute zoom factor
    if len(points) > 1:
      def zoom(win_size, map_size):
        return math.floor(17 - math.log2(win_size*map_size/1194))
      w = 1.2*(2*(max([abs(center_long - x) for x in c1])) * 80)  # dimensioni orizzontali in km + 20%
      w_zoom = zoom(1600,w)
      h = 1.2*(2*(max([abs(center_lat - x) for x in c2])) * 111)  # dimensioni orizzontali in km + 20%
  #    h = 1.2*((max(c2)-min(c2)) * 111) # dimensioni verticali in km + 20%
      h_zoom = zoom(900,h)
      print (f'{w} {h} {w_zoom} {h_zoom}')
      print(min([w_zoom, h_zoom,20]))
      umap['properties']['zoom'] = min([w_zoom, h_zoom, 21])
    else:
      umap['properties']['zoom'] = 19
    
# Imposta il nome della mappa         
    umap["properties"]["name"] = rn

    for feature in geojson["features"]:
      try:
        if feature["properties"]["ulsp_type"] in allowed_types:
          feature["properties"]["_umap_options"] = {"popupTemplate": "Default"}
          feature['properties']['Dataset'] = dataset_name
          feature["properties"]["GitHubURL"] = "https://github.com/prin-underlandscape/"+rn
          feature["properties"]["GPXDownload"] = "https://github.com/prin-underlandscape/"+rn+"/blob/main/"+rn+".gpx"
          if "Link" in geojson["properties"] and geojson["properties"]["Link"] != "":
#            print(geojson["properties"]["WebPageURL"])
            feature["properties"]["Link"] = geojson["properties"]["Link"]
          else:
            feature["properties"]["Link"] = "https://sites.google.com/view/prin-underlandscape/link-non-disponibile"
          if feature["properties"]["ulsp_type"] in ["POI","Risorsa"] and feature["properties"]["Tag primario"] != "":
            print(feature["properties"]["Tag primario"])
            feature["properties"]["_umap_options"].update(tag_options[feature["properties"]["Tag primario"]])
      # Find layer for feature
          layers = list(filter(lambda l: l["_umap_options"]["name"] == feature["properties"]["ulsp_type"], umap["layers"]))
          if len(layers) != 1:
            failprint("Wrong ulsp format")
          layers[0]["features"].append(feature);
        else:
          raise KeyError("Wrong ulsp_type")
      except KeyError as ke:
        failprint("   Feature mal formattata: non trattata ("+ke.args[0]+")")
        continue
    with open(umap_file, 'w', encoding='utf-8') as f:
      json.dump(umap, f, ensure_ascii=False, indent=2)
  except KeyError as ke:
    failprint("   GeoJSON mal formattato: non trattato ("+ke.args[0]+")")
    return False

if len(sys.argv) < 2:
  exit("Bisogna passare i dataset da sincronizzare")

# Caricamento del file di configurazione
with open("config.json") as json_data:
  config = json.load(json_data)

# Browser configuration
chrome_service = Service(executable_path=config["webdriver"])
driver = webdriver.Chrome(service=chrome_service)
driver.set_window_size(1600,900)
driver.implicitly_wait(60) # useful to wait for login


umap_file='./dataset.umap'
umap_login(driver, config)
# Enumera gli argomenti e aggiorna
for fn in sys.argv[1:]:
  try:
    dataset_name = splitext(basename(fn))[0]
  # Attende di accedere alla dashboard	
    driver.find_element(By.PARTIAL_LINK_TEXT, "Dashboard") # Attende di accedere alla dashboard
    print(f"Sincronizzo {dataset_name}") 
  # Download dataset geojsos and extract URL of umap map
    with urlopen(f"https://raw.githubusercontent.com/prin-underlandscape/Master/main/{dataset_name}.geojson") as content:
      geojson = json.load(content)
    generate_umap(geojson, dataset_name, umap_file)
    umap_sync(driver, geojson["properties"]["umapKey"], umap_file)
  except KeyError as error:
    print("C'è stato un problema:", error)
	 
