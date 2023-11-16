# -*- coding: utf-8 -*-
# examples/pynoverb_gui.py
#
# -------------------------------------------------
# Graphical user interface for pynoverb
#
# With this program you can :
# - Adjust room dimensions and wall properties
# - Select listener properties
# - Graphically create source points
# - Export binaural impulse responses for each
#   source point in a chosen directory
# -------------------------------------------------
#
# Example program for the pynoverb package
# (c) OD - 2023
# https://github.com/odoare/pynoverb

import sys
sys.path.insert(0, "../pynoverb")

CANVAS_SIZE = 400
global selind
global f

import tkinter as tk
from tkinter import ttk, filedialog
from pynoverb import rev3_binau_hfdamp_par, rev3_binau_hfdamp_perwalldamp_par, get_n_from_r
import numpy as np
from pynoverb import writewav24
import os
import time

nc = int(np.ceil(os.cpu_count()/3))
print(nc)

def get_room_dimensions():
    return np.array([float(size_entries[label].get()) for label in size_labels])

def get_listener_pos():
    return np.array([float(listener_entries[label].get()) for label in listener_labels])

def get_wall_absorbtion():
    out = np.fromstring(damping_entry.get(),sep=',')
    if len(out)!=1 and len(out)!=6:
        out = None
    elif len(out)==1:
        out = out[0]
    return out

def get_wall_hfdamping():
    return float(hfdamping_entry.get())

def calculate_and_export():
    l = get_room_dimensions()
    x = get_listener_pos()
    a = get_wall_absorbtion()
    if type(a)==type(None):
        infos_string.set("Problem parsing wall damping entry. \n Has to be a single float or six flots, comma separated.")
        return None
    r = 1 - a
    d = get_wall_hfdamping()
    n = get_n_from_r(r)
    basefich = directory_entry.get()+'/'+filename_entry.get()
    t = time.time()
    for ind, s in enumerate(source_listbox.get(0, tk.END)):
        infos_string.set("Calculating and exporting IRs for source "+str(ind))
        s = np.array([float(val) for val in s])  # Convert the string values to float
        source_listbox.selection_set((ind,))
        update_selected_entry()
        root.update()
        if type(r)==np.float64:
            impl,impr = rev3_binau_hfdamp_par(n=n,l=l,x=x,s=s,r=r,d=d,nc=nc)
        elif type(r)==np.ndarray:
            impl,impr = rev3_binau_hfdamp_perwalldamp_par(n=n,l=l,x=x,s=s,r=r,d=d,nc=nc)
        fichier = basefich+'_'+str(ind)+'.wav'
        writewav24(fichier,44100,np.array([impl,impr]).T)
    t = time.time() - t
    infos_string.set("Calculation of "+str(len(source_listbox.get(0, tk.END)))+" IRs done in "+str(t)+"s." )
    write_state_to_file(basefich+".txt")
    pass

def browse_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, directory_path)

def write_state_to_file(filename:str):
    with open(filename, "w") as file1:
        # Writing data to a file
        file1.write("# Pynoverb data \n")
        file1.write("# ------------- \n")
        file1.write("\n")
        file1.write("# Room dimensions \n")
        for a in get_room_dimensions():
            file1.write(str(a)+" ")
        file1.write("\n\n")
        file1.write("# Wall absorbtion \n")
        file1.write(str(get_wall_absorbtion())+"\n")
        file1.write("\n")
        file1.write("# High frequency damping \n")
        file1.write(str(get_wall_hfdamping())+"\n")
        file1.write("\n")
        file1.write("# Listener position \n")
        for a in get_listener_pos():
            file1.write(str(a)+" ")
        file1.write("\n\n")
        file1.write("# Sources positions \n")
        for i,s in enumerate(source_listbox.get(0, tk.END)):
            file1.write(str(i)+": ")
            for a in s:
                file1.write(str(a)+" ")
            file1.write("\n")

def quit_app():
    root.quit()

def no_tab(event):
    return 'break'

def swapy(y):
    return CANVAS_SIZE-y

