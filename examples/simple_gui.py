# import sys
# sys.path.insert(0, "..")

import tkinter as tk
from tkinter import ttk, filedialog
from pynoverb import rev3_binau, get_n_from_r
import numpy as np
# import matplotlib.pyplot as plt
from scipy.io import wavfile

CANVAS_SIZE = 400
global selind
global f

def calculate_and_export():
    l = np.array([float(size_entries[label].get()) for label in size_labels])
    x = np.array([float(listener_entries[label].get()) for label in listener_labels])
    r = 1 - float(damping_entry.get())
    n = int(get_n_from_r(r))
    for ind, s in enumerate(source_listbox.get(0, tk.END)):
        s = np.array([float(val) for val in s])  # Convert the string values to float
        print(str(ind)+'     '+str(s))
        source_listbox.selection_set((ind,))
        update_selected_entry()
        root.update()
        impl,impr = rev3_binau(n=n,l=l,x=x,s=s,r=r)
        # plt.plot(impl)
        # plt.plot(impr)
        fichier = directory_entry.get()+'/'+filename_entry.get()+'_'+str(ind)+'.wav'
        wavfile.write(fichier,44100,np.array([impl,impr]).T)
    # plt.show()
    pass

def browse_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, directory_path)

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
    canvas.create_rectangle(20, swapy(20), 20 + x*f, swapy(20+y*f), outline="black")
    canvas.create_rectangle(20, swapy(30+y*f), 20 + x*f, swapy(30+(z+y)*f), outline="black")
    # Draw the source circle in the xy box
    canvas.create_oval(20 + source_values[0]*f - 8, swapy(20+source_values[1]*f - 8), 20 + source_values[0]*f + 8, swapy(20+source_values[1]*f + 8),outline='red')
    # Draw the listener circle in xy box
    canvas.create_oval(20 + listener_values[0]*f - 8, swapy(20+listener_values[1]*f - 8), 20 + listener_values[0]*f + 8, swapy(20+listener_values[1]*f + 8), fill="blue")
    # Draw the source circle in the xz box
    canvas.create_oval(20 + source_values[0]*f - 8, swapy(30+(source_values[2]+y)*f - 8), 20 + source_values[0]*f + 8, swapy(30+(source_values[2]+y)*f + 8),outline='red')
    # Draw the listener circle in xz box
    canvas.create_oval(20 + listener_values[0]*f - 8, swapy(30+(listener_values[2]+y)*f - 8), 20 + listener_values[0]*f + 8, swapy(30+(listener_values[2]+y)*f + 8), fill="blue")

    for ind, entry in enumerate(source_listbox.get(0, tk.END)):
        entry = [float(val) for val in entry]  # Convert the string values to float
        #canvas.create_oval(20 + entry[0]*f - 4, swapy(20+entry[1]*f - 4), 20 + entry[0]*f + 4, swapy(20+entry[1]*f + 4), fill="red")
        #canvas.create_oval(20 + entry[0]*f - 4, swapy(30+(entry[2]+y)*f - 4), 20 + entry[0]*f + 4, swapy(30+(entry[2]+y)*f + 4), fill="red")
        canvas.create_text(20 + entry[0]*f, swapy(18+entry[1]*f), text=str(ind), font=('Helvetica 12 bold'))
        canvas.create_text(20 + entry[0]*f, swapy(28+(entry[2]+y)*f ), text=str(ind), font=('Helvetica 12 bold') )

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
    print(selind)
    if selind:
        source_listbox.delete(selind)
        # Update canvas after deleting an entry
    update_canvas()

def update_selected_entry(event=None):
    print('In update_selected_entry')
    global selind
    selected_index = source_listbox.curselection()
    selind = selected_index
    print('selind')
    print(selind)
    if selected_index:
        selected_entry = source_listbox.get(selected_index[0])
        for i, label in enumerate(source_labels):
            source_entries[label].delete(0, tk.END)
            source_entries[label].insert(0, selected_entry[i])
    update_canvas()


def add_entry(event):
    print('In add_entry')
    global f
    x, y = event.x - 20, event.y + 20
    source_listbox.insert(tk.END, (round(x/f,2), round(swapy(y)/f,2), round(float(size_entries["z"].get())/2,2) ) )
    source_listbox.selection_set((source_listbox.size()-1,))
    update_selected_entry()

def modify_entry(event=None):
    print('In modify_entry')
    global selind
    source_values = [float(source_entries[label].get()) for label in source_labels]
    print('selind')
    print(selind)
    if selind:
        source_listbox.delete(selind)
        source_listbox.insert(selind, source_values)
        print (source_values)
    update_canvas()


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

# Create a frame for list box
list_frame = tk.Frame(canvas_frame)
list_frame.grid(row=1, column=1, padx=10, pady=10, sticky="n")
ttk.Label(list_frame, text="Sources list").grid(row=0, column=0, padx=5, pady=5)

# Create a ScrolledListBox for the source entries
source_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE,height=20)
source_listbox.grid(row=1, column=0, padx=5, pady=5)
source_listbox.bind('<<ListboxSelect>>', update_selected_entry)
source_listbox.bind('<Delete>', delete_entry)

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

# Create a label for the filename entry
ttk.Label(room_frame, text="Wall damping (typical range [0.01,0.5])").grid(row=0, column=0, padx=5, pady=5, sticky="w")

# Create an entry widget for the room damping
damping_entry = ttk.Entry(room_frame)
damping_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
damping_entry.insert(0, str(0.1))

# Create a frame for the buttons
buttons_frame = ttk.Frame(root)
buttons_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="e")

# Create the "export" button
export_button = ttk.Button(buttons_frame, text="Calculate and export IRs", command=calculate_and_export)
export_button.grid(row=0, column=0, padx=5, pady=5)

# Create the "quit" button
quit_button = ttk.Button(buttons_frame, text="Quit", command=quit_app)
quit_button.grid(row=0, column=1, padx=5, pady=5)

# Create a frame for directory and filename selection
file_frame = ttk.Frame(root)
file_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="w")

# Create a "Browse" button for directory selection
browse_button = ttk.Button(file_frame, text="Browse for directory", command=browse_directory)
browse_button.grid(row=0, column=0, padx=5, pady=5)

# Create an entry widget for directory path
directory_entry = ttk.Entry(file_frame,width=50)
directory_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Create a label for the filename entry
ttk.Label(file_frame, text="Filename base").grid(row=1, column=0, padx=5, pady=5, sticky="w")

# Create an entry widget for the filename
filename_entry = ttk.Entry(file_frame)
filename_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Initialize the canvas
update_canvas()

# Start the main event loop
root.mainloop()
