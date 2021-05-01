# Interactive Cloud Deployment

The project's purpose is for the interactive deployment of a Digital Ocean droplet and setup of a Docker Compose file which spawns an Nginx webserver with SSL enabled.

## How it works
The script uses calls with the Digital Ocean API directly for the Droplet creating and setup using Ansible

## Requirements
Python +v3.x

## Installation
#### Setup Virtual Environment
```bash
sudo apt-get install virtualenv

virtualenv -p python3 venv
. venv/bin/activate
```

#### Install Requirements
```bash
pip install -r requirements.txt
```

## Configuration
- Edit **'env.json'** with the desired values.
- Create a Digital Ocean API token. ([How-to](https://docs.digitalocean.com/reference/api/create-personal-access-token/))
- Customize **'docker-compose.yml'** file to your needs. ([Documentation](https://hub.docker.com/r/linuxserver/swag))

## Usage
#### Interactive
```bash
python3 run_deployment.py
```
#### Automatic
Configure **'config'** JSON document inside **'run_deployment.py'** file.
```bash
python3 run_deployment.py
```

## References
- Digital Ocean: [https://developers.digitalocean.com/documentation/v2/](https://developers.digitalocean.com/documentation/v2/)
- Ansible: [https://docs.ansible.com/ansible/latest/user_guide/](https://docs.ansible.com/ansible/latest/user_guide/)
