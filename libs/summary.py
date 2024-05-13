import os
import json
import random
from colprint import emphprint, failprint, warnprint
import upload_list

summary_filename = "summary.umap"
summary_URL = "https://umap.openstreetmap.fr/it/map/sommario_1044830"
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
#        "overlay": null,,
        "facetKey": "ulsp_type,Tag primario,Dataset",
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
        "permanentCreditBackground": True,
        "popupContentTemplate": "# {ulsp_type} - {Titolo} {Tag primario}\n{{{Foto}|300}}\n**{Descrizione}**\n[[{Link}|Link]] alla pagina dedicata\n**Tag primario**: {Tag primario}\n**Altri tag**: {Altri tag}"   
    },
    "layers": []
}

def generate_summary(ul):
  # Read configuration and assets
  # with open("dataset-sync.config") as json_data:
    # config = json.load(json_data)
  # with open("umapTemplate.json") as json_data:
    # umapTemplate = json.load(json_data)
    
  # logo = Image.open("logoEle_v2.2_small.png").convert("RGBA")
  
  # colprint.emphprint("Clono il repository Master da github")
  # my_git.clone(config['masterName'])
  # os.chdir(config['masterName'])
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
      "popupTemplate": "Default",
      "popupContentTemplate": ""
    }
    
    for f in geojson['features']:
#      print(f)
      f['properties']['Dataset'] = os.path.splitext(fn)[0]
      f['properties']['Link GitHub'] = 'https://github.com/prin-underlandscape/'+os.path.splitext(fn)[0]
  # Compatibilità quando mancano le properties del dataset (geojson)
      if 'properties' in geojson:
        f['properties']['Mappa'] = geojson['properties']['umapKey']
        f['properties']['name'] = f['properties']['Titolo']
      if '_umap_options' not in f['properties']: f['properties']['_umap_options']={}
      if f['properties']['ulsp_type'] == 'Sito':
        f['properties']['_umap_options']['iconClass'] = 'Ball'
        f['properties']['_umap_options']['color'] = '#800101' #Override color for sites
      elif f['properties']['ulsp_type'] == 'POI':
        f['properties']['_umap_options']['iconClass'] = 'Circle'
      elif f['properties']['ulsp_type'] == 'QRtag':
        f['properties']['_umap_options']['iconClass'] = 'Drop'
        f['properties']['_umap_options']['iconUrl']= "/uploads/pictogram/guidepost.svg"
  #  print(color)
    summary['layers'].append(geojson)
  
  with open("../summary.umap", 'w', encoding='utf-8') as f:  
    json.dump(summary, f , ensure_ascii=False, indent=2)
  
  ul.log(summary_filename,summary_URL)
  
  
