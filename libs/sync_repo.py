# Questa libreria fornisce il metodo sync_repo che rigenera il contenuto di un repository sulla
# base del dataset geojson contenuto nel repository Master.
# Il repository, oltre al geojson originario, conterrà:
# - una directory "vignettes" con tutte le foto indicate nelle feature del dataset
# - un file gpx con tutti i percorsi e i punti del dataset
# - un file README che presenta il contenuto del dataset 
# Diversamente da quanto realizzato precedentemente, il repository non contiene il file
# per la mappa uMap, che viene invece generato da un comando distinto ed utilizzato
# unicamente per generare la mappa su uMap. Il file .uMap viene rimosso se presente
# da precedenti revisioni

import sys 
sys.path.append('.')
import urllib.request
from io import BytesIO
from os.path import basename, splitext, isdir
from os import listdir, makedirs, remove
from shutil import rmtree, copyfile
from urllib.parse import urlparse
import json
# dependencies
from PIL import Image, ImageDraw, ImageFont
import qrcode

from my_git import clone, push_repo
from gpx_generation import generate_gpx;

def grab_image(url, filename, vignette_size):
  try:
    with urllib.request.urlopen(url) as response:
      image=Image.open(BytesIO(response.read()))
      image.thumbnail((vignette_size,vignette_size))
      image.save(filename)
  except Exception as e:
    raise(e)

# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
def failprint(s):
  print('\x1b[1;30;41m' + s + '\x1b[0m')
def emphprint(s):
  print('\x1b[1;30;42m' + s + '\x1b[0m')
def warnprint(s):
  print('\x1b[1;30;43m' + s + '\x1b[0m')
#grab_image(image_url,"image.jpg")

def vignetteNameFromURL(url):
  if ( url.netloc == 'i.postimg.cc' ):
    key = url.path.split('/')[1]
    return key + ".jpg"
  elif ( url.netloc == 'www.gaiagps.com' ):
    key = url.path.split('/')[4]
    return key + ".jpg"
  elif ( url.netloc == 'underlandscape.cfs.unipi.it' ):
    key = url.path.split('/')[4][:8]
    return key + ".jpg"
  else:
    if ( url.netloc != "" ):
      raise ValueError("URL non valida")
    else:
      raise ValueError("Nessuna immagine")

# Vero se il file f è nel sidecar del repository r
def in_sidecar(f,r):
  return splitext(basename(f))[0] == r 

#####
# Aggiorna le immagine nel dataset
#####
def sync_images(geojson, dataset_name, vignette_size):
  print("\u2022 Scarico le foto dall'archivio fotografico")
# Rimuove tutte le foto dalla directory, se esiste oppure la crea  
  try:
    if isdir(f"{dataset_name}/vignettes"):
      for f in listdir(f"{dataset_name}/vignettes"):
        remove(f"{dataset_name}/vignettes/{f}")
    else:
      makedirs(f"{dataset_name}/vignettes")
  except Exception as e:
      raise(e)
# Scan features for pictures
  for feature in geojson["features"]:
    try:
      ulsp_type = feature["properties"]["ulsp_type"]
      if ( ulsp_type == "Percorso" ):
        url = urlparse(feature["properties"]["Foto accesso"])
      else:
        url = urlparse(feature["properties"]["Foto"])
      try:
        photo_filename = f"{dataset_name}/vignettes/{vignetteNameFromURL(url)}"
# Questa eviterebbe che la foto venga sovrascritta con una nuova, ma non pare che sia opportuno
#        if ( os.path.exists(photo_filename) ):
#          print("   "+feature["properties"]["Titolo"] + " (" + feature["properties"]["ulsp_type"] +")" + ": immagine già presente");
#        else:
        print("   Scarico l'immagine di " + feature["properties"]["Titolo"])
        print(photo_filename)
        grab_image(feature["properties"]["Foto"], photo_filename, vignette_size)
      except Exception:
        warnprint(f"    Foto non disponibile per {feature['properties']['Titolo']} ({feature['properties']['ulsp_type']})")
    except KeyError:
      try:
        warnprint(f"    Foto non disponibile per {feature['properties']['Titolo']} ({feature['properties']['ulsp_type']})")
      except KeyError as ke:
        failprint("   " + feature["properties"]["Titolo"] + "- Feature mal formattata: non trattata ("+ke.args[0]+")")
        continue
    except Exception as e:
      failprint("   " + feature["properties"]["Titolo"] + "- Feature mal formattata: non trattata ("+e+")")
      continue

