
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
{Descrizione}
---
Questa feature di tipo **{ulsp_type}** è contenuta nel dataset *{Dataset}*
Il contenuto del dataset è scaricabile da [[{GitHubURL}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{Link}|qui]]
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
{Descrizione}
---
Questa feature di tipo **{ulsp_type}** è contenuta nel dataset *{Dataset}*
Il contenuto del dataset è scaricabile da [[{GitHubURL}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{Link}|qui]]
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
Il contenuto del dataset è scaricabile da [[{GitHubURL}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{Link}|qui]]
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
Il contenuto del dataset è scaricabile da [[{GitHubURL}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{Link}|qui]]
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
---
Questa feature di tipo **{ulsp_type}** è contenuta nel dataset *{Dataset}*
Il contenuto del dataset è scaricabile da [[{GitHubURL}|qui]] 
La pagina dedicata nel sito Web del progetto è [[{Link}|qui]]
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
