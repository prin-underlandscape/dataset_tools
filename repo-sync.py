from sys import argv, path
path.append('./libs')
from os.path import splitext, basename
from shutil import rmtree
from json import load
from PIL import Image

from my_git import clone
from colprint import emphprint
from sync_repo import sync_repo

# Verifica presenza argomenti
if len(argv) < 2:
  exit("Bisogna passare i dataset da sincronizzare")
# Caricamento della configurazione
with open("config.json") as json_data:
  config = load(json_data)
# Caricamento del logo
logo = Image.open("logoEle_v2.2_small.png").convert("RGBA")
# Clonazione Master
emphprint("Clono il repository Master da github")
clone(config['master_repo'])
# Sincronizzazione dei dataset passati come parametri
for fn in argv[1:]:
  dataset_name = splitext(basename(fn))[0]
  sync_repo(dataset_name, config, logo)
# Rimozione della directory Master
rmtree(config['master_repo'], ignore_errors=True)




