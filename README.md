# CTE
CTFD but the D is an E and its crappier, and build for PTC-CTF based on Flask and 

## Requirements
A 'server' to install it on 

A domain to host it on, defined in ansibledeployment/files/ctfe, replace ctf.hhscyber.com and www.ctf.hhscyber.com; if you want to host it locally just use your computer's private IP in this place

port 80 needs to be forwarded 

PLANED: Automatic Certbot deployment to run it over 443

SSH enabled

## Installation
Only tested on stock ubuntu18.04+ as it stands, light changes to the playbook would make it able to be installed on debian

` ssh-copy-id -p SSHPORT root@SERVERIP `

` ansible-playbook -u 'root' -i "SERVERIPADDRES," install_server.yaml `
