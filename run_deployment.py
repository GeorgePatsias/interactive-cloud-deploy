import json
import requests
from os import getcwd
from time import sleep
from getpass import getuser
from sys import stdout, exit
from termcolor import colored
from subprocess import Popen, PIPE
from digitalocean import Manager as DOManager

global config
config = {
    "do_token": None,
    "name": None,
    "region": "fra1",
    "size": None,
    "image": "ubuntu-20-04-x64",
    "ssh_keys": None,
    "backups": False,
    "ipv6": False,
    "user_data": None,
    "private_networking": None,
    "volumes": None,
    "tags": []
}


def progress_bar(seconds):
    stdout.write("[{}]".format(" " * seconds))
    stdout.flush()
    stdout.write("\b" * (seconds+1))

    for i in range(seconds):
        sleep(1)
        stdout.write("-")
        stdout.flush()

    stdout.write("]\n")


def validate_do_token():
    do_token = config.get('do_token', None)
    while not do_token:
        do_token = input('Enter DigitalOcean API token: ')

        try:
            response = requests.get('https://api.digitalocean.com/v2/account', headers={"Content-Type": "application/json", "Authorization": f"Bearer {do_token}"}).json()

            if response.get('id', None) == 'Unauthorized':
                print(f'[{colored("ERROR","red")}]: Unauthorized token\n')
                do_token = None

        except Exception:
            print(f'[{colored("ERROR","red")}]: Please check your internet connection\n')
            do_token = None

    config['do_token'] = do_token
    print(f'[{colored("SUCCESS","green")}]: Authorized token\n')


def get_ssh_keys():
    menu_option = None
    while not menu_option and not config.get('ssh_keys', None):
        try:
            menu_option = input(f"""[{colored("MENU","yellow")}] Select SSH key options:
1) Select SSH keys to add from DigitalOcean account
2) Add all from DigitalOcean account\n""")

            if menu_option not in ['1', '2']:
                print(f'[{colored("ERROR","red")}]: Please enter a valid option\n')
                menu_option = None

        except Exception:
            print(f'[{colored("ERROR","red")}]: Please enter a valid option\n')
            menu_option = None

    if menu_option == '1':
        try:
            manager = DOManager(token=config.get("do_token"))
            keys = manager.get_all_sshkeys()

            if not keys:
                print(f'[{colored("INFO","cyan")}]: Not available SSH key in DigitalOcean. Exiting... \n')
                exit()

            menu = f'[{colored("MENU","yellow")}] Select SSH keys to add (comma seperated):\n'
            count = 1
            key_map = {}
            for key in keys:
                menu = f"{menu}{count}) {key.name}\n"
                key_map[str(count)] = key.id
                count += 1

            menu_opt = None
            while not menu_opt:
                menu_opt = input(menu)

                menu_opt = menu_opt.split(',')
                for opt in menu_opt:
                    opt = opt.strip()
                    if opt not in key_map.keys():
                        menu_opt = None

                if not menu_opt:
                    print(f'[{colored("ERROR","red")}]: Enter valid options from menu\n')

            ssk_key_list = []
            for opt in menu_opt:
                opt = opt.strip()
                ssk_key_list.append(key_map[opt])

            config['ssh_keys'] = ssk_key_list

            print(f'[{colored("SUCCESS","green")}]: SSH keys set \n')

            return True

        except Exception:
            print(f'[{colored("ERROR","red")}]: Cannot find SSH keys. Exiting...\n')
            exit()

    if menu_option == '2':
        try:
            manager = digitalocean.Manager(token=config.get("do_token"))
            keys = manager.get_all_sshkeys()

            if not keys:
                print(f'[{colored("ERROR","red")}]: No keys found in DigitalOcean account\n')
                return

            key_list = []
            for key in keys:
                key_list.append(key.id)

            config['ssh_keys'] = key_list

            print(f'[{colored("SUCCESS","green")}]: SSH keys set\n')

            return True

        except Exception:
            print(f'[{colored("ERROR","red")}]: Cannot find SSH keys. Exiting...\n')
            exit()

    config['ssh_keys'] = ssh_key

    return True


