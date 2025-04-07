# Generates the summary umap, by collecting all the files with ".geojson"
# extension in the Master repository, and scanning all features contained
# therein. No arguments needed.
# New features properties are computed to be included in the feature
# description, like for dataset specific uMap maps. In addition, a line
# for the link to the specific map is added to the feature description
# in the map.
# After generating the uMap file, the script uploads the map to uMap.
# Since an API service is not available, the upload is implemented
# mimiking the user operation on uMap GUI with Selenium. Since the
# references inside the GUI change frequently, the script must be
# likely revised in the part that uses the Selenium library (mostly in
# the "umap_common" library).
# Debugged, tested and used in April 2025  
import os
import shutil
import pygit2
import json
import random
import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import sys
sys.path.append('./libs')
from colprint import emphprint, failprint, warnprint
from upload_list import UploadList
from umap_common import tag_options, dataset_template, umap_login, umap_sync

def clone(repoName):
  if os.path.isdir(repoName):
    warnprint("Please remove "+repoName+" folder")
    exit()
  return pygit2.clone_repository("https://github.com/prin-underlandscape/"+repoName,repoName)

with open("config.json") as json_data:
  config = json.load(json_data)
  
# Aggiunge alle descrizioni una riga per la mappa uMap (assente
# nelle mappe uMap)
for layer in dataset_template["layers"]:
	layer["_umap_options"]["popupContentTemplate"] = \
		layer["_umap_options"]["popupContentTemplate"].\
		replace("*{Dataset}*", "*{Dataset}*\nLa mappa relativa al dataset è [[{uMapURL}|qui]]")

emphprint("Clono il repository Master da github")
clone(config['master_repo'])
os.chdir(config['master_repo'])

ul = UploadList()

emphprint("Generazione della mappa umap di sommario")
# filtra i file con estensione geojson
geojson_files = list(
  filter(lambda fn: os.path.splitext(fn)[1] == ".geojson", os.listdir(".")) 
)
#print(geojson_files)

# Esamina tutti i dataset
for fn in geojson_files:
  datasetName = os.path.splitext(fn)[0]
# Esclude dal sommario itinerari e test
#  if re.search("^ITN.*", datasetName): continue
#  if re.search("^Itinerario.*", datasetName): continue
  if re.search("^test.*", datasetName): continue
  emphprint("  Includo il dataset " + datasetName)
  with open(fn) as json_data:
    geojson = json.load(json_data)
# la variabile geojson è il dataset in geojson
# generazione del colore casuale
  random.seed(sum(map(ord,fn)))
  randomColor = hex(random.randint(0,16777215)).replace('0x','#')

# Esamina tutte le features nel dataset
  for f in geojson['features']:
# acquisisce il tipo della feature
    ulspType = f['properties']['ulsp_type'] 	  
# Imposta il nome del dataset
    f['properties']['Dataset'] = datasetName
# Imposta il link github
    f['properties']['GitHubURL'] = 'https://github.com/prin-underlandscape/' + datasetName
# Imposta il link per il download
    f["properties"]["GPXDownload"] = "https://raw.githubusercontent.com/prin-underlandscape/"+datasetName+"/main/"+datasetName+".gpx"
    try:
# Imposta la URL della mappa uMap
      f['properties']['uMapURL'] = geojson['properties']['umapKey']
# Imposta la URL della pagina dedicata nel sito Underlandscape
      if geojson['properties']['WebPageURL']:
        f['properties']['ULSPLink'] = geojson['properties']['WebPageURL']
      else:
        f['properties']['ULSPLink'] = config['no_weburl']
    except KeyError as e:
      print(f'Error: {e}')
# Imposta il "name" (comodità...)
    f['properties']['name'] = f['properties']['Titolo']
# Imposta le umap_options dipendenti dal tipo della feature
    f['properties']['_umap_options']={}
    if ulspType == 'Sito':
      f['properties']['_umap_options'] = {
        'iconClass': 'Ball',
        'color': '#800101'
      }
    elif ulspType == 'POI':
      f['properties']['_umap_options'] = {
        'iconClass': 'Circle',
        'color': randomColor
      }
    elif ulspType == 'Percorso':
      f['properties']['_umap_options'] = {
        "weight": 9,
        'color': randomColor
      }
    elif ulspType == 'QRtag':
      f['properties']['_umap_options'] = {
      'iconClass': 'Drop',
      'color': randomColor,
      'iconUrl': "/uploads/pictogram/guidepost.svg"
      }
    elif ulspType == 'Risorsa':
      f['properties']['_umap_options'] = {
        'iconClass': 'Circle',
        'color': randomColor
      }
    elif ulspType == 'Itinerario':
      f['properties']['_umap_options'] = {
        "weight": 9,
        'color': randomColor
      }
    else:
      raise KeyError("Tipo di feature non prevista")
# Impostazione _map_options comuni      
    f['properties']['_umap_options']['popupTemplate'] = "Default"
    try:
# Seleziona il layer con il nome uguale al tipo della nuova feature
      layer=next(
        filter(lambda l: l["_umap_options"]["name"] == ulspType, dataset_template["layers"])
      )
# Aggancia la nuova feature al livello
      layer["features"].append(f)
      print(f'{ulspType} - {f["properties"]["name"]}')
    except Exception as e:
      print(f'Error: {e}')

with open(f'../{config["summary_filename"]}', 'w', encoding='utf-8') as f:  
  json.dump(dataset_template, f , ensure_ascii=False, indent=2)

ul.log(config["summary_filename"], config["summary_URL"])

# Browser configuration
chrome_service = Service(executable_path=config["webdriver"])
driver = webdriver.Chrome(service=chrome_service)
driver.set_window_size(1600,900)
driver.implicitly_wait(60) # useful to wait for login

umap_login(driver, config)
try:
  print(f"Sincronizzo la mappa sommario")
  umap_sync(driver, config["summary_URL"],f'../{config["summary_filename"]}')
except KeyError as error:
  print("C'è stato un problema:", error)
    
os.chdir('..')
shutil.rmtree(config['master_repo'], ignore_errors=True)
