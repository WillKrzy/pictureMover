# pictureMover
Python program to move and organize photos

## Details
This GUI program was written with Tkinter in Python 3.10.0. This program moves photos from one directory to another while organizng them into a 

- year
    - month
        - date
            - raw file folder (\*.nef, \*.cr2)
            - (\*.jpeg,\*.jpg,\*.png)

structure.

# Important
***This program uses shutil.move which removes the file from the source folder. After this program completes there will only be 1 copy of your file and it will be in the destination*** 

Once more this program ***moves*** files it ***does not copy them***