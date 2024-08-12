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

from datetime import datetime
import hashlib
import os
import sqlite3
import sys
import uuid

import requests

import image_lib
import inspect
import apod_api

# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    """
    Main function to run the APOD script. It retrieves the APOD date from the command line,
    initializes the image cache, adds the APOD to the cache, retrieves its information,
    and sets it as the desktop background image.
    """
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_database_connection():
    """
    Establishes a connection to the image cache database.

    Returns:
        sqlite3.Connection: Connection object to the SQLite database
    """
    conn = sqlite3.connect(image_cache_db) 
    conn.row_factory = sqlite3.Row
    return conn

def get_apod_date():
    """
    Retrieves and validates the APOD date from the command line argument.
    If no date is provided, defaults to today's date. Validates that the date
    is not before the first APOD date or in the future.

    Returns:
        date: APOD date in YYYY-MM-DD format

    Raises:
        SystemExit: If the date is invalid or not provided, the script exits
    """
    today_date = datetime.today().date()
    last_date = datetime(1995, 6, 16).date()

    if len(sys.argv) > 1 and sys.argv[-1] != os.path.basename(__file__):
        apod_date = sys.argv[-1]
    else:
        apod_date = today_date

    try:
        apod_date = datetime.fromisoformat(apod_date).date()
        if apod_date < last_date:
            raise ValueError("APOD date cannot be before 1995-06-16")
        elif apod_date > today_date:
            raise ValueError("APOD date cannot be in the future")
    except ValueError as e:
        print(f"Error: Invalid date format; {e}")
        sys.exit("Script execution aborted")

    return apod_date

def get_script_dir():
    """
    Determines the directory path where this script is located.

    Returns:
        str: Full path of the directory containing this script
    """
    return os.path.dirname(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename))

def init_apod_cache(parent_dir):
    """
    Initializes the image cache by creating the cache directory and database if they do not exist.

    Args:
        parent_dir (str): Full path of the parent directory where the cache will be created
    """
    connection = sqlite3.connect(image_cache_db)
    cur = connection.cursor()

    with open("schema.sql", 'r') as f:
        query = f.read()
        cur.executescript(query)
        print("Schema applied successfully.")

    connection.commit()
    connection.close()

def add_apod_to_cache(apod_date):
    """
    Downloads the APOD image for a specified date, checks if it's already in the cache,
    and adds it if not.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: ID of the APOD in the cache, or 0 if unsuccessful
    """
    print("APOD date:", apod_date.isoformat())

    apod = apod_api.get_apod_info(apod_date)
    print("APOD response:", apod)  # Add this line to debug the API response

    # Continue with the existing code
    title = apod.get("title", "Unknown Title") 
    explanation = apod.get("explanation", "No Explanation Available")
    print(f"APOD title: {title}")

    image_url = apod_api.get_apod_image_url(apod)
    img_path = determine_apod_file_path(title, image_url)
    image_data = image_lib.download_image(image_url)

    if image_data is not None:
        image_hash = hashlib.sha256(image_data).hexdigest()
        print(f"APOD SHA-256: {image_hash}")

        apod_id = get_apod_id_from_db(image_hash)

        if apod_id:
            print("APOD image is already in cache.")
        else:
            print("APOD image is not already in cache.")
            image_lib.save_image_file(image_data, img_path)
            apod_id = add_apod_to_db(title, explanation, img_path, image_hash)
        return apod_id

def add_apod_to_db(title, explanation, file_path, sha256):
    """
    Adds APOD information to the image cache database.

    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Path where the APOD image is saved
        sha256 (str): SHA-256 hash of the APOD image

    Returns:
        int: ID of the newly added APOD record, or 0 if unsuccessful
    """
    try:
        print("Adding APOD to image cache DB...", end='')
        id = uuid.uuid4().hex

        conn = get_database_connection()
        conn.execute("INSERT INTO apod_data VALUES(?, ?, ?, ?, ?)", (id, title, explanation, file_path, sha256))
        conn.commit()
        conn.close()

        print("success")
        return id

    except Exception as e:
        print(str(e))
        return 0

def get_apod_id_from_db(image_sha256):
    """
    Retrieves the ID of an APOD record from the database based on its SHA-256 hash.

    Args:
        image_sha256 (str): SHA-256 hash of the APOD image

    Returns:
        int: ID of the APOD record in the database, or 0 if not found
    """
    conn = get_database_connection()

    apod_id = conn.execute("SELECT id FROM apod_data WHERE SHA_hash = ?", (image_sha256,)).fetchone()
    conn.close()

    return apod_id['id'] if apod_id else 0

def determine_apod_file_path(image_title, image_url):
    """
    Constructs the file path for saving the APOD image based on its title and URL.

    Args:
        image_title (str): Title of the APOD image
        image_url (str): URL of the APOD image

    Returns:
        str: Full path where the APOD image should be saved
    """
    extension = image_url.split('.')[-1]
    name = image_title.strip().replace(" ", "_").replace(":", "_") + f".{extension}"
    path = os.path.join(image_cache_dir, name)
    return path

def get_apod_info(image_id):
    """
    Retrieves APOD information (title, explanation, file path) from the database based on its ID.

    Args:
        image_id (int): ID of the APOD in the database

    Returns:
        dict: Dictionary containing the title, explanation, and file path of the APOD
    """
    conn = get_database_connection()
    data = conn.execute("SELECT title, explanation, img_path FROM apod_data WHERE id = ?", (str(image_id),)).fetchone()
    conn.close()

    return {
        'title': data["title"], 
        'explanation': data["explanation"],
        'file_path': data["img_path"],
    }

def get_all_apod_titles():
    """
    Retrieves a list of titles for all APODs stored in the cache.

    Returns:
        list: List of titles of all APOD images in the cache
    """
    # This function is only needed for the APOD viewer GUI, and its implementation is not provided
    return

if __name__ == '__main__':
    main()
