import os
import json
import random
from colprint import emphprint, failprint, warnprint

# import pytest
# import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service

import upload_list

"""
Aiuto dalla GUI di umap
Proprietà dinamiche
Specificando le proprietà dell'oggetto attraverso le parentesi graffe es. {name} queste saranno automaticamente sostituite con i valori corrispondenti
Formattazione testo
*un solo asterisco per il corsivo*
**due asterischi per il testo marcato**
# un cancelleto per l'intestazione principale
## due cancelletti per le intestazioni di secondo livello
### tre cancelletti per intestazione di terzo livello
Link semplice: [[http://example.com]]
Link con testo: [[http://example.com|testo del link]]
Immagini: {{http://image.url.com}}
Immagine con larghezza personalizzata (width) (in px): {{http://image.url.com|width}}
Iframe: {{{http://iframe.url.com}}}
Iframe con altezza (in px) personalizzata: {{{http://iframe.url.com|height}}}
Iframe con altezza e larghezza personalizzata (in px): {{{http://iframe.url.com|height*width}}}
--- per una linea orizzontale
"""

popupTemplate ='''\
# {Titolo} {Tag primario}
{{{Foto}|300}}
{Descrizione}
Questo **{ulsp_type}** è contenuto nel dataset *{Dataset}*
La mappa del dataset è visibile [[{umapURL}|qui]]
Il contenuto del dataset è scaricabile da [[{Link GitHub}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{WebPageURL}|qui]]
**Tag primario**: {Tag primario}
**Altri tag**: {Altri tag}
'''



