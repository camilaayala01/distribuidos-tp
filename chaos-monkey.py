import random
import subprocess
import time
import re
import os
from dotenv import load_dotenv

load_dotenv('chaos.env')
TO_CHECK = os.getenv("TO_CHECK")
CONTAINER = os.getenv("CONTAINER_NAME")

def container(node):
    return f'{CONTAINER}-{node}'

def kill(node):
        print(f"Killing node {node}")
        result = subprocess.run(['docker', 'kill', container(node)], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('Command executed. Result={}. Output={}. Error={}'.format(result.returncode, result.stdout, result.stderr))

def main():
    nodesToKill = set(re.split(r';', os.getenv('TO_CHECK')) if os.getenv('TO_CHECK') else [])
    while True:
        kill(random.sample(nodesToKill, 1))
        time.sleep(10)