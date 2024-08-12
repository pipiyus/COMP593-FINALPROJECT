""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
import re
from datetime import datetime
import hashlib
import os
import sqlite3
import sys
import uuid
import re
import image_lib
import apod_api

# Full paths of the image cache folder and database
# - The image cache directory is a subdirectory of the specified parent directory.
# - The image cache database is a sqlite database located in the image cache directory.
script_dir = os.path.dirname(os.path.abspath(__file__))
image_cache_dir = os.path.join(script_dir, 'images')
image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Initialize the image cache
    init_apod_cache()

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        print(f"Setting desktop to {apod_info['file_path']}...success")
        image_lib.set_desktop_background_image(apod_info['file_path'])
    else:
        print("Failed to set desktop background.")

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    # TODO: Complete function body
    # Hint: The following line of code shows how to convert and ISO-formatted date string to a date object
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        try:
            # Attempt to parse the provided date string as ISO format
            apod_date = datetime.fromisoformat(date_str).date()
            
            # Validate that the date is not in the future
            if apod_date > datetime.today().date():
                print("Error: APOD date cannot be in the future")
                print("Script execution aborted")
                sys.exit(1)
        except ValueError as e:
            # Check if the error is due to an invalid date format
            if 'day' in str(e) or 'month' in str(e):
                print("Error: Invalid date format; day is out of range for month.")
            else:
                print(f"Error: Invalid date format; Invalid isoformat string: '{date_str}'.")
            print("Script execution aborted")
            sys.exit(1)
    else:
        apod_date = datetime.today().date()
    
    print(f"APOD date: {apod_date.isoformat()}")
    return apod_date

def init_apod_cache():
    """Initializes the image cache by:
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    """
    # TODO: Create the image cache directory if it does not already exist
    # TODO: Create the DB if it does not already exist
    print(f"Image cache directory: {image_cache_dir}")
    if not os.path.exists(image_cache_dir):
        os.makedirs(image_cache_dir)
        print("Image cache directory created.")
    else:
        print("Image cache directory already exists.")

    print(f"Image cache DB: {image_cache_db}")
    if not os.path.exists(image_cache_db):
        try:
            connection = sqlite3.connect(image_cache_db)
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS apod_data (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    explanation TEXT,
                    img_path TEXT,
                    SHA_hash TEXT
                )
            ''')
            connection.commit()
            connection.close()
            print("Image cache DB created.")
        except sqlite3.Error as e:
            print(f"Failed to create database: {e}")
    else:
        print("Image cache DB already exists.")
        print("Image cache DB already exists.")

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    print(f"Getting {apod_date.isoformat()} APOD information from NASA...", end="")
    apod_info = apod_api.get_apod_info(apod_date)
    if not apod_info:
        print("failed")
        print("Failed to get APOD information.")
        return 0
    print("success")

    image_url = apod_info['url']
    image_title = apod_info['title']
    print(f"APOD title: {image_title}")
    print(f"APOD URL: {image_url}")

    if not re.match(r'.*\.(jpg|png)$', image_url):
        print("The URL does not appear to be a direct image link.")
        return 0

    print(f"Downloading image from {image_url}...", end="")
    image_data = image_lib.download_image(image_url)
    if not image_data:
        print("failed")
        print("Failed to download image.")
        return 0
    print("success")

    sha256_hash = hashlib.sha256(image_data).hexdigest()
    print(f"APOD SHA-256: {sha256_hash}")

    apod_id = get_apod_id_from_db(sha256_hash)
    if apod_id:
        print("APOD image is already in cache.")
        return apod_id

    file_path = determine_apod_file_path(image_title, image_url)
    print(f"APOD file path: {file_path}")

    print(f"Saving image file as {file_path}...", end="")
    if not image_lib.save_image_file(image_data, file_path):
        print("failed")
        print("Failed to save image file.")
        return 0
    print("success")

    print("Adding APOD to image cache DB...", end="")
    if add_apod_to_db(image_title, apod_info['explanation'], file_path, sha256_hash):
        print("success")
        return get_apod_id_from_db(sha256_hash)
    else:
        print("failed")
        print("Failed to add APOD to DB.")
        return 0

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful. Zero, if unsuccessful       
    """
    # TODO: Complete function body
    try:
        connection = sqlite3.connect(image_cache_db)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO apod_data (id, title, explanation, img_path, SHA_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), title, explanation, file_path, sha256))
        connection.commit()
        apod_id = cursor.lastrowid
        connection.close()
        return apod_id
    except sqlite3.Error as e:
        print(f"Failed to add APOD to DB: {e}")
        return 0

def get_apod_id_from_db(sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    # TODO: Complete function body
    try:
        connection = sqlite3.connect(image_cache_db)
        cursor = connection.cursor()
        cursor.execute('''
            SELECT id FROM apod_data WHERE SHA_hash = ?
        ''', (sha256,))
        result = cursor.fetchone()
        connection.close()
        return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"Failed to get APOD ID from DB: {e}")
        return 0

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    # TODO: Complete function body
    # Hint: Use regex and/or str class methods to determine the filename.
    # Extract file extension from URL
    """Determines the path at which a newly downloaded APOD image must be saved."""
    file_extension = os.path.splitext(image_url)[1] if '.' in image_url else '.jpg'
    cleaned_title = re.sub(r'[^\w\s]', '', image_title).strip()
    cleaned_title = re.sub(r'\s+', '_', cleaned_title)
    file_name = f"{cleaned_title}{file_extension}"
    return os.path.join(image_cache_dir, file_name)

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # TODO: Query DB for image info
    # TODO: Put information into a dictionary
    try:
        connection = sqlite3.connect(image_cache_db)
        cursor = connection.cursor()
        cursor.execute('''
            SELECT title, explanation, img_path FROM apod_data WHERE id = ?
        ''', (image_id,))
        result = cursor.fetchone()
        connection.close()
        if result:
            return {
                'title': result[0],
                'explanation': result[1],
                'file_path': result[2],
            }
    except sqlite3.Error as e:
        print(f"Failed to get APOD info from DB: {e}")
    return {'file_path': 'TBD'}

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    # TODO: Complete function body
    # NOTE: This function is only needed to support the APOD viewer GUI
    try:
        connection = sqlite3.connect(image_cache_db)
        cursor = connection.cursor()
        cursor.execute('''
            SELECT title FROM apod_data
        ''')
        titles = [row[0] for row in cursor.fetchall()]
        connection.close()
        return titles
    except sqlite3.Error as e:
        print(f"Failed to get all APOD titles: {e}")
    return []

if __name__ == '__main__':
    main()