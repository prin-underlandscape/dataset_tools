# Tool di gestione dei dataset

Al momento i tool per la gestione dei dataset sono quattro:

  * **dataset-sync.py**: esamina gli aggiornamenti recenti ai dataset nel repository master e sincronizza i repository dei dataset non aggiornati
  * **umap_sync.py**: sincronizza la mappa presente su umap.openstreetmap.org con il file umap contenuto nel repository di un dataset
  * **summary-generation.py**: genera la mappa di sommario e la pubblica su umap
  * **mk_dataset_page.sh.py**: genera l'elenco dei repository dei dataset in HTML per incorporarlo nella pagina del sito di Underlandscape

Lo script **make_all.sh** incorpora tutti e tre i passaggi: aggiornamento del dataset, sincronizzazione delle mappe, generazione della mappa di sommario e pagina dei dataset. Al termine dello script, se sono stati aggiunti nuovi dataset, il file *dataset_list.html* va incorporato nella pagina web dei dataset.

## umap_sync.py: il tool di sincronizzazione da dataset su github a mappe su umap

Il tool serve a sincronizzzare automaticamente un dataset Underlandscape su github con la mappa resa disponibile su umap.openstreetmap.fr.

Il tool utilizza la libreria selenium per python per automatizzare i passi per l'importazione del file umap contenuto nel repository github specifico del dataset nella mappa già associata al dataset.

Per utilizzare il tool è necessario installare il driver di un Web Browser. Su linux si può installare il package *chromium-driver*

```sudo apt install chromium-browser```

Evitare i driver installati con snap perché possono dipendere da librerie in versione difficile da reperire.

Al momento il tool *non* è in grado di generare la mappa: quindi la mappa sul servizio umap deve essere già stata creata ed associata.

Per ottenere questo risultato i passi possono essere i seguenti:

 1. creare una nuova mappa su umap.openstreetmap.fr
 2. scaricare localmente il file umap dal repository github
 3. importare nella nuova mappa il file umap e salvare il risultato
 4. copiare la URL della mappa
 5. nell'archivio Master dei dataset, editare con Off il repository e copiare nel campo opportuno la URL copiata al passo precedente
 6. fare push del repository Master csì modificato
 7. con il comando dataset-sync sincronizzare il repository specifico con il nuovo contenuto

### Installazione del tool

 1. Scaricare questo repository
 2. Nella directory generata creare un ambiente virtuale con il comando `python3 -m venv env`
 3. Avviare l'ambiente virtuale con il comando `source env/bin/activate`
 3. Installare le dipendenze con il comando `pip install -r requirements.txt`

### Uso del tool umap-sync.py

Il tool si utilizza come un comando Unix, nella directory in cui risiede, dopo aver avviato l'ambiente virtuale con `source env/bin/activate` il comando è: `python3 umap-sync.py <lista di dataset>`

La *<lista di dataset>* è una sequenza di nomi di dataset, ad esempio `ULS017_Riparo_della_Gabellaccia`. La stringa può o meno contenere una estensione o un percorso, che viene ignorata. Ad esempio si può scrivere `python3 umap-sync.py ../Master/Fase1*`, e verranno eleborati tutti i dataset che iniziano con `Fase1`. Comunque non verranno utilizzati i dati nei file nella directory `../Master`, ma solo i nomi dei file verrano utilizzati per interpolare i nomi dei dataset.

L'esecuzione del comando apre un browser in una finestra dedicata e richiede le credenziali per poter operare sulle mappe da aggiornare.

Quindi i dataset nell'elenco vengono elaborati consecutivamnte, per ciascuno aggiornando la mappa su umap.openstreetmap.fr con il file umap contenuto nel repository Master su GitHub. **Attenzione**: per questa operazione non vengono utilizzate copie di dataset eventualmente presenti sul PC.

Al termine dell'aggiornamento la mappa risultante rimane brevemente disponibile. Per quanto in questa fase sia possibile modificarla, non è consigliabile farlo perché la modifica andrebbe perduta alla successiva sincronizzazione. Se si riscontrano problemi modificare il dataset sul repository scaricamndo il repository Master e modificando il dataset con Off e ricaricando il repo Master.

Occasionalmente uno degli aggiornamenti può rimanere bloccato nella fase di salvataggio mostrando un popup "Problema nella risposta". In questo caso chiudere il popup e premere il tasto di salvataggio (oppure la combinazione CRTL-S)
