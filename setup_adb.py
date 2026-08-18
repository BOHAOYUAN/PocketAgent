import os
import urllib.request
import zipfile
import shutil

def download_and_extract_adb():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bin_dir = os.path.join(base_dir, "bin")
    platform_tools_dir = os.path.join(bin_dir, "platform-tools")
    adb_exe = os.path.join(platform_tools_dir, "adb.exe")

    if os.path.exists(adb_exe):
        print(f"[ADB] ADB already exists at: {adb_exe}")
        return adb_exe

    os.makedirs(bin_dir, exist_ok=True)
    zip_path = os.path.join(bin_dir, "platform-tools.zip")
    url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"

    print(f"[ADB] Downloading Google Platform-Tools (ADB) from {url}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    print("[ADB] Extracting platform-tools.zip...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(bin_dir)

    if os.path.exists(zip_path):
        os.remove(zip_path)

    print(f"[ADB] ADB installed successfully: {adb_exe}")
    return adb_exe

if __name__ == "__main__":
    download_and_extract_adb()
