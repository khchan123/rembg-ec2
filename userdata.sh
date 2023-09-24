#!/bin/bash

yum update -y
yum install -y pip virtualenv

mkdir -p /home/ssm-user/app
cd /home/ssm-user/app
virtualenv -p python3 venv
source venv/bin/activate

# TODO: download files from another source
wget https://github.com/khchan123/rembg-ec2/raw/main/app/app.py
wget https://github.com/khchan123/rembg-ec2/raw/main/app/requirements.txt
wget https://github.com/khchan123/rembg-ec2/raw/main/app/gunicorn.conf.py
wget https://github.com/khchan123/rembg-ec2/raw/main/app/gunicorn.service -o /etc/systemd/system/gunicorn.service

pip install rembg[cli]
pip install markupsafe==2.0.1
pip install -r requirements.txt
chown -R ssm-user:ssm-user /home/ssm-user/app
systemctl start gunicorn
systemctl enable gunicorn
