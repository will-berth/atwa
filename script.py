import argparse
import os
import requests
from itertools import product
from bs4 import BeautifulSoup
import re
import time

def find_files_in_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        file_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if re.search(r'\.\w+$', href):
                file_links.append(href)
                
        return file_links
    except requests.RequestException as e:
        print(f"Error al acceder a la URL: {e}")
        return []

def download_file(url, output_dir, filename):
    try:
        print(url, filename)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f'Successfully downloaded: {filename}')
        time.sleep(2)
    except requests.exceptions.RequestException as e:
        print(f'Failed to download {filename}: {e}')

def generate_urls(url_root, pattern, max_vals):
    nums1, nums2 = map(int, max_vals.split(','))
    for i, j in product(range(1, nums1 + 1), range(1, nums2 + 1)):
        yield f'{url_root}/{pattern.format(i, j)}.pdf', pattern.format(i, j) + '.pdf'

def main():
    parser = argparse.ArgumentParser(description='Download files from a URL or generate URLs based on a pattern.')
    parser.add_argument('--url', type=str, help='Specific URL of the file to download.')
    parser.add_argument('--url-files', type=str, help='Specific URL with the files to download.')
    parser.add_argument('--url-root', type=str, help='Root URL for generating file URLs.')
    parser.add_argument('--pattern', type=str, help='Pattern for generating file names, e.g., {0}_{1}.')
    parser.add_argument('--max-vals', type=str, help='Comma-separated max values for generating file names, e.g., 1263,7.')
    parser.add_argument('--output-dir', type=str, default='downloads', help='Directory to save downloaded files.')
    parser.add_argument('--file-type', type=str, default='downloads', help='Specific file type, e.g: mp3, pdf, doc')
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    if args.url:
        filename = os.path.basename(args.url)
        print(args.url, filename)
        download_file(args.url, args.output_dir, filename)
    elif args.url_root and args.pattern and args.max_vals:
        for url, filename in generate_urls(args.url_root, args.pattern, args.max_vals):
            print(url, filename)
            download_file(url, args.output_dir, filename)
    elif args.url_files:
        file_links = find_files_in_url(args.url_files)
        for filename in file_links:
            download_file(f"{args.url_files}{filename}", args.output_dir, filename)
    else:
        print('Please provide either --url or --url-root, --pattern, and --max-vals.')

if __name__ == '__main__':
    main()
