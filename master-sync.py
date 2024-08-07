import sys 
sys.path.append('./libs')

import urllib.request
import io
import os
import sys
import shutil
import pathlib
from urllib.parse import urlparse
import json
# dependencies
from PIL import Image, ImageDraw, ImageFont
import qrcode
import datetime

# https://github.com/PyGithub/PyGithub
# more: https://stackoverflow.com/questions/49458329/create-clone-and-push-to-github-repo-using-pygithub-and-pygit2
from github import Github
from github import Auth
import pygit2

from os.path import splitext, basename
from sync_repo import sync_repo

from my_git import diffFiles, push_repo, clone
from colprint import emphprint, failprint, warnprint
#from summary import generate_summary
#from upload_list import UploadList;
#from umap_generation import generate_umap;
from gpx_generation import generate_gpx;

def grab_image(url,filename):
  with urllib.request.urlopen(url) as response:
    image=Image.open(io.BytesIO(response.read()))
    image.thumbnail((config["vignette_size"],config["vignette_size"]))
    image.save(filename)

# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
def failprint(s):
  print('\x1b[1;30;41m' + s + '\x1b[0m')
def emphprint(s):
  print('\x1b[1;30;42m' + s + '\x1b[0m')
def warnprint(s):
  print('\x1b[1;30;43m' + s + '\x1b[0m')
#grab_image(image_url,"image.jpg")

def cleanup():
  shutil.rmtree(config['master_repo'], ignore_errors=True)
  
def vignetteNameFromURL(url):
  if ( url.netloc == 'i.postimg.cc' ):
    key = url.path.split('/')[1]
    return "/vignettes/" + key + ".jpg"
  elif ( url.netloc == 'www.gaiagps.com' ):
    key = url.path.split('/')[4]
    return "/vignettes/" + key + ".jpg"
  elif ( url.netloc == 'underlandscape.cfs.unipi.it' ):
    key = url.path.split('/')[4][:8]
    return "/vignettes/" + key + ".jpg"
  else:
    if ( url.netloc != "" ):
      raise ValueError("URL non valida")
    else:
      raise ValueError("Nessuna immagine")

# Funziona
def create_user(token):
  with Github(token) as g:
    try:
      user = g.get_user()
#     pprint(user)
    except:
      failprint("Authentication failure")
      exit()
  return user
  
# Funziona
# def clone(repoName):
  # if os.path.isdir(repoName):
    # warnprint("Please remove "+repoName+" folder")
    # exit()
  # return pygit2.clone_repository("https://github.com/prin-underlandscape/"+repoName,repoName)

# Funziona
def pull():
  master = pygit2.Repository('.')
  remote = master.remotes["origin"]
  remote.fetch()
  remote_master_id = master.lookup_reference('refs/remotes/origin/main').target
  merge_result,altro = master.merge_analysis(remote_master_id)
  print(merge_result)
  if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
    return
  elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
    master.merge(remote_master_id)
  else:
    failprint("Pull fallita")
    exit()

###
# Esamina commit sino a trovarne uno che contiene il file .lastsync
# e inserisce nell'insieme result i nomi dei file modificati dai
# commit.
# Restituisce l'insieme (senza ripetizioni) dei file modificati
# dall'ultima sincronizzazione    
###
# def diffFiles():
  # result = []
  # master = pygit2.Repository('.')
  # commit = list(master.walk(master.head.target))[0]
  # while ( any(commit.parents) ):
    # diff = master.diff(commit, commit.parents[0])
    # df = list(
            # map(lambda obj: obj.delta.new_file.path, 
              # filter(lambda obj: type(obj) == pygit2.Patch, diff))
        # )
# #    print(df)
    # if ( ".lastsync" in df ): break
    # result += df
    # commit = commit.parents[0]
# #    print("---")
# #  pprint(list(set(result)))
  # return list(set(result))

# Funziona
def indexList():
  master = pygit2.Repository('.')
  return list(map(lambda obj: obj.name, list(master.walk(master.head.target))[0].tree))
  
def commitMaster():
  if list(map(lambda r: r.delta.new_file.path, master.diff("HEAD"))):
    # Build index and tree
    master.index.add_all()
    master.index.write()
    tree = master.index.write_tree()
    # Commit
    author = pygit2.Signature("Augusto Ciuffoletti", "augusto.ciuffoletti@gmail.com")
    message = input("Enter commit message: ")
    master.create_commit('HEAD', author, author, message,tree,[master.head.target])
  else:
    emphprint('Nothing to commit on summary repository')
    
# def push_repo(r):
# # if list(map(lambda r: r.delta.new_file.path, r.diff("HEAD"))):
  # # Build index and tree
  # r.index.add_all()
  # r.index.write()
  # tree = r.index.write_tree()
  # # Commit
  # author = pygit2.Signature("Augusto Ciuffoletti", "augusto.ciuffoletti@gmail.com")
  # message = input("Digita il messaggio di commit per il dataset: ")
  # r.create_commit('HEAD', author, author, message,tree,[r.head.target])
  # # Push
  # # Build credentials
  # credentials = pygit2.UserPass(config["username"], config["access_token"])
  # # Push on "origin" remote with user credentials
  # remote = r.remotes["origin"]
  # remote.credentials = credentials
  # callbacks=pygit2.RemoteCallbacks(credentials=credentials)
  # remote.push(['refs/heads/main'],callbacks=callbacks)
