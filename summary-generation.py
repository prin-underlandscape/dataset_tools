import os;
import shutil;
import sys; 
sys.path.append('./libs');
import pygit2;
import json;

from summary import generate_summary;
from upload_list import UploadList;

# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
def failprint(s):
  print('\x1b[1;30;41m' + s + '\x1b[0m')
def emphprint(s):
  print('\x1b[1;30;42m' + s + '\x1b[0m')
def warnprint(s):
  print('\x1b[1;30;43m' + s + '\x1b[0m')

def clone(repoName):
  if os.path.isdir(repoName):
    warnprint("Please remove "+repoName+" folder")
    exit()
  return pygit2.clone_repository("https://github.com/prin-underlandscape/"+repoName,repoName)

with open("dataset-sync.config") as json_data:
  config = json.load(json_data)
  
emphprint("Clono il repository Master da github")
clone(config['masterName'])
os.chdir(config['masterName'])

ul = UploadList() 
generate_summary(ul)    # genera l'umap di sommario

os.chdir('..')
shutil.rmtree(config['masterName'], ignore_errors=True)
