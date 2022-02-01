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

  sourceDirectoryPath = StringVar()
  ttk.Entry(frame, textvariable=sourceDirectoryPath, width=50).grid(row=1, column=1, columnspan=3)
  ttk.Button(frame, text="Existing Photo Directory", command=lambda:get_directory(sourceDirectoryPath)).grid(row=1, column=4)

  destinationDirectoryPath = StringVar()
  ttk.Entry(frame, textvariable=destinationDirectoryPath, width=50).grid(row=2, column=1, columnspan=3)
  ttk.Button(frame, text="Choose Destination", command=lambda:get_directory(destinationDirectoryPath)).grid(row=2, column=4)

  ttk.Button(frame, text="Copy", command=lambda:copy(sourceDirectoryPath.get(), destinationDirectoryPath.get(), frame)).grid(row=3, column=2, columnspan=2)
  root.mainloop()

def get_directory(stringVar) :  
  path = filedialog.askdirectory()
  stringVar.set(path)

def copy(source, destination, parent) :
  if (not os.path.isdir(source)) :
    messagebox.showerror(title="Error", message=f"{source} is not a directory")
  elif (not os.path.isdir(destination)) :
    messagebox.showerror(title="Error", message=f"{destination} is not a directory")
  elif (is_destination_sub_folder_of_source(source, destination)) :
    messagebox.showerror(title="Error", message="Destination of copy cannot be a subfolder of the source folder")
  else :
    totalFiles = count_all_files_to_copy(source)
    processedFiles = IntVar()
    progressBar = ttk.Progressbar(parent, length=200, orient=HORIZONTAL, mode='determinate', variable=processedFiles, maximum=totalFiles)
    progressBar.grid(row=2, column=3)
    progressBar.start()
    progressQueue = queue.LifoQueue()
    thread = threading.Thread(target=copy_files, args=[source, destination, progressQueue])
    thread.start()
    progressBar.after(100, poll, progressBar, progressQueue, processedFiles, totalFiles, thread)

def poll(progressbar, queue, progress, total, thread) :
  count = queue.get()
  progress.set(count)
  if count == total :
    thread.join()
    progressbar.stop()
    progressbar.destroy()
    print('Done')
  else :
    progressbar.after(100, poll, progressbar, queue, progress, total, thread)

def is_destination_sub_folder_of_source(source, destination) :
  commonPrefix = os.path.commonprefix([source, destination])
  return commonPrefix == source

def count_all_files_to_copy(source) :
  totalFiles = 0
  for _, _, files in os.walk(source):
    for file in files :
      if file.lower().endswith(tuple(allFileTypes)) :
        totalFiles += 1
  return totalFiles

def copy_files(source, destination, queue) :
  filesProcessed = 0
  with os.scandir(source) as iterator:
    for item in iterator:
        if item.is_dir():
            filesProcessed = handle_folder(item, destination, filesProcessed, queue)

def handle_folder(folder, destination, filesProcessed, queue) :
    with os.scandir(folder.path) as iterator:
        for item in iterator:
            if item.is_file() and item.name.lower().endswith(tuple(allFileTypes)) :
                filesProcessed = handle_file(item, destination, filesProcessed, queue)
            elif item.is_dir():
                filesProcessed = handle_folder(item, destination, filesProcessed, queue)
    return filesProcessed

def handle_file(file, destination, filesProcessed, queue):
    stat_result = file.stat()
    timestamp = stat_result.st_mtime
    date = datetime.datetime.fromtimestamp(timestamp)
    year = date.strftime("%Y")
    month = date.strftime("%B")
    day = date.strftime("%d")
    path = f"{destination}" + "\\" + year + "\\" + month + "\\" + day + "\\"
    if file.name.lower().endswith(tuple(rawFileTypes)) :
        path = path + "\\RAW\\"
    if not os.path.exists(path) :
        os.makedirs(path)    
    shutil.move(file.path, path + file.name)
    filesProcessed += 1
    queue.put(filesProcessed)
    return filesProcessed

allFileTypes = ['jpg', 'jpeg', 'png', 'nef', 'cr2']
rawFileTypes = ['nef', 'cr2']
main()