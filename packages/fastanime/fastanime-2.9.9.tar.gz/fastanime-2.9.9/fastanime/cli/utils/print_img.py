import shutil
import subprocess

import requests


def print_img(url: str):
    """helper function to print an image given its url

    Args:
        url: [TODO:description]
    """
    if EXECUTABLE := shutil.which("icat"):
        subprocess.run([EXECUTABLE, url])
    else:
        EXECUTABLE = shutil.which("chafa")

        if EXECUTABLE is None:
            print("chafanot found")
            return

        res = requests.get(url)
        if res.status_code != 200:
            print("Error fetching image")
            return
        img_bytes = res.content
        """
        Change made in call to chafa. Chafa dev dropped ability
        to pull from urls. Keeping old line here just in case.

        subprocess.run([EXECUTABLE, url, "--size=15x15"], input=img_bytes)
        """
        subprocess.run([EXECUTABLE, "--size=15x15"], input=img_bytes)