def update_canvas(event=None):
    global f
    # Get the size, source position, and listener position values
    size_values = [float(size_entries[label].get()) for label in size_labels]
    source_values = [float(source_entries[label].get()) for label in source_labels]
    listener_values = [float(listener_entries[label].get()) for label in listener_labels]

    # Clear the canvas
    canvas.delete("all")

    # Draw the parallelepiped (box)
    x, y, z = size_values
    maxlength = max(x,z+y)
    f = (CANVAS_SIZE-50)/maxlength

    # Draw room rectangles
    canvas.create_rectangle(20, swapy(20), 20 + x*f, swapy(20+y*f), outline="black")
    canvas.create_rectangle(20, swapy(40+y*f), 20 + x*f, swapy(40+(z+y)*f), outline="black")

    # Draw arrow axes
    canvas.create_line(20, swapy(20), 20+f, swapy(20), arrow=tk.LAST)
    canvas.create_line(20, swapy(20), 20, swapy(20+f), arrow=tk.LAST)
    canvas.create_line(20, swapy(40+f*y), 20+f, swapy(40+f*y), arrow=tk.LAST)
    canvas.create_line(20, swapy(40+f*y), 20, swapy(40+y*f+f), arrow=tk.LAST)
    canvas.create_text(20+f, swapy(8), text="x", font=('Times 14 italic'))
    canvas.create_text(8, swapy(20+f), text="y", font=('Times 14 italic'))
    canvas.create_text(20+f, swapy(28+y*f), text="x", font=('Times 14 italic'))
    canvas.create_text(8, swapy(30+y*f+f), text="z", font=('Times 14 italic'))

    # Draw the source circle in the xy box
    canvas.create_oval(20 + source_values[0]*f - 8, swapy(20+source_values[1]*f - 8), 20 + source_values[0]*f + 8, swapy(20+source_values[1]*f + 8),outline='red')
    # Draw the listener circle in xy box
    canvas.create_oval(20 + listener_values[0]*f - 8, swapy(20+listener_values[1]*f - 8), 20 + listener_values[0]*f + 8, swapy(20+listener_values[1]*f + 8), fill="blue")
    # Draw the source circle in the xz box
    canvas.create_oval(20 + source_values[0]*f - 8, swapy(40+(source_values[2]+y)*f - 8), 20 + source_values[0]*f + 8, swapy(40+(source_values[2]+y)*f + 8),outline='red')
    # Draw the listener circle in xz box
    canvas.create_oval(20 + listener_values[0]*f - 8, swapy(40+(listener_values[2]+y)*f - 8), 20 + listener_values[0]*f + 8, swapy(40+(listener_values[2]+y)*f + 8), fill="blue")

    for ind, entry in enumerate(source_listbox.get(0, tk.END)):
        entry = [float(val) for val in entry]  # Convert the string values to float
        #canvas.create_oval(20 + entry[0]*f - 4, swapy(20+entry[1]*f - 4), 20 + entry[0]*f + 4, swapy(20+entry[1]*f + 4), fill="red")
        #canvas.create_oval(20 + entry[0]*f - 4, swapy(30+(entry[2]+y)*f - 4), 20 + entry[0]*f + 4, swapy(30+(entry[2]+y)*f + 4), fill="red")
        canvas.create_text(20 + entry[0]*f, swapy(18+entry[1]*f), text=str(ind), font=('Helvetica 12 bold'))
        canvas.create_text(20 + entry[0]*f, swapy(38+(entry[2]+y)*f ), text=str(ind), font=('Helvetica 12 bold') )

    # Update the selected entry in the scrolled listbox
    selected_index = source_listbox.curselection()
    if selected_index:
        selected_entry = list(source_listbox.get(selected_index[0]))
        for i, label in enumerate(source_labels):
            selected_entry[i] = source_entries[label].get()
        source_listbox.delete(selected_index)
        source_listbox.insert(selected_index, selected_entry)

def delete_entry(event=None):
    global selind
    # selected_index = source_listbox.curselection()
    # print(selected_index)
    # print(selind)
    if selind:
        source_listbox.delete(selind)
        # Update canvas after deleting an entry
    update_canvas()

def update_selected_entry(event=None):
    # print('In update_selected_entry')
    global selind
    selected_index = source_listbox.curselection()
    selind = selected_index
    # print('selind')
    # print(selind)
    if selected_index:
        selected_entry = source_listbox.get(selected_index[0])
        for i, label in enumerate(source_labels):
            source_entries[label].delete(0, tk.END)
            source_entries[label].insert(0, selected_entry[i])
    update_canvas()


