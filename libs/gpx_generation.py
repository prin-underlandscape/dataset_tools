import json
import inspect
from colprint import emphprint, failprint, warnprint
from gpx import GPX, Waypoint, Link, Track, TrackSegment

tag_options = {
 "Grotta": { "color": "Sienna", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/star.svg"},
 "Ristoro": { "color": "DarkViolet", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/restaurant.svg"},
 "Accoglienza": { "color": "DarkViolet", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/hotel.svg"},
 "Svago": { "color": "DarkViolet", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/pitch.svg"},
 "Infopoint": { "color": "Red", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/information.svg"},
 "Servizi": { "color": "Red", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/government.svg"},
 "Trasporti": { "color": "Red", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/bus.svg"},
 "Sanità": { "color": "Red", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/bus.svg"},
 "Segnaletica": { "color": "Green", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/guidepost.svg"},
 "Attrazione naturalistica": { "color": "Green", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/mountain.svg"},
 "Monumento": { "color": "MediumBlue", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/monument.svg"},
 "Museo": { "color": "MediumBlue", "iconClass": "Drop", "iconUrl": "/uploads/pictogram/museum.svg"}
}

def mkwpt(pt):
  wpt = Waypoint()
  wpt.lat = pt[1];
  wpt.lon = pt[0];
  wpt.ele = pt[2];
  return wpt;

####
# Crea il file gpx
####
def generate_gpx(geojson, rn):
  gpx = GPX()
  print(rn)
  try:
    with open("../umapTemplate.json") as json_data:
      umap = json.load(json_data)
      print("\u2022 Generazione del file gpx")
      allowed_types = list(map(lambda l: l["_umap_options"]["name"], umap["layers"]))
      for feature in geojson["features"]:
        try:
          if feature["properties"]["ulsp_type"] in allowed_types:
            if feature['properties']['ulsp_type']  in ['POI','Sito','QRtag','Risorsa']:
              wpt = Waypoint()
              wpt.lat = feature["geometry"]["coordinates"][1];
              wpt.lon = feature["geometry"]["coordinates"][0];
              wpt.name = feature["properties"]["Titolo"];
              wpt.desc = feature["properties"]["Descrizione"];
              wpt.ele = "500";
              # wpt.sym = "green-pin-down" # Non esistono icone standard
              #link = Link(None)
              #link.href = "https://www.google.com"
              #image = Link()
              #image.href = "https://i.postimg.cc/XJg7Nmq2/Pianta.jpg"
              #image.type = "image/jpeg"
              #image.text = "Immagine"
              #wpt.links = [image]
              gpx.waypoints.append(wpt)
            elif feature["properties"]["ulsp_type"] == "Percorso":
              trk = Track()
              trk.name = "Prova" #feature["properties"]["Titolo"];
              trk.desc = "Descrizione" #feature["properties"]["Descrizione"];
              # Linestring
              trksgmt = TrackSegment();
              trksgmt.trkpts = list(map(mkwpt,feature["geometry"]["coordinates"]));
              trk.trksegs.append(trksgmt)
              gpx.tracks.append(trk)
          else:
            raise KeyError("Wrong ulsp_type")
          gpx.to_file(rn+"/"+rn+".gpx");
        except KeyError as ke:
          failprint("   Feature mal formattata: non trattata ("+ke.args[0]+")")
          continue
  except KeyError as ke:
    failprint("   GeoJSON mal formattato: non trattato ("+ke.args[0]+")")
    return False
