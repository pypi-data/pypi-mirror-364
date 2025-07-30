import os
import zipfile
import requests
from tqdm import tqdm

def spine_dataset_small(destination_dir="spine_dataset"):
    """
    Downloads and extracts the spine dataset from BUU server into the specified directory.
    """
    dataset_url = "http://angsila.cs.buu.ac.th/~watcharaphong.yk/datasets/BUU-LSPINE_400.zip"
    zip_filename = "BUU-LSPINE_400.zip"
    extracted_dir =  destination_dir

    zip_path = os.path.join(os.path.dirname(__file__), zip_filename)

    def download_with_progress(url, dest_path):
        response = requests.get(url, stream=True)
        total = int(response.headers.get('content-length', 0))
        with open(dest_path, 'wb') as file, tqdm(
            desc=f"Downloading {zip_filename}",
            total=total,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)

    # Download
    if not os.path.exists(zip_path):
        print("Downloading dataset...")
        download_with_progress(dataset_url, zip_path)
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
