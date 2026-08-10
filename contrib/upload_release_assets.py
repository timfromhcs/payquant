import urllib.request
import os

token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN', '')
release_id = '367283041'
assets = [
    ('payquant-v4.0.0-windows.zip', 'release_dist/payquant-v4.0.0-windows.zip', 'application/zip'),
    ('payquant-v4.0.0-macos.zip', 'release_dist/payquant-v4.0.0-macos.zip', 'application/zip'),
    ('payquant-v4.0.0-linux.zip', 'release_dist/payquant-v4.0.0-linux.zip', 'application/zip'),
    ('payquant-v4.0.0-android.zip', 'release_dist/payquant-v4.0.0-android.zip', 'application/zip')
]

if token:
    for name, path, content_type in assets:
        if os.path.exists(path):
            print(f"Uploading asset {name} ({os.path.getsize(path)} bytes)...")
            url = f"https://uploads.github.com/repos/timfromhcs/payquant/releases/{release_id}/assets?name={name}"
            with open(path, 'rb') as f:
                data = f.read()
            req = urllib.request.Request(url, data=data, headers={
                'Authorization': f'token {token}',
                'Content-Type': content_type,
                'User-Agent': 'PayQuant-Agent'
            })
            try:
                resp = urllib.request.urlopen(req)
                print(f"Successfully uploaded {name}!")
            except Exception as e:
                print(f"Failed to upload {name}: {e}")
