from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
import time
from os.path import abspath


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

# Il template per il dataset: contiene le proprietà del dataset e i
# layer per i diversi ulsp_types 
dataset_template = {
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
       "name": "OSM Outdoors (Thunderforest)",
       "maxZoom": 18,
       "minZoom": 0,
       "attribution": "Tiles © [[http://www.thunderforest.com/outdoors/|Thunderforest]] / map data © [[http://osm.org/copyright|OpenStreetMap contributors]] under ODbL",
       "url_template": "https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=e6b144cfc47a48fd928dad578eb026a6"
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
{Descrizione}
[[{GPXDownload}|Scarica]] il percorso in formato GPX
---
Questa feature di tipo **{ulsp_type}** è contenuta nel dataset *{Dataset}*
Il contenuto del dataset è accessibile [[{GitHubURL}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{ULSPLink}|qui]]
--- 

**Punto d'accesso**: {Punto d'accesso}
**Provincia**: {Provincia}
**Comune**: {Comune}
**Lunghezza** (km): {Lunghezza}
**Durata**: {Durata}
**Dislivello in salita** (m): {Dislivello in salita}
**Dislivello in discesa** (m): {Dislivello in discesa}
**Difficoltà** (km): {Difficoltà}
**Segnaletica**: {Segnaletica} 
**Copertura GPS**: {Copertura GPS} 
**Copertura rete Mobile**: {Copertura rete mobile} 
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
{Descrizione}
---
Questa feature di tipo **{ulsp_type}** è contenuta nel dataset *{Dataset}*
Il contenuto del dataset è accessibile [[{GitHubURL}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{ULSPLink}|qui]]
---
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
{Testo}
**FID**: {fid}
---
Questa feature di tipo **{ulsp_type}** è contenuta nel dataset *{Dataset}*
Il contenuto del dataset è accessibile [[{GitHubURL}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{ULSPLink}|qui]]
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
---
Questa feature di tipo **{ulsp_type}** è contenuta nel dataset *{Dataset}*
Il contenuto del dataset è accessibile [[{GitHubURL}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{ULSPLink}|qui]]
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
**Pagina Web**: [[{ULSPLink}|link]]
**Tag primario**: {Tag primario}
**Altri tag**: {Altri tag}"
---
Questa feature di tipo **{ulsp_type}** è contenuta nel dataset *{Dataset}*
Il contenuto del dataset è accessibile [[{GitHubURL}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{ULSPLink}|qui]]
'''
      }
    },
    {
      "type": "FeatureCollection",
      "features": [ ],
      "_umap_options": {
        "name": "Itinerario",
        "color": "Brown",
        "weight": 6,
        "displayOnLoad": True,
        "browsable": True,
        "remoteData": {},
        "popupShape": "Panel",
        "popupTemplate": "Table",
        "popupContentTemplate": '''\
# {Titolo}
## Itinerario {Tipologia}
{Descrizione}
[[{GPXDownload}|Scarica]] in formato GPX
---
{{{Foto accesso}|150}}
**Punto d'accesso**: {Punto d'accesso}
**Provincia**: {Provincia}
**Comune**: {Comune}
**Lunghezza** (km): {Lunghezza}
**Durata**: {Durata}
**Dislivello in salita** (m): {Dislivello in salita}
**Dislivello in discesa** (m): {Dislivello in discesa}
**Difficoltà** (km): {Difficoltà}
**Segnaletica**: {Segnaletica}
---
Questa feature di tipo **{ulsp_type}** è contenuta nel dataset *{Dataset}*
Il contenuto del dataset è accessibile [[{GitHubURL}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{ULSPLink}|qui]]
'''
      }
    }
  ]
}

tag_options = {
# "Grotta": { "color": "Sienna", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/star.svg"},
 "Grotta": { "color": "Sienna", "iconClass": "Drop", "iconUrl": "https://i.postimg.cc/4xKB2LTm/grottat.png"},
 "Ristoro": { "color": "DarkViolet", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/restaurant.svg"},
 "Accoglienza": { "color": "DarkViolet", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/hotel.svg"},
 "Svago": { "color": "DarkViolet", "iconClass": "Drop", "iconUrl": "https://i.postimg.cc/FKBTtN7Q/trekking.png"},
 "Infopoint": { "color": "Red", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/information.svg"},
 "Servizi": { "color": "Red", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/government.svg"},
 "Trasporti": { "color": "Red", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/bus.svg"},
 "Sanità": { "color": "Red", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/bus.svg"},
 "Segnaletica": { "color": "Green", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/guidepost.svg"},
 "Attrazione naturalistica": { "color": "Green", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/mountain.svg"},
 "Monumento": { "color": "MediumBlue", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/monument.svg"},
 "Museo": { "color": "MediumBlue", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/museum.svg"}
}

# Login using user credentials in the config file (alternative manual
# login questionable...)
def umap_login(driver, config):
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
  # Attende di accedere alla dashboard	
  driver.find_element(By.PARTIAL_LINK_TEXT, "Dashboard") # Attende di accedere alla dashboard

# Uploads the content of "umap_file" to the map at "umap_url" using the
# Selenium driver "driver". Depends on uMap web pages organization,
# which is unstable. Use Shift-Ctrl-I in the browser to update the
# elements references.
# After upload waits 10s to allow a fast check
def umap_sync(driver, umap_url, umap_file):
  print("Accedo alla mappa")
  # Accede alla mappa umap online
  driver.get(umap_url)
  # Attende l'abilitazione della modifica della mappa e la seleziona
  driver.find_element(By.CSS_SELECTOR, ".edit-enable.leaflet-control > button").click() 
  print("Modifica abilitata!")
  # Preme il bottone "Rotella" per modificare le impostazioni della mappa
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
  # Carica i dati (ma forse si potrebbero anche copiare direttamente
  # nel textbox senza memorizzarlo in un file
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

