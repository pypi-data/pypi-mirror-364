import os
import zipfile
import requests
from tqdm import tqdm

def spine_dataset_small(destination_dir="spine_dataset"):
    """
    Downloads and extracts the spine dataset from Google Drive into the specified directory.
    """
    file_id = "1OqM9J8S2Cy23D-4nIRJdZdzD9-mmo2Og"
    zip_filename = "spine_dataset.zip"
    extracted_dir = os.path.join(os.path.dirname(__file__), destination_dir)

    def download_file_from_google_drive(file_id, dest_path):
        def get_confirm_token(response):
            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    return value
            return None

        def save_response_content(response, destination):
            CHUNK_SIZE = 32768
            with open(destination, "wb") as f:
                for chunk in tqdm(response.iter_content(CHUNK_SIZE), desc="Downloading", unit="chunk"):
                    if chunk:
                        f.write(chunk)

        URL = "https://docs.google.com/uc?export=download"
        session = requests.Session()
        response = session.get(URL, params={'id': file_id}, stream=True)
        token = get_confirm_token(response)

        if token:
            params = {'id': file_id, 'confirm': token}
            response = session.get(URL, params=params, stream=True)

        save_response_content(response, dest_path)

    # Download
    zip_path = os.path.join(os.path.dirname(__file__), zip_filename)
    if not os.path.exists(zip_path):
        print("Downloading dataset...")
        download_file_from_google_drive(file_id, zip_path)
    else:
        print("Dataset zip already exists.")

    # Extract
    if not os.path.exists(extracted_dir):
        print("Extracting dataset...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)
        print(f"Dataset extracted to {extracted_dir}")
    else:
        print("Dataset already extracted.")

    return extracted_dir
