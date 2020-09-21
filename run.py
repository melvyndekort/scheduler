#!/usr/bin/python

import os
import schedule
import time
import docker

def resetPermissions():
  print('Starting resetting filesystem permissions')
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='melvyndekort/resetperms:1.2',
                        auto_remove=True,
                        detach=True,
                        environment=[
                          'SETUID=8888',
                          'SETGID=8888',
                          'DIRS=/host/data01/kids;/host/data01/movies;/host/data01/music;/host/data01/software;/host/data01/torrents;/host/data01/tv;/host/data01/usenet;/host/data01/xxx;/host/safe01/photos'
                        ],
                        name='resetperms',
                        volumes={'/safe01': {'bind': '/host/safe01', 'mode': 'rw'},
                                 '/data01': {'bind': '/host/data01', 'mode': 'rw'}})
  print('Finished resetting filesystem permissions')
  client.close()

def dyndns():
  print('Starting dyndns update')
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='melvyndekort/route53-dyndns:1.1',
                        auto_remove=True,
                        detach=True,
                        environment=[
                          'ZONEID=' + os.environ['ZONEID'],
                          'FQDN=' + os.environ['FQDN'],
                          'AWS_ACCESS_KEY_ID=' + os.environ['AWS_ACCESS_KEY_ID'],
                          'AWS_SECRET_ACCESS_KEY=' + os.environ['AWS_SECRET_ACCESS_KEY']
                        ],
                        name='dyndns')
  print('Finished dyndns update')
  client.close()

def backupDatabases():
  print('Starting sonarr backup')
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='alpine:3.12',
                        auto_remove=True,
                        command='-O sonarr.zip http://sonarr:8989/api/system/backup?apikey=' + os.environ['SONARR_TOKEN'],
                        detach=True,
                        entrypoint='wget',
                        name='sonarr-backup',
                        network='media_default',
                        volumes={'/safe01/backups/lmserver': {'bind': '/host/lmserver', 'mode': 'rw'}},
                        user=8888,
                        working_dir='/host/lmserver')
  print('Finished sonarr backup')
  print('Starting radarr backup')
  client.containers.run(image='alpine:3.12',
                        auto_remove=True,
                        command='-O radarr.zip http://radarr:7878/api/system/backup?apikey=' + os.environ['RADARR_TOKEN'],
                        detach=True,
                        entrypoint='wget',
                        name='radarr-backup',
                        network='media_default',
                        volumes={'/safe01/backups/lmserver': {'bind': '/host/lmserver', 'mode': 'rw'}},
                        user=8888,
                        working_dir='/host/lmserver')
  print('Finished radarr backup')
  client.close()

def backupData():
  print('Starting restic backup to B2')
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='restic/restic:0.9.6',
                        auto_remove=True,
                        command='--no-cache -r b2:lmserver-backups backup -H lmserver /host/backups',
                        detach=True,
                        environment=[
                          'B2_ACCOUNT_ID=' + os.environ['B2_ACCOUNT_ID'],
                          'B2_ACCOUNT_KEY=' + os.environ['B2_ACCOUNT_KEY'],
                          'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                        ],
                        name='restic',
                        volumes={'/safe01/backups': {'bind': '/host/backups', 'mode': 'ro'},
                                 '/home/melvyn/Sync': {'bind': '/host/backups/Sync', 'mode': 'ro'}})
  print('Finished restic backup to B2')
  client.close()

def backupPhotos():
  print('Starting rclone backup to StackStorage')
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='rclone/rclone:1.53',
                        auto_remove=True,
                        command='sync /data stackstorage:photos --create-empty-src-dirs',
                        detach=True,
                        name='rclone',
                        volumes={'/safe01/photos': {'bind': '/data', 'mode': 'ro'},
                                 'rclone': {'bind': '/config/rclone', 'mode': 'ro'}})
  print('Finished rclone backup to StackStorage')
  client.close()

schedule.every(1).hours.do(resetPermissions)
schedule.every(1).hours.do(dyndns)
schedule.every().day.at("02:00").do(backupDatabases)
schedule.every().day.at("02:15").do(backupData)
schedule.every().day.at("03:00").do(backupPhotos)

while 1:
  schedule.run_pending()
  time.sleep(1)
