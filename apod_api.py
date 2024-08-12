import requests

def main():
    """Test the functions in this module."""
    apod_date = "2024-04-16"
    apod_info = get_apod_info(apod_date)
    if apod_info:
        url = get_apod_image_url(apod_info)
        if url:
            print(f"The URL for APOD image on {apod_date} is: {url}")
        else:
            print("Failed to get the image URL.")
    else:
        print("Failed to access APOD info.")

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (str): APOD date in YYYY-MM-DD format.

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful.
    """
    api_key = "bWdRBzPNHRux9uLcEU4Ly7MStvoYLoCxKHVn8B9p" 
    url = f"https://api.nasa.gov/planetary/apod?date={apod_date}&api_key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        return response.json()  
    except requests.RequestException as e:
        print(f"Error fetching APOD data: {e}")
        return None

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API.

    Returns:
        str: APOD image URL or None if not found.
    """
    if 'media_type' in apod_info_dict:
        media_type = apod_info_dict['media_type']
        if media_type == 'image':
            return apod_info_dict.get('hdurl', apod_info_dict.get('url'))
        elif media_type == 'video':
            return apod_info_dict.get('thumbnail_url')
        else:
            print("Unsupported media type.")
    else:
        print("Media type not found in APOD info.")
    
    return None

if __name__ == '__main__':
    main()