def add_entry(event):
    # print('In add_entry')
    global f
    x, y = event.x - 20, event.y + 20
    source_listbox.insert(tk.END, (round(x/f,2), round(swapy(y)/f,2), round(float(size_entries["z"].get())/2,2) ) )
    source_listbox.selection_set((source_listbox.size()-1,))
    update_selected_entry()

def modify_entry(event=None):
    # print('In modify_entry')
    global selind
    source_values = [float(source_entries[label].get()) for label in source_labels]
    # print('selind')
    # print(selind)
    if selind:
        source_listbox.delete(selind)
        source_listbox.insert(selind, source_values)
        # print (source_values)
    update_canvas()

def show_damping_message(event=None):
    infos_string.set("""Enter one value, or a list of 6 numbers, comma separated
                     The smaller is this value the longer is the calculation""")

def hide_damping_message(event=None):
    infos_string.set("")

def show_directory_message(event=None):
    infos_string.set("The directory where the IRs will be exported")

def hide_directory_message(event=None):
    infos_string.set("")

def show_canvas_message(event=None):
    infos_string.set("Left click in the xy zone to add a new source")

def hide_canvas_message(event=None):
    infos_string.set("")

def show_source_message(event=None):
    infos_string.set("Select a source to delete with DEL or modify below")

def hide_source_message(event=None):
    infos_string.set("")

def show_filename_message(event=None):
    infos_string.set("Write here the base name of all file names")

def hide_filename_message(event=None):
    infos_string.set("")

# Create the main window
root = tk.Tk()
root.title("Pynoverb simple GUI")

# Create a frame for the canvas and list box
canvas_frame = tk.Frame(root)
canvas_frame.grid(row=0, column=0, padx=10, pady=0, sticky="n")
ttk.Label(canvas_frame, text="Room").grid(row=0, column=0, padx=5, pady=5)

# Create a canvas for drawing
canvas = tk.Canvas(canvas_frame, width=CANVAS_SIZE, height=CANVAS_SIZE, bg='white')
canvas.grid(row=1, column=0, padx=5, pady=5)
canvas.bind("<Button-1>", add_entry)
canvas.bind("<Enter>", show_canvas_message)
canvas.bind("<Leave>", hide_canvas_message)

# Create a frame for list box
list_frame = tk.Frame(canvas_frame)
list_frame.grid(row=1, column=1, padx=10, pady=5, sticky="n")
ttk.Label(list_frame, text="Sources list").grid(row=0, column=0, padx=5, pady=5)

# Create a ScrolledListBox for the source entries
source_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE,height=20)
source_listbox.grid(row=1, column=0, padx=5, pady=5)
source_listbox.bind('<<ListboxSelect>>', update_selected_entry)
source_listbox.bind('<Delete>', delete_entry)
source_listbox.bind('<Enter>', show_source_message)
source_listbox.bind('<Leave>', hide_source_message)

# Create a frame for the size and listener
sizelist_frame = tk.Frame(root)
sizelist_frame.grid(row=1, column=0, padx=0, pady=0, sticky="w")
ttk.Label(sizelist_frame, text="").grid(row=0, column=0, padx=5, pady=5)

# Create a frame for the "Size" group of controls
size_frame = ttk.Frame(sizelist_frame)
size_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")
ttk.Label(size_frame, text="Room dimensions").grid(row=0, column=1, padx=5, pady=5, sticky="W")

# Create three number entries for "Size" with default values
size_entries = {}
size_labels = ["x", "y", "z"]
default_size_values = [4, 3, 2.5]
for i, label in enumerate(size_labels):
    ttk.Label(size_frame, text=label).grid(row=i+1, column=0, padx=5, pady=5, sticky="W")
    size_entries[label] = ttk.Entry(size_frame)
    size_entries[label].insert(0, str(default_size_values[i]))
    size_entries[label].grid(row=i+1, column=1, padx=5, pady=5)
    size_entries[label].bind("<FocusOut>", update_canvas)
    size_entries[label].bind("<Return>", update_canvas)

# Create a frame for the "Listener position" group of controls
listener_frame = ttk.Frame(sizelist_frame)
listener_frame.grid(row=1, column=1, padx=10, pady=10, sticky="w")
ttk.Label(listener_frame, text="Listener position").grid(row=0, column=1, padx=5, pady=5, sticky="W")

