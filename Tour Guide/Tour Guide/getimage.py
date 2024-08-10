import os
import requests

def download_images(query, download_path, max_images=10):
    api_key = 'ZuRric8BOJ8AAptcBDkHoRh67qJ6XA6bGcTSteBh76vTBv1d3Xo1r42O'
    url = f'https://api.pexels.com/v1/search?query={query}&per_page={max_images}'

    headers = {'Authorization': api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        for index, photo in enumerate(data['photos']):
            if index >= max_images:
                break
            image_url = photo['src']['medium']
            image_filename = os.path.join(download_path, f'images_{index}.jpg')
            download_image(image_url, image_filename)
    except requests.exceptions.RequestException as e:
        print('Error fetching images:', e)
        raise

def download_image(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f'Downloaded {filename}')
    except requests.exceptions.RequestException as e:
        print(f'Error downloading {url}:', e)

# Example usage
query = 'nature'  # Example search query
download_path = 'static/predimages'  # Specify your download location
max_images = 6  # Maximum number of images to download
download_images(query, download_path, max_images)
