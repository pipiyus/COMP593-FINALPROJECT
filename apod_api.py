'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
import requests
import json
def main():
    # TODO: Add code to test the functions in this module
   apod_date="2024-04-16"
   apod_info=get_apod_info(apod_date)
   if apod_info:
       url=get_apod_image_url(apod_info)
       print(f"the url for apod image is{apod_date}: {url}")
   else:
       print("failed to access info from apod info")
   return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    url="https://api.nasa.gov/planetary/apod"
    

    params={
        'api_key':'DEMO_KEY',
        'date':apod_date,
        'thumbs':True
    
    }
    response=requests.get(url,params=params)
    if response.status_code==200:
     return {'url': response.json().get('url'), 'media_type': response.json().get('media_type')}   
    else:
     print(f'failed to receive apod info and date:{apod_date}')

    # TODO: Complete the function body
    # Hint: The APOD API uses query string parameters: https://requests.readthedocs.io/en/latest/user/quickstart/#passing-parameters-in-urls
    # Hint: Set the 'thumbs' parameter to True so the info returned for video APODs will include URL of the video thumbnail image 
    return None

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """
    if 'media_type' in apod_info_dict:
            if apod_info_dict['media_type']=='image':
                if' hdrul' in apod_info_dict:
                    return apod_info_dict['hdurl']
                elif 'url' in apod_info_dict:
                    return apod_info_dict['url']
                else:
                    print('url not found in apod file')
            elif apod_info_dict['media_type']=='video':
                if 'thumbnail_url' in apod_info_dict:
                    return apod_info_dict['thumbnail_url']
                else:
                    print('Thumbnail  url is missing in apod file' )
    else:
            print('media_type not found in apod file')
            
    # TODO: Complete the function body
    # Hint: The APOD info dictionary includes a key named 'media_type' that indicates whether the APOD is an image or video
    return None

if __name__ == '__main__':
    main()