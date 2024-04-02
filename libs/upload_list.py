from colprint import emphprint, failprint, warnprint

class UploadList:
  list = []

  def log(self,dataset, umapURL):
    self.list.append((dataset,umapURL))
  
  def show(self):
    warnprint("File da caricare nelle rispettive mappe umap")
    for (f,URL) in self.list:
      print("  File: " + f)
      print("  uMap URL: " + URL)
      emphprint(" - - -")
