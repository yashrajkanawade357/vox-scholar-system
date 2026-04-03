import os, time, requests, tarfile
url = 'https://chroma-onnx-models.s3.amazonaws.com/all-MiniLM-L6-v2/onnx.tar.gz'
dest_dir = os.path.expanduser('~/.cache/chroma/onnx_models/all-MiniLM-L6-v2')
dest_file = os.path.join(dest_dir, 'onnx.tar.gz')
os.makedirs(dest_dir, exist_ok=True)

downloaded = 0
if os.path.exists(dest_file):
    downloaded = os.path.getsize(dest_file)

max_retries = 50
while max_retries > 0:
    try:
        headers = {'Range': f'bytes={downloaded}-'}
        print(f"Resuming embedding model download from {downloaded} bytes...")
        with requests.get(url, headers=headers, stream=True, timeout=15) as r:
            if r.status_code in [200, 206]:
                with open(dest_file, 'ab') as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if downloaded % (5*1024*1024) < 65536:
                                print(f"  {downloaded/1024/1024:.1f} MB downloaded...")
                break # Success
            elif r.status_code == 416: # Range not satisfiable (already fully downloaded?)
                break
    except Exception as e:
        print(f"Network interrupt: {e}. Retrying in 3 seconds...")
        time.sleep(3)
        max_retries -= 1

print("Download complete. Extracting embedding model...")
try:
    with tarfile.open(dest_file) as tar:
        tar.extractall(path=dest_dir)
except EOFError:
    print("Corrupted archive. Please delete and restart.")
print("Embedding model ready!")