# Inizializzazione umap mappa Summary 
summary = {
	"type": "umap",
	"geometry": {
    "type": "Point",
    "coordinates": [
      10.405556,
      44.121944
    ]
  },
	"properties": {
    "name": "Sommario",
    "zoom": 11,
    "easing": False,
    "licence": "",
    "miniMap": False,
    "overlay": {},
    "facetKey": "ulsp_type,Tag primario,Dataset",
    "slideshow": {},
    "tilelayer": {
       "tms": False,
       "name": "OSM OpenTopoMap",
       "maxZoom": 20,
       "minZoom": 1,
       "attribution": "Kartendaten: © [[https://openstreetmap.org/copyright|OpenStreetMap]]-Mitwirkende, [[http://viewfinderpanoramas.org/|SRTM]] | Kartendarstellung: © [[https://opentopomap.org/|OpenTopoMap]]    ([[https://creativecommons.org/licenses/by-sa/3.0/|CC-BY-SA]])",
       "url_template": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
    },
    "captionBar": False,
    "description": "Summary map of Underlandscape activity and results",
    "limitBounds": {},
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
  "layers": [
    {
      "type": "FeatureCollection",
      "features": [],
      "_umap_options": {
          "name": "Percorso",
          "displayOnLoad": True,
          "browsable": True,
          "remoteData": {},
          "popupShape": "Panel",
          "popupTemplate": "Table",
          "popupContentTemplate": '''\
# {Titolo}
##   ( [[https://sites.google.com/view/prin-underlandscape/home-page/attivit%C3%A0-sul-campo/{Link}|link]]) 
##   [[{GitHubURL}|GitHub repository]] 
{Descrizione}
--- 
**Lunghezza** (km): {Lunghezza}
**Durata**: {Durata}
**Dislivello in salita** (m): {Dislivello in salita}
**Dislivello in discesa** (m): {Dislivello in discesa} 
--- 
Registrato il {Data} alle {Ora} 
con {Strumento} 
da {Autore}
'''
      }
    },
    {
      "type": "FeatureCollection",
      "features": [ ],
      "_umap_options": {
        "name": "POI",
        "displayOnLoad": True,
        "browsable": True,
        "remoteData": {},
        "iconClass": "Ball",
        "popupShape": "Panel",
        "popupTemplate": "Table",
        "popupContentTemplate": '''\
# {Titolo}
{{{Foto}|300}} 
##   [[{GitHubURL}|GitHub repository]] 
##   [[{Link}|Link]] alla pagina dedicata 
{Descrizione} 
**Tag primario**: {Tag primario}
**Altri tag**: {Altri tag}
**Altitudine** (m): {Altitudine} 
--- 
Scattata il {Data} alle {Ora} 
con {Strumento} 
da {Autore}
'''
      }
    },
    {
      "type": "FeatureCollection",
      "features": [ ],
      "_umap_options": {
          "name": "QRtag",
          "displayOnLoad": True,
          "browsable": True,
          "remoteData": {},
          "iconClass": "Ball",
          "popupShape": "Panel",
          "popupTemplate": "Table",
          "popupContentTemplate": '''\
# {Titolo} 
{{{Foto}|300}} 
## [[{GitHubURL}|GitHub repository]] 
{Testo} 
 
FID: {fid}
'''
      }
    },
    {
      "type": "FeatureCollection",
      "features": [ ],
      "_umap_options": {
          "name": "Sito",
          "displayOnLoad": True,
          "browsable": True,
          "remoteData": {},
          "iconClass": "Ball",
          "popupShape": "Panel",
          "popupTemplate": "Table",
          "popupContentTemplate": '''\
# SITO {Sito}
{{{Foto}|300}}
## {Titolo} 
##   [[{GitHubURL}|GitHub repository]] 
## [[{Link}|Link]] alla pagina dedicata
{Descrizione}
---
**Tipologia**: {Tipologia sito}
**Definizione**: {Definizione}
**Cronologia iniziale**: {Cronologia iniziale}
**Cronologia finale**: {Cronologia finale}
**Reperti ceramici**: {Reperti ceramici}
**Reperti geologici**: {Reperti geologici}
**Reperti organici**: {Reperti organici}
**Altri manufatti**: {Altri manufatti}
---
**Altitudine** (m): {Altitudine}
**Sicurezza**: {Sicurezza}
**Accessibilità**: {Accessibilità}
**Copertura rete mobile**: {Copertura rete mobile}
**Copertura GPS**: {Copertura GPS}
---
**Provincia**: {Provincia}
**Comune**: {Comune}
**Toponimo**: {Toponimo}
**Microtoponimo**: {Microtoponimo}
**Strade d'accesso**: {Strade d'accesso}
**Altra localizzazione**: {Altri elementi di localizzazione}
---
**Prima visita**: {Data} {Ora}
**Strumento**: {Strumento}
[[{Bibliografia}|Link]] alla bibliografia
'''
      }
    },
    {
      "type": "FeatureCollection",
      "features": [ ],
      "_umap_options": {
        "name": "Risorsa",
        "displayOnLoad": True,
        "browsable": True,
        "remoteData": {},
        "iconClass": "Ball",
        "popupShape": "Panel",
        "popupTemplate": "Table",
        "popupContentTemplate": '''\
# {Titolo}
{{{Foto}|300}}
{Descrizione}
**Altitudine** (m): {Altitudine}
**Repository GitHub**: [[{GitHubURL}|link]]
**Pagina descrittiva dell'itinerario**: [[{ULSPLink}|link]]
**Pagina descrittiva della risorsa** :[[{Link}|link]]
**Tag primario**: {Tag primario}
**Altri tag**: {Altri tag}"
'''
      }
    },
    {
      "type": "FeatureCollection",
      "features": [ ],
      "_umap_options": {
        "name": "Itinerario",
        "displayOnLoad": True,
        "browsable": True,
        "remoteData": {},
        "popupShape": "Panel",
        "popupTemplate": "Table",
        "popupContentTemplate": '''\
# {Titolo}
## Itinerario {Tipologia}
   ( [[https://sites.google.com/view/prin-underlandscape/home-page/attivit%C3%A0-sul-campo/{Link}|link]]) 
##   [[{GitHubURL}| Download ]] 
{Descrizione}
--- 
**Lunghezza** (km): {Lunghezza}
**Durata**: {Durata}
**Dislivello in salita** (m): {Dislivello in salita}
**Dislivello in discesa** (m): {Dislivello in discesa}
'''
      }
    }
  ]
}

# Viene invocata nella directory ottenuta scaricando il repo Master
def generate_summary(ul):

  # Caricamento del file di configurazione (dovrebbe essere fatto fuori e passato come parametro)
  with open("../config.json") as json_data:
    config = json.load(json_data)

  emphprint("Generazione della mappa umap di sommario")
	# filtra i file con estensione geojson
  geojson_files = list(
    filter(lambda fn: os.path.splitext(fn)[1] == ".geojson", os.listdir(".")) 
  )
	#print(geojson_files)
	
  for fn in geojson_files:
    emphprint("  Includo il dataset " + os.path.splitext(fn)[0])
    with open(fn) as json_data:
      geojson = json.load(json_data)
    random.seed(sum(map(ord,fn)))
    randomColor = hex(random.randint(0,16777215)).replace('0x','#')
		
    for f in geojson['features']:
      ulspType = f['properties']['ulsp_type']
      f['properties']['Dataset'] = os.path.splitext(fn)[0]
      f['properties']['Link GitHub'] = 'https://github.com/prin-underlandscape/'+os.path.splitext(fn)[0]
      try:
        f['properties']['umapURL'] = geojson['properties']['umapKey']
        f['properties']['WebPageURL'] = geojson['properties']['WebPageURL']
      except KeyError as e:
        print(f'Error: {e}')
      f['properties']['name'] = f['properties']['Titolo']
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
      try:
        layer=next(
          filter(lambda l: l["_umap_options"]["name"] == ulspType, summary["layers"])
        )
        layer["features"].append(f)
        print(f'{ulspType} - {f["properties"]["name"]}')
      except Exception as e:
        print(f'Error: {e}')
	
  with open(config["summary_filename"], 'w', encoding='utf-8') as f:  
    json.dump(summary, f , ensure_ascii=False, indent=2)
	
  ul.log(config["summary_filename"], config["summary_URL"])
  
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
