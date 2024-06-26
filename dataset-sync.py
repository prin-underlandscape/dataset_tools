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

from pprint import pprint

import sys 
sys.path.append('./libs')
import my_git
from colprint import emphprint, failprint, warnprint
from summary import generate_summary
from upload_list import UploadList;
from umap_generation import generate_umap;
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
  # Esce dal workspace
  os.chdir('..')
  shutil.rmtree(config['masterName'], ignore_errors=True)
  
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
def clone(repoName):
  if os.path.isdir(repoName):
    warnprint("Please remove "+repoName+" folder")
    exit()
  return pygit2.clone_repository("https://github.com/prin-underlandscape/"+repoName,repoName)

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
def diffFiles():
  result = []
  master = pygit2.Repository('.')
  commit = list(master.walk(master.head.target))[0]
  while ( any(commit.parents) ):
    diff = master.diff(commit, commit.parents[0])
    df = list(
            map(lambda obj: obj.delta.new_file.path, 
              filter(lambda obj: type(obj) == pygit2.Patch, diff))
        )
#    print(df)
    if ( ".lastsync" in df ): break
    result += df
    commit = commit.parents[0]
#    print("---")
#  pprint(list(set(result)))
  return list(set(result))

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
    
def push_repo(r):
# if list(map(lambda r: r.delta.new_file.path, r.diff("HEAD"))):
  # Build index and tree
  r.index.add_all()
  r.index.write()
  tree = r.index.write_tree()
  # Commit
  author = pygit2.Signature("Augusto Ciuffoletti", "augusto.ciuffoletti@gmail.com")
  message = input("Digita il messaggio di commit per il dataset: ")
  r.create_commit('HEAD', author, author, message,tree,[r.head.target])
  # Push
  # Build credentials
  credentials = pygit2.UserPass(config["username"], config["access_token"])
  # Push on "origin" remote with user credentials
  remote = r.remotes["origin"]
  remote.credentials = credentials
  callbacks=pygit2.RemoteCallbacks(credentials=credentials)
  remote.push(['refs/heads/main'],callbacks=callbacks)
#  else:
#    emphprint('   Non è necessario aggiornare questo dataset')

# Vero se il file f è nel sidecar del repository r
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
      try:
        if geojson["properties"]["Descrizione"] == "": raise KeyError("Descrizione vuota")
        f.write(geojson["properties"]["Descrizione"] + "\n")
      except:
        f.write("descrizione del dataset mancante\n")
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
with open("dataset-sync.config") as json_data:
  config = json.load(json_data)
  
logo = Image.open("logoEle_v2.2_small.png").convert("RGBA")

emphprint("Clono il repository Master da github")
clone(config['masterName'])
os.chdir(config['masterName'])

index = indexList()

emphprint("File nell'indice github del repository master")
print(index)

diffrepos = set(                                          # elimina duplicati
              map(lambda fn: fn.split('.')[0],            # seleziona quello che precede il primo . (file nel sidecar)
              filter(lambda fn: fn in os.listdir("."),diffFiles())) # seleziona solo i file ancora presenti nella directory
            )
emphprint("Dataset da aggiornare")
if diffrepos: print(diffrepos)
else: print("nessuno")

to_remove = set(
              map(lambda fn: fn.split('.')[0],                 # seleziona quello che precede il primo . (file nel sidecar)
              filter(lambda fn: fn not in os.listdir("."),diffFiles())) # seleziona i file non più nella directory (rimossi)
            )
emphprint("Dataset da rimuovere")
if to_remove: print(to_remove)
else: print("nessuno")

# Create user with credentials
emphprint("Accesso all'account GitHub")
user = create_user(config["access_token"])

# Get list of repositories on github
remote_repos = list(map(lambda s: s.name, user.get_repos()))
emphprint("Dataset sull'account github (compresi i dataset)")
print(list(filter(lambda r: r.startswith(("ULS","QRT","Fase1","Itinerario")), remote_repos)))

# Get list of repositories with no remote
missing_repos=set(                                                    # elimina duplicati
                filter(lambda r: r not in remote_repos,               # filtra quelli che non hanno repo su GitHub
                map(lambda fn: os.path.splitext(fn)[0],diffFiles()))  # elimina l'estensione dei file indice
              )
emphprint("Dataset da creare")
if missing_repos: print(missing_repos)
else: print("nessuno")