####
# Generazione dei QRtag (segnalazione)
####      
def generate_qrtags(geojson, dataset_name, config, logo):
  print("\u2022 Genero i QRtags")
#    logo = Image.open("logoEle_v2.2_small.png").convert("RGBA") 
  for feature in geojson["features"]:
    try:
      ulsp_type = feature["properties"]["ulsp_type"]
      if ( ulsp_type == "QRtag" ):
        if not isdir(dataset_name+"/qrtags"):
          print("   Creo una cartella per i QRtag")
          makedirs(dataset_name+"/qrtags")
        titolo = feature["properties"]["Titolo"]
        testo = feature["properties"]["Testo"]
        fid = feature["properties"]["fid"]
        canvas = Image.new('RGB', (960,1260), (240,240,240))
        # Logo
        small_logo=logo.resize((170,170))
        canvas.paste(small_logo, (20,1060), small_logo)
        # QR code
        qr = qrcode.QRCode(
          version=1,
          error_correction=qrcode.constants.ERROR_CORRECT_L,
          box_size=10,
          border=2,
        )
        testo += testo+"\n"+config["weburl"]+"/"+dataset_name+"/"+fid
        qr.add_data(testo)
        qr.make(fit=True)
        qrimage = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        canvas.paste(qrimage.resize((900,900)), (30,140))
        
        draw = ImageDraw.Draw(canvas)
        # Titolo
        fs=100
        line=""
        p1=""
        font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf", fs)
        for w in titolo.split(" "):
          if p1 == "":
            while font.getlength(line+" "+w) > 900:
#              print(fs)
              fs -= 10
              if fs < 70:
                p1 = line
                line = ""
              font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf", fs)
          line = line+" "+w;
        titolo = line
        if p1 != "":
          titolo = p1 + "\n" + line
    #     if font.getlength(titolo) > 700:
    #       font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf", 70)
        draw.text((20, 0),titolo,(0,0,0),font)
        # Istruzioni
        font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf", 32)
        draw.text((200, 1050),"Scansiona il QR-code per maggiori informazioni\nsu questa località, anche senza usare Internet, e\ncerca altri QR-tag in quest'area",(50,50,50),font)
        # Nota
        #font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf", 32)
        #draw.text((140, 1140),"Cerca altri QR-code informativi in quest'area",(50,50,50),font)
        # Credits
        font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", 28)
        draw.text((200, 1195),"Underlandscape - 2021\nProgetto di ricerca di Interesse Nazionale",(50,50,50),font)
        
        canvas.save(dataset_name+"/qrtags/"+fid+".png")
    except KeyError as ke:
      failprint("   Feature mal formattata: non trattata ("+ke.args[0]+")")
      continue

####
# Genera il file README.md
####
def generate_readme(geojson, dataset_name):
  print("\u2022 Genero il readme per il dataset")
  try:
    with open(dataset_name+"/README.md", 'w', encoding='utf-8') as f:
      f.write("# " + dataset_name + " (")
      try:
        if geojson["properties"]["umapKey"] == "": raise KeyError("Link alla mappa non definito")
        f.write("[mappa](" + geojson["properties"]["umapKey"]+")")
      except:
        f.write("mappa non collegata")
      f.write(")\n")
