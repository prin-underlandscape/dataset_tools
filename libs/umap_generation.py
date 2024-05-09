import json
from colprint import emphprint, failprint, warnprint

tag_options = {
  "Albergo": { "color": "MediumSlateBlue","iconClass": "Drop", "iconUrl": "/uploads/pictogram/hotel.svg" },
  "Ristorante": { "iconClass": "Drop", "iconUrl": "/uploads/pictogram/restaurant.svg"},
  "Bar": { "iconClass": "Drop", "iconUrl": "/uploads/pictogram/cafe.svg" },
  "Parco giochi": { "iconClass": "Drop", "iconUrl": "/uploads/pictogram/playground.svg"},
  "Monumento": { "iconClass": "Drop", "iconUrl":  "/uploads/pictogram/monument.svg"},
  "Parcheggio": { "iconClass": "Drop", "iconUrl":  "/uploads/pictogram/parking-car.svg"},
  "Segnalazione": { "iconClass": "Drop", "iconUrl":  "/uploads/pictogram/guidepost.svg"},
  "Fermata Bus": { "iconClass": "Drop", "iconUrl":  "/uploads/pictogram/bus-stop.svg"}
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