# Exit if no parameters
if not diffrepos.union(to_remove).union(missing_repos):
  emphprint("Nessun aggiornamento necessario")
#### Solo debug summary ##############################################
#  ul = UploadList()
#  generate_summary(ul)    # genera l'umap di sommario
#  ul.show()
#### FINE debug ######################################################
  cleanup()
  exit()
else:
  # Ask confirm
  emphprint("Sommario delle operazioni sui dataset:")
  for r in diffrepos.union(to_remove):
    print("\u2022 "+r, end="")
    if r in missing_repos: print(" (da creare)")
    elif r in to_remove: print(" (da rimuovere)")
    else: print(" (da aggiornare)")
  l=input("Premi a capo per continuare, CTRL-C per interrompere: -> ")
  if l != "":
    cleanup()
    exit()
  
###
# Creazione dei repository relativi a nuovi geojson
###
  for rn in missing_repos:
    emphprint("Creazione del repository "+rn)
    repo = user.create_repo(rn, description = rn + ": dataset geolocalizzato del progetto Underlandscape" )
    repo.create_file("README.md", "Create empty README", "# " + rn)

###
# Rimozione dei repository relativi a geojson rimossi
###
  rmlist = list( filter(lambda r: r.name in to_remove, user.get_repos()))
  for r in rmlist:
    l='x'
    while l not in ['s','n']:
      warnprint("Autorizzi la rimozione del dataset "+r.name+ " (s oppure n)?")
      l=input("-> ")
    if l == 's':
      print("Rimozione del dataset "+r.name)
      r.delete()
    else:
      emphprint("La rimozione del dataset non verrà più riproposta e dovrà essere effettuata manualmente")

###
# Ricalcolo e aggiornamento dei repository modificati
###
  ul = UploadList()
  for rn in diffrepos:
    ####
    # Ricalcolo e aggiornamento di un singolo dataset
    ####
    
    # Clona il repository dataset
    emphprint("Clono "+rn)
    if os.path.isdir(rn):
      shutil.rmtree(rn, ignore_errors=True)
    r = clone(rn)
    
    # Copia il geojson e i file nel sidecar nel repository clonato
    # I file nel sidecar hanno il nome che inizia con il nome del repo seguito da .
    files = list(filter(lambda fn: in_sidecar(fn,rn), os.listdir(".")))
    print("\u2022 Copio i file modificati:", end=" ")
    for f in files:
      try:
        print(f, end=" ")
        shutil.copyfile(f,rn+"/"+f)
      except:
        warnprint("Cannot copy file in cloned directory ("+f+")")
        continue
    print()

    # Carica in una variabile il geojson (una FeatureCollection)
    with open(rn+"/"+rn+".geojson") as json_data:
      geojson = json.load(json_data)
    
    sync_images()     # aggiorna le foto
    generate_umap(geojson, rn)   # crea il file umap
    if rn.startswith(("Itinerario")):
      generate_gpx(geojson, rn)   # crea il file umap
    generate_qrtags() # crea i tag delle feature con ulsp_type qrtag
    generate_readme() # crea i tag delle feature con ulsp_type qrtag
    #ul.log(rn+".umap",geojson['properties']['umapKey'])
    
    push_repo(r)
    shutil.rmtree(rn, ignore_errors=True)

generate_summary(ul)    # genera l'umap di sommario

ul.show()               # Visualizza l'elenco dei file da caricare nelle rispettive mappe umap

####
# Debug:
# -) togliere il commento dalla riga che segue
# -) clonare o fare pull dell'archivio master in una directory
#    diversa da questa (IMPORTANTE)
# -) effettuare una modifica in un file nell'archivio master così creato
#   (quale dipende dal problema riscontrato)
# -) fare commit nell'archivio master
# -) fare push nell'archivio master
# -) richiamare questa funzione, se necessario rimuovendo prima
#    il clone del repository master che viene creato in questa 
#    directory
# In questo modo l'esecuzione di questo programma può essere ripetuta
# senza dover ogni volta effettuare una modifica. Al termine della
# sessione di debug disabilitare la riga seguente e ripetere il comando
####
# exit() # debug only

# Registra il timestamp
print("Registro il timestamp")
with open(".lastsync", mode='a') as f:
    f.write(f'{datetime.datetime.utcnow():%Y-%m-%d %H:%M:%S UTC}\n')

# Aggiorno il repository Master su github
push_repo(pygit2.Repository('.'))

cleanup()




