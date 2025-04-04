import os
import shutil
import sys
sys.path.append('./libs')
import pygit2
import json
import random
import time
import re
from os.path import abspath

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

def sync(umap_url, umap_file):
  print("Accedo alla mappa")
  # Accede alla mappa umap online
  driver.get(umap_url)
  # Attende l'abilitazione della modifica della mappa e la seleziona
  driver.find_element(By.CSS_SELECTOR, ".edit-enable.leaflet-control > button").click() 
  print("Modifica abilitata!")
  # Preme il bottone rotella per modificare le impostazioni della mappa
  driver.find_element(By.CSS_SELECTOR, '[data-ref="settings"]').click()
  # Preme "Azioni avanzate"
  driver.find_element(By.CSS_SELECTOR, "details:nth-child(11) > summary").click()
  # Preme "Vuota"
  driver.find_element(By.CSS_SELECTOR, '[data-ref="clear"]').click()
  # Preme "Rimuovi tutti i layer" (importante)
  driver.find_element(By.CSS_SELECTOR, '[data-ref="empty"]').click()
  # Chiude il pannello "Rotella"
  driver.find_element(By.CSS_SELECTOR, ".buttons:nth-child(1) .icon-close").click()
  # Seleziona il tasto di caricamento "Freccia in alto"
  print("Rimozione dei livelli completata")
  driver.find_element(By.CSS_SELECTOR, '[data-ref="import"]').click()
  # Carica i dati (ma si potrebbero anche copiare direttamente nel textbox
  # senza memorizzarlo in un file
  time.sleep(1) # delay per lasciare che tutto vada...
  upload_file = abspath(umap_file)
  file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
  file_input.send_keys(upload_file)
  # Preme pulsante di importazione
  driver.find_element(By.NAME, "submit").click()
  print("Nuova mappa importata")
  # Chiude il pannello di caricamento
  driver.find_element(By.CSS_SELECTOR, ".buttons:nth-child(1) .icon-close").click()
  # Salva la nuova mappa
  driver.find_element(By.CSS_SELECTOR, ".edit-save.button.round").click()
  # Chiude il pannello di editing (importante: aspettando che il salvataggio termini)
  print("Nuova mappa salvata")
  driver.find_element(By.CSS_SELECTOR, ".edit-disable.round").click()
  print("=== Concluso (tra 10 secondi chiudo)")
  # Attesa per consentire all'operatore di osservare il risultato
  time.sleep(10)
  driver.get("https://umap.openstreetmap.fr/")	

with open("config.json") as json_data:
  config = json.load(json_data)
  
# Aggiunge alle descrizioni una riga per la mappa uMap (assente
# nelle mappe uMap)
for layer in summary["layers"]:
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
        filter(lambda l: l["_umap_options"]["name"] == ulspType, summary["layers"])
      )
# Aggancia la nuova feature al livello
      layer["features"].append(f)
      print(f'{ulspType} - {f["properties"]["name"]}')
    except Exception as e:
      print(f'Error: {e}')

with open(f'../{config["summary_filename"]}', 'w', encoding='utf-8') as f:  
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
driver.find_element(By.CSS_SELECTOR, '[title="Openstreetmap-Oauth2"]').click()
# Autenticazione su OSM
try:
  driver.find_element(By.ID, "username").click()
  driver.find_element(By.ID, "username").send_keys(config["osm_username"])
  driver.find_element(By.ID, "password").click()
  driver.find_element(By.ID, "password").send_keys(config["osm_password"])
  driver.find_element(By.NAME, "commit").click()
except NameError as e:
  print("Credenziali non definite: login manuale")
 
try:
# Attende di accedere alla dashboard	
  driver.find_element(By.PARTIAL_LINK_TEXT, "Dashboard") # Attende di accedere alla dashboard
  print(f"Sincronizzo la mappa sommario") 
  sync(config["summary_URL"],f'../{config["summary_filename"]}')
except KeyError as error:
  print("C'è stato un problema:", error)
    
os.chdir('..')
shutil.rmtree(config['master_repo'], ignore_errors=True)
