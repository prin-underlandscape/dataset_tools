import os, sys
import time
import json
import os, sys
from os.path import basename, splitext
from urllib.request import urlretrieve, urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys


def sync(dataset_name):
  # Attende di accedere alla dashboard	
  driver.find_element(By.PARTIAL_LINK_TEXT, "Dashboard") # Attende di accedere alla dashboard
  print(f"Sincronizzo {dataset_name}") 
  # Download dataset geojsos and extract URL of umap map
  with urlopen(f"https://raw.githubusercontent.com/prin-underlandscape/{dataset_name}/main/{dataset_name}.geojson") as content:
    umap_url = json.load(content)["properties"]["umapKey"]
  print(f"Scarico il file umap da {umap_url}") 
  # Scarica il file umap e lo memorizza localmente 
  urlretrieve(f"https://raw.githubusercontent.com/prin-underlandscape/{dataset_name}/main/{dataset_name}.umap",'./dataset.umap')
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
  upload_file = os.path.abspath("./dataset.umap")
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
chrome_service = Service(executable_path='/snap/chromium/2890/usr/lib/chromium-browser/chromedriver')
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
    dataset = splitext(basename(fn))[0]
    sync(dataset)
  except Exception as error:
    print("C'è stato un problema:", error)
	 