# #  else:
# #    emphprint('   Non è necessario aggiornare questo dataset')

# # Vero se il file f è nel sidecar del repository r
def in_sidecar(f,r):
  return f.startswith(r+'.')

#####
# Aggiorna le immagine nel dataset
#####
def sync_images():
# create directory if non-existent
  print("\u2022 Scarico le foto dall'archivio fotografico")
  try:
    if not os.path.isdir(rn+"/vignettes"):
      print("   Creo una directory per le immagini")
      os.makedirs(rn+"/vignettes")
  except:
      return False
# Scan features for pictures
  for feature in geojson["features"]:
    try:
      ulsp_type = feature["properties"]["ulsp_type"]
      if ( ulsp_type == "Percorso" ):
        url = urlparse(feature["properties"]["Foto accesso"])
      else:
        url = urlparse(feature["properties"]["Foto"])
      try:
        photo_filename = rn + vignetteNameFromURL(url)
        if ( os.path.exists(photo_filename) ):
          print("   "+feature["properties"]["Titolo"] + " (" + feature["properties"]["ulsp_type"] +")" + ": immagine già presente");
        else:
          print("   Scarico l'immagine di " + feature["properties"]["Titolo"])
          grab_image(feature["properties"]["Foto"],photo_filename)
      except:
        warnprint(feature["properties"]["Titolo"] + ' - Attributo Foto vuoto o errato')
    except KeyError:
      try:
        failprint("    No vignette URL for " + feature["properties"]["Titolo"] + " (" + feature["properties"]["ulsp_type"] +")")
      except KeyError as ke:
        failprint("   " + feature["properties"]["Titolo"] + "- Feature mal formattata: non trattata ("+ke.args[0]+")")
        continue
    except Exception as e:
      failprint("   " + feature["properties"]["Titolo"] + "- Feature mal formattata: non trattata ("+e+")")
      continue

####
# Generazione dei QRtag (segnalazione)
####      
def generate_qrtags():
  print("\u2022 Genero i QRtags")
#    logo = Image.open("logoEle_v2.2_small.png").convert("RGBA") 
  for feature in geojson["features"]:
    try:
      ulsp_type = feature["properties"]["ulsp_type"]
      if ( ulsp_type == "QRtag" ):
        if not os.path.isdir(rn+"/qrtags"):
          print("   Creo una cartella per i QRtag")
          os.makedirs(rn+"/qrtags")
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
        testo += testo+"\n"+config["weburl"]+"/"+rn+"/"+fid
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
        
        canvas.save(rn+"/qrtags/"+fid+".png")
    except KeyError as ke:
      failprint("   Feature mal formattata: non trattata ("+ke.args[0]+")")
      continue

####
# Genera il file README.md
####
def generate_readme():
  print("\u2022 Genero il readme per il dataset")
  try:
    with open(rn+"/README.md", 'w', encoding='utf-8') as f:
      f.write("# " + rn + " (")
      try:
        if geojson["properties"]["umapKey"] == "": raise KeyError("Link alla mappa non definito")
        f.write("[mappa](" + geojson["properties"]["umapKey"]+")")
      except:
        f.write("mappa non collegata")
      f.write(")\n")
      print(geojson)
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
    # if qrtag display the tag
        if ( ulsp_type == "QRtag" ):
          try:
            fid = feature["properties"]["fid"]
            f.write("[<img src='qrtags/"+fid+".png' width='150'/>](qrtags/"+fid+".png) ")
            fotourl = urlparse(feature["properties"]["Foto"])
            vignette = vignetteNameFromURL(fotourl)
            f.write("[<img src='"+vignette+"' width='250'/>]("+vignette+") \n\n")
          except KeyError:
            warnprint("   Non è disponibile l'immagine per il QRtag " + feature["properties"]["Titolo"])
            f.write("*Nessuna immagine* \n\n")
            raise KeyError
          except IndexError:
            warnprint("   Non è disponibile l'immagine per il QRtag "+ feature["properties"]["ulsp_type"] + " " + feature["properties"]["Titolo"])
            f.write("*Nessuna immagine* \n\n")
          except ValueError as e:
            warnprint(str(e))
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
              warnprint("   Non è disponibile l'immagine per la feature " + feature["properties"]["Titolo"])
              f.write("*Non è disponibile l'immagine relativa alla feature* \n\n")
              continue
          try:
            vignette = vignetteNameFromURL(fotourl)
            f.write("[<img src='"+vignette+"' width='250'/>]("+vignette+") \n\n")
          except IndexError:
            warnprint("   Non è disponibile l'immagine per "+ feature["properties"]["ulsp_type"] + " " + feature["properties"]["Titolo"])
            f.write("*Nessuna immagine* \n\n")
          except ValueError as e:
            warnprint(str(e))
          except UnboundLocalError:
            pass
        f.write("**"+feature["properties"]["Descrizione"]+"**"+"\n")
  except KeyError as ke:
    failprint("   GeoJSON mal formattato: non trattato ("+ke.args[0]+")")
    return False
        

