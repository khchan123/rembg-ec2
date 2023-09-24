#!/bin/bash

yum update -y
yum install -y pip virtualenv

mkdir -p /home/ec2-user/app
cd /home/ec2-user/app
virtualenv -p python3 venv
source venv/bin/activate

# TODO: download files from another source
wget https://github.com/khchan123/rembg-ec2/raw/main/app/app.py
wget https://github.com/khchan123/rembg-ec2/raw/main/app/requirements.txt
wget https://github.com/khchan123/rembg-ec2/raw/main/app/gunicorn.conf.py
wget https://github.com/khchan123/rembg-ec2/raw/main/app/gunicorn.service -O /etc/systemd/system/gunicorn.service

pip install rembg[cli]
pip install markupsafe==2.0.1
pip install -r requirements.txt
chown -R ec2-user:ec2-user /home/ec2-user

systemctl start gunicorn
systemctl enable gunicorn
