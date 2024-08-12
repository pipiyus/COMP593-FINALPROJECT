'''
Library of useful functions for working with images.
'''

import requests
import ctypes
import os

def main():
    # TODO: Add code to test the functions in this module
    return

def download_image(image_url):
    """Downloads an image from a specified URL.

    DOES NOT SAVE THE IMAGE FILE TO DISK.

    Args:
        image_url (str): URL of image

    Returns:
        bytes: Binary image data, if succcessful. None, if unsuccessful.
    """
    print(f'Retrieving image from {image_url}...',  end='')
    response = requests.get(image_url)
    if response.status_code == requests.codes.ok:
        print('done')
        return response.content
    else:
        print('failed')
        print(f'Response code: {response.status_code} ({response.reason})')
    return

def save_image_file(image_data, image_path):
    """Saves image data as a file on disk.
    
    DOES NOT DOWNLOAD THE IMAGE.

    Args:
        image_data (bytes): Binary image data
        image_path (str): Path to save image file

    Returns:
        bool: True, if succcessful. False, if unsuccessful
    """
    
    try:
        print(f"Saving image to {image_path}...", end='')
        with open(image_path, 'wb') as f:
            f.write(image_data)
            print("Completed")
            return 
    except Exception as error:
        print(f"failed: {error}")
    return

def set_desktop_background_image(image_path):
    """Sets the desktop background image to a specific image.

    Args:
        image_path (str): Path of image file

    Returns:
        bytes: True, if succcessful. False, if unsuccessful        
    """
    
    print(f"Setting desktop to {image_path}...", end='')
    SPI_SETDESKWALLPPAPER = 20
    try:
        if ctypes.windll.user32.SystemParametersInfoW('SPI_SETDESKWALLPAPER', 0, image_path, 3):
            print("Completed")
            return 
        else:
            print("failed")
    except Exception as ex:
            print(f"failed: {ex}")
    return

def scale_image(image_size, max_size=(800, 600)):
    """Calculates the dimensions of an image scaled to a maximum width
    and/or height while maintaining the aspect ratio  

    Args:
        image_size (tuple[int, int]): Original image size in pixels (width, height) 
        max_size (tuple[int, int], optional): Maximum image size in pixels (width, height). Defaults to (800, 600).

    Returns:
        tuple[int, int]: Scaled image size in pixels (width, height)
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    # NOTE: This function is only needed to support the APOD viewer GUI
    resize_ratio = min(max_size[0] / image_size[0], max_size[1] / image_size[1])
    new_size = (int(image_size[0] * resize_ratio), int(image_size[1] * resize_ratio))
    return new_size

if __name__ == '__main__':
    main()