##from latex2svg import latex2svg
##out = latex2svg(r'\( e^{i \pi} + 1 = 0 \)')
##print(out['depth'])  # baseline position in em
##print(out['svg'])  # rendered SVG

#!/usr/bin/env python3

#Remeber to do this: setx PATH "C:\Users\School\Downloads\python-3.9.0\Scripts"
#Then: pip install svglib
#Get MiKTeX

#latextopng: https://pypi.org/project/pnglatex/

##try:
##    import mymodule
##except ImportError as e:
##    pass  # module doesn't exist, deal with it.

importDir=r"C:\Users\School\Downloads"
exportDir=r"C:\Users\School\Downloads"
pdf2cairoPath=r"C:\Users\School\Downloads\PDFLaTeXEditor\poppler-0.68.0_x86\poppler-0.68.0\bin\pdftocairo.exe"
libPath=r"C:\Users\School\Downloads\PDFLaTeXEditor\lib"
#Make blank.pdf, icons local, in its own special folder (put path above)

Stringify=lambda string: '"'+string+'"'
Join=lambda directory,file: directory+r'\ '[:-1]+file

#Dependencies:

from tkinter import *
from tkinter import filedialog
import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
from PyPDF2 import PdfFileWriter, PdfFileReader
import shutil
import zipfile
from pathlib import Path
import subprocess
from PIL import Image, ImageTk
from functools import partial

tk = Tk()
filenameDisplay=StringVar(tk)
filenameDisplay.set("")
numPages=StringVar(value=["Page 1"])
tk.title("New Document - PDFLaTeXEditor")

def resetChdir():
    os.chdir(str(Path.home()))


def pdf2duo(file):
    newpath=Join(importDir,file.split(r'\ '[:-1])[-1][:-4])
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    f=open(file,"rb")
    inputpdf = PdfFileReader(f)

    global numPages
    numPages.set(["Page "+str(_+1) for _ in range(inputpdf.numPages)])

    with open(Join(newpath,"numPages.txt"),"w") as numPagesFile:
        numPagesFile.write(str(inputpdf.numPages))
        
    for i in range(inputpdf.numPages):
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        with open(Join(newpath,"page_"+str(i+1)+".pdf"), "wb") as outputStream:
            output.write(outputStream)

        #subprocess.call(Stringify(pdf2cairoPath)+" -png -singlefile "+Stringify(Join(newpath,"page_"+str(i+1)+".pdf"))+" "+Stringify(Join(newpath,"page_"+str(i+1)+".png")))
        #os.rename(Join(newpath,"page_"+str(i+1)+".png.png"),Join(newpath,"page_"+str(i+1)+".png"))
        subprocess.call(Stringify(pdf2cairoPath)+" -svg "+Stringify(Join(newpath,"page_"+str(i+1)+".pdf"))+" "+Stringify(Join(exportDir,"svg.svg")),creationflags=0x08000000)

        drawing = svg2rlg(Join(exportDir,"svg.svg"))
        renderPM.drawToFile(drawing, Join(newpath,"page_"+str(i+1)+".png"), fmt="PNG")
        os.remove(Join(exportDir,"svg.svg"))

        #Maybe convert to svg, get the size in pixels, scale the PNGs to that, and delete the svg.svg
                          
    f.close()
    
    os.chdir(importDir)
    shutil.make_archive(file.split(r'\ '[:-1])[-1][:-4],'zip',file.split(r'\ '[:-1])[-1][:-4])
    resetChdir()
    
    os.rename(file[:-4]+".zip",os.path.splitext(file[:-4]+".zip")[0]+".duo")
    shutil.rmtree(newpath)



size=(0,0)
def viewPage(file,num):
    os.rename(file,os.path.splitext(file)[0]+".zip")
    with zipfile.ZipFile(os.path.splitext(file)[0]+".zip") as z:
        with open(Join(exportDir,"svg_temp.png"), "wb") as f:
            f.write(z.read("page_"+str(num)+".png"))

    os.rename(os.path.splitext(file)[0]+".zip",os.path.splitext(file)[0]+".duo")
        
    img = Image.open(Join(exportDir,"svg_temp.png"))

    global size
    size = img.size

    pimg = ImageTk.PhotoImage(img)

    os.remove(Join(exportDir,"svg_temp.png"))

    
    return pimg

pimg=viewPage(Join(libPath,'blank.duo'),1)

frame = Canvas(tk, width=size[0], height=size[1])
frame.pack()
frame.create_image(0,0,anchor='nw',image=pimg)



pages = Canvas(tk)
images = Canvas(tk)


buttonWidth=5

#Make the listbox-- if the page clovked on is different than the one selected, change it

def LoadPic(file,scale,event=None):
    filename=Join(libPath,file)
    img=Image.open(filename)
    pass
    
