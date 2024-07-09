#!/bin/bash
set -e

python3 dataset-sync.py
l=$(cat update_list)
if [ -n "update_list" ]
then
  python3 umap-sync.py $l
  rm update_list
  python3 summary-generation.py
  ./mk_dataset_page.sh
  echo "Ora, se sono stati aggiunti nuovi dataset, incorpora il file\n\
   'dataset_list.html' nella pagine dei dataset, sul sito"   
fi
