import json
from colprint import emphprint, failprint, warnprint
from umap_common import tag_options, umap_template

####
# Crea i file umap
####
def generate_umap(geojson, rn):
  print(rn)
  try:
#    with open("../umapTemplate.json") as json_data:
#      umap = json.load(json_data)
    umap=copy.deepcopy(umap_template)
    print("\u2022 Generazione del file umap")
    allowed_types = list(map(lambda l: l["_umap_options"]["name"], umap["layers"]))
    for feature in geojson["features"]:
      try:
        if feature["properties"]["ulsp_type"] in allowed_types:
          feature["properties"]["_umap_options"] = {"popupTemplate": "Default"};
          feature["properties"]["GitHubURL"] = "https://github.com/prin-underlandscape/"+rn;
          if "WebPageURL" in geojson["properties"] and geojson["properties"]["WebPageURL"] != "":
            print(geojson["properties"]["WebPageURL"])
            feature["properties"]["ULSPLink"] = geojson["properties"]["WebPageURL"]
          if feature["properties"]["ulsp_type"] == "POI" and feature["properties"]["Tag primario"] != "":
            print(feature["properties"]["Tag primario"])
            feature["properties"]["_umap_options"] |= tag_options[feature["properties"]["Tag primario"]]
      # Find layer for feature
          layers = list(filter(lambda l: l["_umap_options"]["name"] == feature["properties"]["ulsp_type"], umap["layers"]))
          if len(layers) != 1:
            failprint("Wrong ulsp format")
          layers[0]["features"].append(feature);
      # Setup map center, the "geometry" attribute in the umap JSON Object. 
      # Uses the first feature Point, LineString or MultiLineString in the dataset,
      # defaults to a point not far from Monzone in Lunigiana
          if 'geometry' not in umap:
            umap["geometry"] = {
              "type": "Point",
              "coordinates": [10.1, 44.14]
            }
            if feature['geometry']['type'] == 'Point':
              umap["geometry"]["coordinates"] = feature["geometry"]["coordinates"]
            elif feature['geometry']['type'] == 'LineString': 
              umap["geometry"]["coordinates"] = feature["geometry"]["coordinates"][0]
            elif feature['geometry']['type'] == 'MultiLineString':      
              umap["geometry"]["coordinates"] = feature["geometry"]["coordinates"][0][0]      
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
