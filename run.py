#!/usr/bin/python

import os
import schedule
import time
import docker

def database_backups():
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='alpine:latest',
                        auto_remove=True,
                        command='-O sonarr.zip http://sonarr:8989/api/system/backup?apikey=' + os.environ['SONARR_TOKEN'],
                        detach=True,
                        entrypoint='wget',
                        name='sonarr-backup',
                        network='media_default',
                        volumes={'/safe01/backups/lmserver/': {'bind': '/host/backups/lmserver', 'mode': 'rw'}},
                        user=8888,
                        working_dir='/host/backups/lmserver')
  client.containers.run(image='alpine:latest',
                        auto_remove=True,
                        command='-O radarr.zip http://radarr:7878/api/system/backup?apikey=' + os.environ['RADARR_TOKEN'],
                        detach=True,
                        entrypoint='wget',
                        name='radarr-backup',
                        network='media_default',
                        volumes={'/safe01/backups/lmserver/': {'bind': '/host/backups/lmserver', 'mode': 'rw'}},
                        user=8888,
                        working_dir='/host/backups/lmserver')
  return schedule.CancelJob

def data_backup():
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='restic/restic:latest',
                        auto_remove=True,
                        command='-r b2:lmserver-backups backup /host/backups',
                        detach=True,
                        environment=[
                          'B2_ACCOUNT_ID=' + os.environ['B2_ACCOUNT_ID'],
                          'B2_ACCOUNT_KEY=' + os.environ['B2_ACCOUNT_KEY'],
                          'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                        ],
                        name='restic',
                        volumes={'/safe01/backups': {'bind': '/host/backups', 'mode': 'ro'}}
                       )
  return schedule.CancelJob

def photos_backup():
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='rclone/rclone:latest',
                        auto_remove=True,
                        command='sync /data stackstorage:photos --create-empty-src-dirs --progress',
                        detach=True,
                        name='rclone',
                        volumes={'/safe01/photos': {'bind': '/data', 'mode': 'ro'},
                                 'rclone': {'bind': '/config/rclone', 'mode': 'ro'}
                                }
                       )
  return schedule.CancelJob

schedule.every().day.at("02:00").do(database_backups)
schedule.every().day.at("02:15").do(data_backup)
schedule.every().day.at("03:00").do(photos_backup)

while 1:
  schedule.run_pending()
  time.sleep(1)
