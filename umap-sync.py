import sys
sys.path.append('./libs')
from os.path import basename, splitext, abspath
import time
import json
import math
from copy import deepcopy
from functools import reduce
from urllib.request import urlretrieve, urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys

from colprint import emphprint, failprint, warnprint
from umap_common import tag_options, umap_template

def generate_umap(geojson):
  rn = geojson["properties"]["Nome"]
  try:
    umap=deepcopy(umap_template)
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
          feature["properties"]["_umap_options"] = {"popupTemplate": "Default"};
          feature["properties"]["GitHubURL"] = "https://github.com/prin-underlandscape/"+rn;
          if "WebPageURL" in geojson["properties"] and geojson["properties"]["WebPageURL"] != "":
#            print(geojson["properties"]["WebPageURL"])
            feature["properties"]["ULSPLink"] = geojson["properties"]["WebPageURL"]
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
    with open('dataset.umap', 'w', encoding='utf-8') as f:
      json.dump(umap, f, ensure_ascii=False, indent=2)
  except KeyError as ke:
    failprint("   GeoJSON mal formattato: non trattato ("+ke.args[0]+")")
    return False

def sync(umap_url):
  # Accede alla mappa umap online
  driver.get(umap_url)
  # Attende l'abilitazione della modifica della mappa e la seleziona
  driver.find_element(By.CSS_SELECTOR, ".leaflet-control-edit-enable > button").click()
  # Preme il bottone rotella per modificare le impostazioni della mappa
  driver.find_element(By.CSS_SELECTOR, ".update-map-settings").click()
  # Preme "Azioni avanzate"
  driver.find_element(By.CSS_SELECTOR, "details:nth-child(11) > summary").click()
  # Preme "Vuota"
  driver.find_element(By.CSS_SELECTOR, ".umap-empty:nth-child(2)").click()
  # Preme "Rimuovi tutti i layer" (importante)
  driver.find_element(By.CSS_SELECTOR, ".button:nth-child(3)").click()
  # Chiude il pannello "Rotella"
  driver.find_element(By.CSS_SELECTOR, ".buttons:nth-child(1) .icon-close").click()
  # Seleziona il tasto di caricamento "Freccia in alto"
  driver.find_element(By.CSS_SELECTOR, ".upload-data").click()
  # Carica i dati (ma si potrebbero anche copiare direttamente nel textbox
  # senza memorizzarlo in un file
  upload_file = abspath("./dataset.umap")
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
  driver.get("https://umap.openstreetmap.fr/")	

if len(sys.argv) < 2:
  exit("Bisogna passare i dataset da sincronizzare")

print("Ecco")

# Caricamento del file di configurazione
with open("config.json") as json_data:
  config = json.load(json_data)

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
    generate_umap(geojson)
    sync(geojson["properties"]["umapKey"])
  except KeyError as error:
    print("C'è stato un problema:", error)
	 