def Load(event=None):

    global filename
    filename_temp=filedialog.askopenfilename(initialdir=importDir,filetypes=(("DUO files","*.duo"),("PDF files","*.pdf")))
    if(len(filename_temp)>0):
        filename = filename_temp
        filename = filename.replace(r"/ "[:-1],r"\ "[:-1])
        filenameDisplay.set(filename.split(r"\ "[:-1])[-1][:-3]+"duo")

def Open(event=None):
    
    global pimg
    if not os.path.isfile(os.path.splitext(filename)[0]+".duo"):
        pdf2duo(filename)
    else:
        os.rename(os.path.splitext(filename)[0]+".duo",os.path.splitext(filename)[0]+".zip")
        with zipfile.ZipFile(os.path.splitext(filename)[0]+".zip") as z:
            with z.open("numPages.txt") as f:
                for line in f:
                    global numPages
                    numPages.set(["Page "+str(_+1) for _ in range(int(line))])

        os.rename(os.path.splitext(filename)[0]+".zip",os.path.splitext(filename)[0]+".duo")
        #Make the svgs to the .duo file so viewPage calls from the svgs directly
        #Add all the stuff I need: blank pdf, icons, to seperate folder, and save the path as a variable above
    tk.title(str(filenameDisplay.get())+" - PDFLaTeXEditor")
    filenameDisplay.set("")
    pimg=viewPage(os.path.splitext(filename)[0]+".duo",1)
    frame = Canvas(tk, width=size[0], height=size[1])
    frame.place(x=tk.winfo_screenwidth()//2,y=0,anchor="n")
    frame.create_image(0,0,anchor='nw',image=pimg)
        
    pages.place(x=0,y=0,height=tk.winfo_screenheight(), width=tk.winfo_screenwidth()//2-size[0]//2)
    images.place(x=0,y=tk.winfo_screenwidth(),height=tk.winfo_screenheight(), width=tk.winfo_screenwidth()//2-size[0]//2)

    listbox.select_set(0)

def on_selection(event=None):
    global pimg
    pimg=viewPage(filename[:-3]+"duo",listbox.curselection()[0]+1)
    frame = Canvas(tk, width=size[0], height=size[1])
    frame.place(x=tk.winfo_screenwidth()//2,y=0,anchor="n")
    frame.create_image(0,0,anchor='nw',image=pimg)
        
    pages.place(x=0,y=0,height=tk.winfo_screenheight(), width=tk.winfo_screenwidth()//2-size[0]//2)

def OnEntryUpDown(self, event):
    selection = event.widget.curselection()[0]
    
    if event.keysym == 'Up':
        selection += -1

    if event.keysym == 'Down':
        selection += 1

    if 0 <= selection < event.widget.size():
        event.widget.selection_clear(0, tk.END)
        event.widget.select_set(selection)
        
loadOpen=Frame(pages)

Button(loadOpen, text='Load', command=Load,width=buttonWidth).pack(side=LEFT)
Button(loadOpen,text="Open",command=Open, width=buttonWidth).pack(side=LEFT)
Label(loadOpen,textvariable=filenameDisplay,relief="sunken",anchor="w").pack(side=LEFT,fill=BOTH,expand=1)
loadOpen.pack(side=TOP,anchor="w",fill=X)

pages.place(x=0,y=0,height=tk.winfo_screenheight(), width=tk.winfo_screenwidth()//2-size[0]//2)

List=Frame(pages)

listbox = Listbox(List,listvariable=numPages,exportselection=False,selectmode=SINGLE)
listbox.pack(side = LEFT, fill = BOTH,expand=1)

scrollbar = Scrollbar(List)
scrollbar.pack(side = LEFT, fill = BOTH)

listbox.config(yscrollcommand = scrollbar.set)
scrollbar.config(command = listbox.yview)

List.place(x=0, y=25,relwidth=1.0)
#Make images drag and drop-- https://stackoverflow.com/questions/37280004/drag-and-drop-widgets-tkinter
listbox.select_set(0)
listbox.bind('<<ListboxSelect>>',on_selection)
##listbox.bind('<Up>',OnEntryUpDown)
##listbox.bind('<Down>',OnEntryUpDown)



addRemove=Frame(images)
Button(addRemove,text='Add',width=buttonWidth).pack(side=LEFT)
addRemove.pack(side=TOP,anchor="e",fill=X)
images.place(x=tk.winfo_screenwidth(),y=0,height=tk.winfo_screenheight(), width=tk.winfo_screenwidth()//2-size[0]//2)


#.tli-- File format for the LaTeX. txt file: first line is latex formula, second is x, third is y, fourth is width (or maybe just condense it into one line with scaling factor instead), and fifth is height  
tk.mainloop()