def parse_do_name(name):
    name = name.strip()
    for char in name:
        if char not in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-.':
            print(f'[{colored("ERROR","red")}]: Valid names contain alphanumberic, periods or dashes, not ending/starting with symbols\n')
            return

    if name[0] in ['-', '.'] or name[len(name)-1] in ['-', '.']:
        print(f'[{colored("ERROR","red")}]: Valid names contain alphanumberic, periods or dashes, not ending/starting with symbols\n')
        return

    return True


def droplet_config_name():
    while not config.get('name', None):
        name = input(f'[{colored("INPUT","yellow")}]: Enter Droplet name: ')

        if not parse_do_name(name):
            return

        config['name'] = name
        print(f'[{colored("SUCCESS","green")}]: Droplet name set \n')
        return True


def droplet_config_size():
    size_list = requests.get('https://api.digitalocean.com/v2/sizes', headers={"Content-Type": "application/json", "Authorization": f"Bearer {config['do_token']}"}).json()

    sizes_map = {}
    menu = f'[{colored("MENU","yellow")}] Select Droplet size:\n'
    count = 1
    for size in size_list.get('sizes'):
        slug = size.get('slug')
        if slug.startswith('s-'):
            sizes_map[str(count)] = slug
            menu = f"{menu}{count}) {slug}\n"
            count += 1

    menu_option = None
    while not menu_option:
        menu_option = input(menu)

        if menu_option not in sizes_map.keys():
            print(f'[{colored("ERROR","red")}]: Enter a valid Droplet size\n')
            menu_option = None

    config['size'] = sizes_map[menu_option]
    print(f'[{colored("SUCCESS","green")}]: Droplet size set\n')


def create_droplet():
    while not config.get('ssh_keys', None):
        get_ssh_keys()

    while not config.get('name', None):
        droplet_config_name()

    while not config.get('size', None):
        droplet_config_size()

    do_token = config.pop('do_token')
    response = requests.post(
        "https://api.digitalocean.com/v2/droplets",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {do_token}"},
        data=json.dumps(config)
    ).json()

    droplet_id = response.get('droplet', None).get('id', None)
    if not droplet_id:
        print(f'[{colored("ERROR","red")}]: Droplet not created! Something went wrong\n')
        exit()

    print(f'[{colored("INFO","cyan")}]: Creating Droplet, please wait...\n')

    progress_bar(15)

    response = requests.get(f"https://api.digitalocean.com/v2/droplets/{droplet_id}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {do_token}"}).json()

    if not response:
        print(f'[{colored("ERROR","red")}]: Droplet not created! Something went wrong\n')

    network_info = response.get('droplet', None).get('networks', None)
    print(f'[{colored("SUCCESS","green")}]: Droplet created \nNetwork Information: {network_info}')

    return network_info


def setup_environment(network_info):
    print(f'[{colored("INFO","cyan")}]: Setting up environment, please wait...')
    progress_bar(60)

    ips = network_info.get('v4', None)
    ip = None
    for item in ips:
        if item.get('type', None) != "private":
            ip = item.get('ip_address', None)
            break

    with open('env.json') as json_file:
        json_decoded = json.load(json_file)

    json_decoded['host'] = ip

    with open('env.json', 'w') as json_file:
        json.dump(json_decoded, json_file, indent=4)

    try:
        process = Popen(["ansible-playbook", "-i", f"{ip},", "setup_env.yml", "-e", "@env.json"], stdout=PIPE, encoding='utf-8')

        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(line)

        print(f'[{colored("SUCCESS","green")}]: Droplet environment set\n')

    except Exception:
        print(f'[{colored("ERROR","red")}]: Cannot set environment! Something went wrong\n')


if __name__ == '__main__':
    validate_do_token()

    network_info = create_droplet()

    setup_environment(network_info)

    print(f"[{colored('SUCCESS','green')}]: Job's done! Byeee!\n")
