import argparse
import requests
from tqdm import tqdm
def main():
    parse = argparse.ArgumentParser(description='Download some files')
    parse.add_argument('--url', type=str, required=True, help='The URL you want to download')
    parse.add_argument('-out', type=str, required=True, help='The output file path')
    args = parse.parse_args()

    url = args.url
    fileName = args.out

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        chunk_size = 8192

        with open(fileName, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True, desc=fileName, ncols=80, bar_format="{desc}: {percentage:3.0f}% {n_fmt}/{total_fmt}B") as pbar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
def download_file(url, fileName):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(fileName, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

if __name__ == '__main__':
    main()
    print('download success')