# Create three number entries for "Listener position" with default values
listener_entries = {}
listener_labels = ["x", "y", "z"]
default_listener_values = [2, 1, 2]
for i, label in enumerate(listener_labels):
    ttk.Label(listener_frame, text=label).grid(row=i+1, column=0, padx=5, pady=5, sticky="W")
    listener_entries[label] = ttk.Entry(listener_frame)
    listener_entries[label].insert(0, str(default_listener_values[i]))
    listener_entries[label].grid(row=i+1, column=1, padx=5, pady=5)
    listener_entries[label].bind("<FocusOut>", update_canvas)
    listener_entries[label].bind("<Return>", update_canvas)


# Create a frame for the "Source position" group of controls
source_frame = ttk.Frame(sizelist_frame)
source_frame.grid(row=1, column=2, padx=10, pady=10, sticky="w")
ttk.Label(source_frame, text="Source position").grid(row=0, column=1, padx=5, pady=5, sticky="W")

# Create three number entries for "Source position" with default values
source_entries = {}
source_labels = ["x", "y", "z"]
default_source_values = [2, 2, 2]
for i, label in enumerate(source_labels):
    ttk.Label(source_frame, text=label).grid(row=i+1, column=0, padx=5, pady=5, sticky="W")
    source_entries[label] = ttk.Entry(source_frame)
    source_entries[label].insert(0, str(default_source_values[i]))
    source_entries[label].grid(row=i+1, column=1, padx=5, pady=5)
    #source_entries[label].bind("<FocusOut>", modify_entry)
    source_entries[label].bind("<Return>", modify_entry)
    source_entries[label].bind('<Tab>', no_tab)

# Create a frame for the room properties
room_frame = ttk.Frame(root)
room_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")

# Create a label for the damping entry

# Create an entry widget for the room damping
damping_label = ttk.Label(room_frame, text="Wall absorbtion [0.01 ... 0.5]")
damping_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
damping_label.bind("<Enter>", show_damping_message)
damping_label.bind("<Leave>", hide_damping_message)
damping_entry = ttk.Entry(room_frame)
damping_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
damping_entry.insert(0, str(0.1))
damping_entry.bind("<Enter>", show_damping_message)
damping_entry.bind("<Leave>", hide_damping_message)
ttk.Label(room_frame, text="HF damping [0 ... 1]").grid(row=0, column=2, padx=5, pady=5, sticky="w")
hfdamping_entry = ttk.Entry(room_frame)
hfdamping_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
hfdamping_entry.insert(0, str(0.1))

# Create a frame for the buttons
buttons_frame = ttk.Frame(root)
buttons_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="e")

# Create a label for informations
infos_string = tk.StringVar()
info_label = ttk.Label(buttons_frame, textvariable=infos_string)
info_label.grid(row=0, column=0, padx=5, pady=5)

# Create the "export" button
export_button = ttk.Button(buttons_frame, text="Calculate and export IRs", command=calculate_and_export)
export_button.grid(row=0, column=1, padx=5, pady=5)

# Create the "quit" button
quit_button = ttk.Button(buttons_frame, text="Quit", command=quit_app)
quit_button.grid(row=0, column=2, padx=5, pady=5)

# Create a frame for directory and filename selection
file_frame = ttk.Frame(root)
file_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="w")

# Create a "Browse" button for directory selection
browse_button = ttk.Button(file_frame, text="Browse for directory", command=browse_directory)
browse_button.grid(row=0, column=0, padx=5, pady=5)
browse_button.bind("<Enter>",show_directory_message)
browse_button.bind("<Leave>",hide_directory_message)

# Create an entry widget for directory path
directory_entry = ttk.Entry(file_frame,width=50)
directory_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
directory_entry.bind("<Enter>",show_directory_message)
directory_entry.bind("<Leave>",hide_directory_message)

# Create a label for the filename entry
filename_label = ttk.Label(file_frame, text="Filename base")
filename_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
filename_label.bind('<Enter>',show_filename_message)
filename_label.bind('<Leave>',hide_filename_message)
# Create an entry widget for the filename
filename_entry = ttk.Entry(file_frame)
filename_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
filename_entry.bind('<Enter>',show_filename_message)
filename_entry.bind('<Leave>',hide_filename_message)

# Initialize the canvas
update_canvas()

# Start the main event loop
root.mainloop()
