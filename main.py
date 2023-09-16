import os
import shutil
import subprocess

import requests


def main():
    os.makedirs("plugins", exist_ok=True)
    if not os.path.exists("eula.txt"):
        with open('eula.txt', 'w') as fp:
            fp.write('#By changing the setting below to TRUE you are indicating your agreement to our EULA ('
                     'https://aka.ms/MinecraftEULA).\neula=false')

    version = select_version()
    latest_build = get_message(f"https://api.papermc.io/v2/projects/paper/versions/{version}/", "builds")[-1]
    if not is_up_to_date(version):
        download_build(version, latest_build)
    prepare_server(version)
    subprocess.run(
        ["cd", f"versions/{version}", "&", "java", "-Xms1G", "-Xmx32G", "-XX:+UseG1GC", "-jar",
         f"paper-{version}-{latest_build}.jar", "nogui"], shell=True)


def select_version():
    print("SELECT YOUR PAPER SPIGOT VERSION:")
    versions = get_message("https://api.papermc.io/v2/projects/paper/", "versions")
    print(*versions, "latest (enter)", sep='\n')
    selected = input("\nSELECT YOUR PAPER SPIGOT VERSION: ")
    if selected == "latest" or selected == "":
        selected = versions[-1]
    if not valid_version(selected):
        input("PRESS ENTER TO CONTINUE")
        selected = select_version()
    return selected


def get_message(url, path):
    response = requests.get(url).json()
    return response.get(path)


def download_build(version, build):
    print("Downloading latest Paper Spigot build")
    url = (f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build}/downloads/"
           + f"paper-{version}-{build}.jar")
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    os.makedirs(f"versions/{version}/", exist_ok=True)
    shutil.move(f"paper-{version}-{build}.jar", f"versions/{version}/paper-{version}-{build}.jar")


def valid_version(version):
    builds = requests.get(f"https://api.papermc.io/v2/projects/paper/versions/{version}/").json()
    if 'error' in builds:
        print(builds["error"])
        return False
    return True


def is_up_to_date(version):
    path = f"versions/{version}/"
    if os.path.exists(path):
        files = [i for i in os.listdir(path) if os.path.isfile(os.path.join(path, i)) and
                 'paper-' and '.jar' in i]
        if len(files) == 1:
            return files[0]
        for file in files:
            os.remove(os.path.join(path, file))
    return False


def prepare_server(version):
    path = f"versions/{version}"
    shutil.rmtree(f"{path}/plugins", ignore_errors=True)
    if os.path.exists(f"{path}/eula.txt"):
        os.remove(f"{path}/eula.txt")
    shutil.copytree("plugins", f"{path}/plugins")
    shutil.copyfile("eula.txt", f"{path}/eula.txt")


if __name__ == "__main__":
    main()