# Read configuration and assets
with open("config.json") as json_data:
  config = json.load(json_data)
  
logo = Image.open("logoEle_v2.2_small.png").convert("RGBA")

emphprint("Clono il repository Master da github")
master = clone(config['master_repo'])

index = list(map(lambda obj: obj.name, list(master.walk(master.head.target))[0].tree)) #indexList()

diff = diffFiles(master)
emphprint("File modificati dall'ultima modifica del file .lastsync")
print(diff)

to_update = set(                                          						# elimina duplicati
              map(lambda fn: splitext(basename(fn))[0],            				# seleziona quello che precede il primo . (geojson e file nel sidecar)
              filter(lambda fn: fn in os.listdir(config['master_repo']),diff))	# seleziona solo i file ancora presenti nella directory
            )
emphprint("Dataset da aggiornare")
if to_update: print(to_update)
else: print("nessuno")

to_remove = set(
              map(lambda fn: splitext(basename(fn))[0],                 			# seleziona quello che precede il primo . (file nel sidecar)
              filter(lambda fn: fn not in os.listdir(config['master_repo']),diff))	# seleziona i file non più nella directory (rimossi)
            )
emphprint("Dataset da rimuovere")
if to_remove: print(to_remove)
else: print("nessuno")

# Create user with credentials
emphprint("Creo l'utente GitHub con credenziali base e delete")
user = create_user(config["access_token"])

# Get list of dataset repositories on github
dataset_repos = list(
                  filter(lambda r: r.startswith(("ULS","QRT","Fase1","Itinerario","ITN","test")), 	# select based on filename prefix
                    list(map(lambda s: s.name, user.get_repos()))									# all the repos of the user
                  )
                )
emphprint("Repository di dataset sull'account github")
print(dataset_repos)

# Get list of repositories with no remote
missing_repos=set(                                                    		# elimina duplicati (per file nel sidecar)
                filter(lambda r: r not in dataset_repos,               		# filtra quelli che non hanno repo su GitHub
                map(lambda fn: splitext(basename(fn))[0],diff)) 			 # elimina l'estensione dei file indice
              )
emphprint("Dataset da creare")
if missing_repos: print(missing_repos)
else: print("nessuno")

# Exit if no parameters
if not to_update.union(to_remove).union(missing_repos):
  emphprint("Nessun aggiornamento necessario")
  cleanup()
  exit()

###
# Visualizzazione azione e conferma
###
emphprint("Sommario delle operazioni sui dataset:")
for r in to_update.union(to_remove):
  print("\u2022 "+r, end="")
  if r in to_remove: print(" (da rimuovere)")
  elif r in missing_repos: print(" (da creare)")
  else: print(" (da aggiornare)")

l=input("Premi a capo per continuare, CTRL-C per interrompere: -> ")
if l != "":
  cleanup()
  exit()

###
# Rimozione dei repository relativi a geojson rimossi
###
for repo in to_remove:
  l='x'
  while l not in ['s','n']:
    warnprint("Autorizzi la rimozione del dataset "+repo+ " (s oppure n)?")
    l=input("-> ")
  if l == 's':
    print("Rimozione del dataset "+repo)
    try:
      list(filter(lambda r: r.name == repo, user.get_repos()))[0].delete()
    except:
      warnprint(f"Non riesco a rimuovere il repository {repo}")
  else:
    emphprint("La rimozione del dataset non verrà più riproposta e dovrà essere effettuata manualmente")

###
# Creazione dei repository relativi a nuovi geojson
###
for rn in missing_repos:
  emphprint("Creazione del repository "+rn)
  repo = user.create_repo(rn, description = rn + ": dataset geolocalizzato del progetto Underlandscape" )
  repo.create_file("README.md", "Create empty README", "# " + rn)

###
# Ricalcolo e aggiornamento dei repository modificati
###
for fn in to_update:
  dataset_name = splitext(basename(fn))[0]
  sync_repo(dataset_name, config, logo)

# Registra il timestamp
print("Modifico il file .lastsync")
with open(f"{config['master_repo']}/.lastsync", mode='a') as f:
    f.write(f'{datetime.datetime.utcnow():%Y-%m-%d %H:%M:%S UTC}\n')

# Aggiorno il repository Master su github
push_repo(master, config["username"], config["access_token"] )

# Rimozione della directory Master
cleanup()

# Registra l'elenco dei dataset modificati per passarlo a umap-sync
updates=' '.join(to_update.union(to_remove).union(missing_repos))
print(f"Dataset da aggiornare: {updates}")
with open(r"../update_list", 'a') as f:
  f.write(f" {updates}")






