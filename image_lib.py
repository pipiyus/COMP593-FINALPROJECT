import requests
import ctypes
import os

def main():
    """Test the functions in this module."""
    # Add test code here if needed
    return

def download_image(image_url):
    """Downloads an image from a specified URL.

    DOES NOT SAVE THE IMAGE FILE TO DISK.

    Args:
        image_url (str): URL of image

    Returns:
        bytes: Binary image data, if successful. None, if unsuccessful.
    """
    print(f'Retrieving image from {image_url}...', end='')
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        print('done')
        return response.content
    except requests.RequestException as e:
        print(f'failed: {e}')
    return None

def save_image_file(image_data, image_path):
    """Saves image data as a file on disk.
    
    DOES NOT DOWNLOAD THE IMAGE.

    Args:
        image_data (bytes): Binary image data
        image_path (str): Path to save image file

    Returns:
        bool: True, if successful. False, if unsuccessful
    """
    print(f"Saving image to {image_path}...", end='')
    try:
        with open(image_path, 'wb') as f:
            f.write(image_data)
            print("Completed")
            return True
    except Exception as e:
        print(f"failed: {e}")
    return False

def set_desktop_background_image(image_path):
    """Sets the desktop background image to a specific image.

    Args:
        image_path (str): Path of image file

    Returns:
        bool: True, if successful. False, if unsuccessful
    """
    print(f"Setting desktop to {image_path}...", end='')
    SPI_SETDESKWALLPAPER = 20
    try:
        if ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3):
            print("Completed")
            return True
        else:
            print("failed")
    except Exception as e:
        print(f"failed: {e}")
    return False

def scale_image(image_size, max_size=(800, 600)):
    """Calculates the dimensions of an image scaled to a maximum width
    and/or height while maintaining the aspect ratio  

    Args:
        image_size (tuple[int, int]): Original image size in pixels (width, height) 
        max_size (tuple[int, int], optional): Maximum image size in pixels (width, height). Defaults to (800, 600).

    Returns:
        tuple[int, int]: Scaled image size in pixels (width, height)
    """
    # DO NOT CHANGE THIS FUNCTION
    resize_ratio = min(max_size[0] / image_size[0], max_size[1] / image_size[1])
    new_size = (int(image_size[0] * resize_ratio), int(image_size[1] * resize_ratio))
    return new_size

if __name__ == '__main__':
    main()
