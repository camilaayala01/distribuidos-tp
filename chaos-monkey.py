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
    return f'{CONTAINER}-{node}-1'

def kill(node):
        print(f"Killing node {node}")
        result = subprocess.run(['docker', 'kill', container(node)], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('Command executed. Result={}. Output={}. Error={}'.format(result.returncode, result.stdout, result.stderr))

def main():
    nodesToKill = set(re.split(r';', os.getenv('TO_CHECK')) if os.getenv('TO_CHECK') else [])
    print(nodesToKill)
    while True:
        node_to_kill = random.choice(list(nodesToKill))
        kill(node_to_kill)
        time.sleep(10)

if __name__ == '__main__':
    main()