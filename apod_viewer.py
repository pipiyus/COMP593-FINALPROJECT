import os
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import apod_desktop
import datetime

# Initialize the image cache
apod_desktop.init_apod_cache()

def fetch_apod():
    """Fetches the APOD image for the selected date."""
    selected_date = date_entry.get()
    try:
        # Validate the date format
        apod_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
        return
    
    try:
        # Add APOD to cache and get its ID
        apod_id = apod_desktop.add_apod_to_cache(apod_date)
        if apod_id == 0:
            raise Exception("APOD could not be added to the cache.")
        
        # Fetch APOD info from the cache
        apod_info = apod_desktop.get_apod_info(apod_id)
        
        if not os.path.exists(apod_info['file_path']):
            raise FileNotFoundError("Image file not found.")
        
        display_apod(apod_info)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch APOD: {e}")

def display_apod(apod_info):
    """Displays the APOD image and title."""
    image_path = apod_info['file_path']
    apod_title = apod_info.get('title', 'No Title')

    # Load and display the image
    img = Image.open(image_path)
    img.thumbnail((400, 300))
    img = ImageTk.PhotoImage(img)
    
    image_label.config(image=img)
    image_label.image = img

    # Display the title
    title_label.config(text=apod_title)

# Set up the main window
root = Tk()
root.title("APOD Viewer")
root.geometry('600x500')

# Date input
date_label = Label(root, text="Enter Date (YYYY-MM-DD):")
date_label.pack(pady=10)

date_entry = Entry(root)
date_entry.pack(pady=10)

fetch_button = Button(root, text="Fetch APOD", command=fetch_apod)
fetch_button.pack(pady=10)

# Image display
image_label = Label(root)
image_label.pack(pady=20)

# Title display
title_label = Label(root, text="", wraplength=500, justify="center")
title_label.pack(pady=10)

# Start the GUI loop
root.mainloop()