#      print(geojson)
      try:
        if geojson["properties"]["Descrizione"] == "": raise KeyError("Descrizione vuota")
        f.write(geojson["properties"]["Descrizione"] + "\n\n")
      except:
        f.write("descrizione del dataset mancante\n")    
      f.write("Questo dataset fa parte dei risultati del progetto [PRIN Underlandscape](https://sites.google.com/view/prin-underlandscape/)\n\n")   
      f.write("La mappa di sommario con tutti i dataset prodotti nel corso del progetto è disponibile a questo [link](https://umap.openstreetmap.fr/it/map/sommario_1044830)\n\n")
      for feature in geojson["features"]:
        ulsp_type = feature["properties"]["ulsp_type"]
        f.write("## " + feature["properties"]["ulsp_type"] + ": " + feature["properties"]["Titolo"] + "\n")
        try:
          if feature["properties"]["Descrizione"] == "": raise KeyError("Descrizione vuota")
          f.write(feature["properties"]["Descrizione"] + "\n\n")
        except:
          warnprint(f"   Non è disponibile la descrizione di {feature['properties']['Titolo']} ({ulsp_type})")
          f.write(f"Descrizione di {feature['properties']['Titolo']} ({ulsp_type}) mancante\n")     
    # if qrtag display the tag
        if ( ulsp_type == "QRtag" ):
          try:
            fid = feature["properties"]["fid"]
            f.write("[<img src='qrtags/"+fid+".png' width='150'/>](qrtags/"+fid+".png) ")
            fotourl = urlparse(feature["properties"]["Foto"])
            vignette = vignetteNameFromURL(fotourl)
            f.write("[<img src='"+vignette+"' width='250'/>]("+vignette+") \n\n")
          except KeyError:
            warnprint(f"   Non è disponibile l'immagine per {feature['properties']['Titolo']} ({feature['properties']['ulsp_type']})")
            f.write("*Nessuna immagine* \n\n")
            raise KeyError
          except IndexError:
            warnprint(f"   Non è disponibile l'immagine per {feature['properties']['Titolo']} ({feature['properties']['ulsp_type']})")
            f.write("*Nessuna immagine* \n\n")
          except ValueError as e:
            warnprint(f"   Non è disponibile l'immagine per {feature['properties']['Titolo']} ({feature['properties']['ulsp_type']})")
            f.write("*Nessuna immagine* \n\n")
          except UnboundLocalError:
            pass
    # select attribute with vignette URL
        else:
          if ( ulsp_type == "Percorso" ):
            try: 
              fotourl = urlparse(feature["properties"]["Foto accesso"])
            except KeyError:
              warnprint("   Non è disponibile l'immagine per il percorso " + feature["properties"]["Titolo"])
              f.write("*Non è disponibile l'immagine dell'accesso al percorso* \n\n")
              continue
          else:
            try:
              fotourl = urlparse(feature["properties"]["Foto"])
            except KeyError:
              warnprint(f"   Non è disponibile l'immagine per {feature['properties']['Titolo']} ({feature['properties']['ulsp_type']})")
              f.write("*Non è disponibile l'immagine relativa alla feature* \n\n")
              continue
          try:
            vignette = vignetteNameFromURL(fotourl)
            f.write(f"[<img src=vignettes/{vignette} width='250'/>]("+vignette+") \n\n")
          except IndexError:
            warnprint(f"   Non è disponibile l'immagine per {feature['properties']['Titolo']} ({feature['properties']['ulsp_type']})")
            f.write("*Nessuna immagine* \n\n")
          except ValueError:
            warnprint(f"   Non è disponibile l'immagine per {feature['properties']['Titolo']} ({feature['properties']['ulsp_type']})")
            f.write("*Nessuna immagine* \n\n")
          except UnboundLocalError:
            pass
        f.write("**"+feature["properties"]["Descrizione"]+"**"+"\n")
  except KeyError as ke:
    failprint("   GeoJSON mal formattato: non trattato ("+ke.args[0]+")")
    return False

def sync_repo(dataset_name, config, logo):
  try:
    master_directory = config['master_repo']
    emphprint("Clono "+dataset_name)
# Rimuove la directory del dataset da aggiornare, se esistente 
    if isdir(dataset_name):
      rmtree(dataset_name, ignore_errors=True)
# Clona il repository del dataset (la directory generata ha il nome del dataset)
    dataset_repository = clone(dataset_name)
  except Exception as e:
    raise(e)
    
  # Copia il geojson e i file nel sidecar dal master nel repository clonato
  # I file nel sidecar hanno il nome che inizia con il nome del repo seguito da .
  files = list(filter(lambda fn: in_sidecar(fn,dataset_name), listdir(master_directory)))
  
  print("\u2022 Copio questi file dal master nel repository del dataset:", end=" ")
  for f in files:
    try:
      print(f, end=" ")
      copyfile(f"{master_directory}/{f}",f"{dataset_name}/{f}")
    except Exception as e:
      print(e)
      warnprint("Cannot copy file in cloned directory ("+f+")")
      continue
  print()

  # Carica in una variabile il geojson (una FeatureCollection)
  with open(f"{master_directory}/{dataset_name}.geojson") as json_data:
    geojson = json.load(json_data)
  
  try:
    remove(f"{dataset_name}/{dataset_name}.umap")
  except:
    warnprint("Non posso rimuovere il file .umap dal repository")
  sync_images(geojson, dataset_name, config["vignette_size"])     # aggiorna le foto
  generate_gpx(geojson, dataset_name)   # crea il file gpx
  generate_qrtags(geojson, dataset_name, config, logo) # crea i tag delle feature con ulsp_type qrtag
  generate_readme(geojson, dataset_name) # 
  # #ul.log(rn+".umap",geojson['properties']['umapKey'])
  
  push_repo(dataset_repository, config["username"], config["access_token"])
  rmtree(dataset_name, ignore_errors=True)
  
  return





