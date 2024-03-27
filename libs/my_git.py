#import urllib.request
import os
import sys
#from urllib.parse import urlparse

# https://github.com/PyGithub/PyGithub
# more: https://stackoverflow.com/questions/49458329/create-clone-and-push-to-github-repo-using-pygithub-and-pygit2
from github import Github
from github import Auth
import pygit2

import sys 
sys.path.append('.')
import colprint

# Funziona
def create_user(token):
  with Github(token) as g:
    try:
      user = g.get_user()
#     pprint(user)
    except:
      colprint.failprint("Authentication failure")
      exit()
  return user
  
# Funziona
def clone(repoName):
  if os.path.isdir(repoName):
    colprint.warnprint("Please remove "+repoName+" folder")
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
    colprint.failprint("Pull fallita")
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
    colprint.emphprint('Nothing to commit on summary repository')
    
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
#    colprint.emphprint('   Non è necessario aggiornare questo dataset')
