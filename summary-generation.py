import os
import shutil
import sys
sys.path.append('./libs')
import pygit2
import json
import random
import time
import re

from colprint import emphprint, failprint, warnprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service

from upload_list import UploadList
from umap_common import summary
#import upload_list

def clone(repoName):
  if os.path.isdir(repoName):
    warnprint("Please remove "+repoName+" folder")
    exit()
  return pygit2.clone_repository("https://github.com/prin-underlandscape/"+repoName,repoName)

#with open("dataset-sync.config") as json_data:
#  config = json.load(json_data)
with open("config.json") as json_data:
  config = json.load(json_data)
  
emphprint("Clono il repository Master da github")
clone(config['master_repo'])
os.chdir(config['master_repo'])

ul = UploadList() 
#generate_summary(ul)    # genera l'umap di sommario

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
  if re.search("^ITN.*", datasetName): continue
  if re.search("^Itinerario.*", datasetName): continue
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
    f['properties']['Dataset'] = os.path.splitext(fn)[0]
# Imposta il link github
    f['properties']['Link GitHub'] = 'https://github.com/prin-underlandscape/'+os.path.splitext(fn)[0]
# Imposta il link per il download
    f["properties"]["GPXDownload"] = "https://raw.githubusercontent.com/prin-underlandscape/"+datasetName+"/main/"+datasetName+".gpx"
    try:
# Imposta la URL della mappa uMap
      f['properties']['umapURL'] = geojson['properties']['umapKey']
# Imposta la URL della pagina decicata nel sito Underlandscape
      f['properties']['WebPageURL'] = geojson['properties']['WebPageURL']
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
        filter(lambda l: l["_umap_options"]["name"] == ulspType, summary["layers"])
      )
# Aggancia la nuova feature al livello
      layer["features"].append(f)
      print(f'{ulspType} - {f["properties"]["name"]}')
    except Exception as e:
      print(f'Error: {e}')

with open(config["summary_filename"], 'w', encoding='utf-8') as f:  
  json.dump(summary, f , ensure_ascii=False, indent=2)

ul.log(config["summary_filename"], config["summary_URL"])

# Browser configuration
chrome_service = Service(executable_path=config["webdriver"])
driver = webdriver.Chrome(service=chrome_service)
driver.set_window_size(1600,900)
driver.implicitly_wait(60) # useful to wait for login
# Start from login page
driver.get("https://umap.openstreetmap.fr/it/login/")
# Seleziona oauth2 con osm
driver.find_element(By.CSS_SELECTOR, ".login-openstreetmap-oauth2").click()
# Autenticazione su OSM
try:
  driver.find_element(By.ID, "username").click()
  driver.find_element(By.ID, "username").send_keys(config["osm_username"])
  driver.find_element(By.ID, "password").click()
  driver.find_element(By.ID, "password").send_keys(config["osm_password"])
  driver.find_element(By.NAME, "commit").click()
except NameError as e:
  print("Credenziali non definite: login manuale")
# Attende di accedere alla dashboard	
  driver.find_element(By.PARTIAL_LINK_TEXT, "Dashboard")
# Accede alla mappa Sommario
driver.get(config["summary_URL"])
# Attende l'abilitazione della modifica della mappa e la seleziona
driver.find_element(By.CSS_SELECTOR, ".leaflet-control-edit-enable > button").click()
# Preme il bottone rotella per modificare le impostazioni della mappa
driver.find_element(By.CSS_SELECTOR, ".update-map-settings").click()
# Preme "Azioni avanzate"
driver.find_element(By.CSS_SELECTOR, "details:nth-child(11) > summary").click()
# Preme "Clear data"
driver.find_element(By.CSS_SELECTOR, ".umap-empty:nth-child(2)").click()
# Preme "Rimuovi tutti i layer" (importante)
driver.find_element(By.CSS_SELECTOR, ".button:nth-child(3)").click()
# Chiude il pannello "Rotella"
driver.find_element(By.CSS_SELECTOR, ".buttons:nth-child(1) .icon-close").click()
# Seleziona il tasto di caricamento "Freccia in alto"
driver.find_element(By.CSS_SELECTOR, ".upload-data").click()
# Carica i dati (ma si potrebbero anche copiare direttamente nel textbox
# senza memorizzarlo in un file
upload_file = os.path.abspath(config["summary_filename"])
file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
file_input.send_keys(upload_file)
# Preme pulsante di importazione
driver.find_element(By.NAME, "submit").click()
# Chiude il pannello di caricamento
driver.find_element(By.CSS_SELECTOR, ".buttons:nth-child(1) .icon-close").click()
# Salva la nuova mappa
driver.find_element(By.CSS_SELECTOR, ".leaflet-control-edit-save").click()
# Chiude il pannello di editing (importante: aspettando che il salvataggio termini)
driver.find_element(By.CSS_SELECTOR, ".leaflet-control-edit-disable").click()
print("=== Concluso")
# Attesa per consentire all'operatore di osservare il risultato
time.sleep(10)

os.chdir('..')
shutil.rmtree(config['master_repo'], ignore_errors=True)
