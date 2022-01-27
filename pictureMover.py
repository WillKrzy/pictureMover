import os
import datetime
import queue
import shutil
import threading
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

def main() :
  root = Tk()
  root.geometry("500x80")
  root.title("Picture Mover")
  frame = ttk.Frame(root)
  frame.grid(column=0, row=0, sticky=(N,W,E,S))
  root.columnconfigure(0, weight=1)
  root.rowconfigure(0, weight=1)

  originalDirectoryPath = StringVar()
  ttk.Entry(frame, textvariable=originalDirectoryPath, width=50).grid(row=1, column=1, columnspan=3)
  ttk.Button(frame, text="Existing Photo Directory", command=lambda:getDirectory(originalDirectoryPath)).grid(row=1, column=4)

  newDirectoryPath = StringVar()
  ttk.Entry(frame, textvariable=newDirectoryPath, width=50).grid(row=2, column=1, columnspan=3)
  ttk.Button(frame, text="Choose Destination", command=lambda:getDirectory(newDirectoryPath)).grid(row=2, column=4)

  ttk.Button(frame, text="Copy", command=lambda:checkDirectories(originalDirectoryPath.get(), newDirectoryPath.get(), frame)).grid(row=3, column=2, columnspan=2)
  root.mainloop()

def getDirectory(stringVar) :  
  path = filedialog.askdirectory()
  stringVar.set(path)

def checkDirectories(source, destination, parent) :
  if (not os.path.isdir(source)) :
    messagebox.showerror(title="Error", message=f"{source} is not a directory")
  elif (not os.path.isdir(destination)) :
    messagebox.showerror(title="Error", message=f"{destination} is not a directory")
  elif (isDestinationSubfolderOfSource(source, destination)) :
    messagebox.showerror(title="Error", message="Destination of copy cannot be a subfolder of the source folder")
  else :
    totalFiles = countAllFilesToCopy(source)
    processedFiles = IntVar()
    progressBar = ttk.Progressbar(parent, length=200, orient=HORIZONTAL, mode='determinate', variable=processedFiles, maximum=totalFiles)
    progressBar.grid(row=1, column=1)
    progressBar.start()
    myqueue = queue.LifoQueue()
    thread = threading.Thread(target=lambda:copyFiles(source, destination, myqueue))
    thread.start()
    progressBar.after(100, lambda:poll(progressBar, myqueue, processedFiles, totalFiles, thread))

def poll(progressbar, queue, progress, total, thread) :
  count = queue.get()
  print(count)
  progress.set(count)
  if count == total :
    thread.join()
    progressbar.stop()
    progressbar.destroy()
    print('Done')
  else :
    progressbar.after(100, lambda:poll(progressbar, queue, progress, total, thread))


def isDestinationSubfolderOfSource(source, destination) :
  commonPrefix = os.path.commonprefix([source, destination])
  return commonPrefix == source

def countAllFilesToCopy(source) :
  totalFiles = 0
  for _, _, files in os.walk(source):
    for file in files :
      if file.lower().endswith(tuple(allFileTypes)) :
        totalFiles += 1
  return totalFiles

def copyFiles(source, destination, queue) :
  filesProcessed = 0
  with os.scandir(source) as iterator:
    for item in iterator:
        if item.is_dir():
            filesProcessed = handleFolder(item, destination, filesProcessed, queue)

def handleFolder(folder, destination, filesProcessed, queue) :
    with os.scandir(folder.path) as iterator:
        for item in iterator:
            if item.is_file() and item.name.lower().endswith(tuple(allFileTypes)) :
                filesProcessed = handleFile(item, destination, filesProcessed, queue)
            elif item.is_dir():
                handleFolder(item, destination, filesProcessed, queue)
    return filesProcessed

def handleFile(file, destination, filesProcessed, queue):
    stat_result = file.stat()
    stamp = stat_result.st_mtime
    date = datetime.datetime.fromtimestamp(stamp)
    year = date.strftime("%Y")
    month = date.strftime("%B")
    day = date.strftime("%d")
    path = f"{destination}" + "\\" + year + "\\" + month + "\\" + day + "\\"
    if file.name.lower().endswith(tuple(rawFileTypes)) :
        path = path + "\\RAW\\"
    if  not os.path.exists(path) :
        os.makedirs(path)    
    shutil.move(file.path, path + file.name)
    filesProcessed += 1
    queue.put(filesProcessed)
    return filesProcessed

allFileTypes = ['jpg', 'jpeg', 'png', 'nef', 'cr2']
rawFileTypes = ['nef', 'cr2']
main()