import json
from colprint import emphprint, failprint, warnprint

tag_options = {
 "Grotta": { "color": "Sienna", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/star.svg"},
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

####
# Crea i file umap
####
def generate_umap(geojson, rn):
  print(rn)
  try:
    with open("../umapTemplate.json") as json_data:
      umap = json.load(json_data)
    print("\u2022 Generazione del file umap")
    allowed_types = list(map(lambda l: l["_umap_options"]["name"], umap["layers"]))
    for feature in geojson["features"]:
      try:
        if feature["properties"]["ulsp_type"] in allowed_types:
          feature["properties"]["_umap_options"] = {"popupTemplate": "Default"};
          feature["properties"]["GitHubURL"] = "https://github.com/prin-underlandscape/"+rn;
          if "WebPageURL" in geojson["properties"] and geojson["properties"]["WebPageURL"] != "":
            print(geojson["properties"]["WebPageURL"])
            feature["properties"]["Link"] = geojson["properties"]["WebPageURL"]
          if feature["properties"]["ulsp_type"] == "POI" and feature["properties"]["Tag primario"] != "":
            print(feature["properties"]["Tag primario"])
            feature["properties"]["_umap_options"] |= tag_options[feature["properties"]["Tag primario"]]
      # Find layer for feature
          layers = list(filter(lambda l: l["_umap_options"]["name"] == feature["properties"]["ulsp_type"], umap["layers"]))
          if len(layers) != 1:
            failprint("Wrong ulsp format")
          layers[0]["features"].append(feature);
      # Setup map center
          if feature['properties']['ulsp_type'] in ['POI','Sito','QRtag']:
            if 'coordinates' not in umap:
              umap["geometry"] = {
                "type": "Point",
                "coordinates": feature["geometry"]["coordinates"]
              }
          elif feature["properties"]["ulsp_type"] == "Percorso":       
            umap["geometry"] = {
              "type": "Point",
              "coordinates": feature["geometry"]["coordinates"][0]
            }
          else:
            umap["geometry"] = {
              "type": "Point",
              "coordinates": [10.1, 44.14]
            }
      # Setup map name
          umap["properties"]["name"] = rn
        else:
          raise KeyError("Wrong ulsp_type")
        with open(rn+"/"+rn+".umap", 'w', encoding='utf-8') as f:
          json.dump(umap, f, ensure_ascii=False, indent=2)
      except KeyError as ke:
        failprint("   Feature mal formattata: non trattata ("+ke.args[0]+")")
        continue
  except KeyError as ke:
    failprint("   GeoJSON mal formattato: non trattato ("+ke.args[0]+")")
    return False
