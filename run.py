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
                        detach=False,
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
                        detach=False,
                        environment=[
                          'ZONEID=' + os.environ['ZONEID'],
                          'FQDN=' + os.environ['FQDN'],
                          'AWS_ACCESS_KEY_ID=' + os.environ['AWS_ACCESS_KEY_ID'],
                          'AWS_SECRET_ACCESS_KEY=' + os.environ['AWS_SECRET_ACCESS_KEY']
                        ],
                        name='dyndns')
  print('Finished dyndns update')
  client.close()

def backupDataOne():
  print('Starting sonarr backup')
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='alpine:3.12',
                        auto_remove=True,
                        command='-O sonarr.zip http://sonarr:8989/api/system/backup?apikey=' + os.environ['SONARR_TOKEN'],
                        detach=False,
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
                        detach=False,
                        entrypoint='wget',
                        name='radarr-backup',
                        network='media_default',
                        volumes={'/safe01/backups/lmserver': {'bind': '/host/lmserver', 'mode': 'rw'}},
                        user=8888,
                        working_dir='/host/lmserver')
  print('Finished radarr backup')
  print('Starting restic backup to Wasabi: lmserver')
  client.containers.run(image='restic/restic:0.9.6',
                        auto_remove=True,
                        command='--no-cache -r s3:https://s3.wasabisys.com/mdekort-backup/lmserver backup -H lmserver /host/backups',
                        detach=False,
                        environment=[
                          'AWS_ACCESS_KEY_ID=' + os.environ['WASABI_ACCESS_KEY_ID'],
                          'AWS_SECRET_ACCESS_KEY=' + os.environ['WASABI_SECRET_ACCESS_KEY'],
                          'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                        ],
                        name='restic',
                        volumes={'/safe01/backups': {'bind': '/host/backups', 'mode': 'ro'}})
  print('Finished restic backup to Wasabi: lmserver')
  client.close()

def backupDataTwo():
  print('Starting restic backup to Wasabi: syncthing')
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='restic/restic:0.9.6',
                        auto_remove=True,
                        command='--no-cache -r s3:https://s3.wasabisys.com/mdekort-backup/syncthing backup -H lmserver /host/syncthing',
                        detach=False,
                        environment=[
                          'AWS_ACCESS_KEY_ID=' + os.environ['WASABI_ACCESS_KEY_ID'],
                          'AWS_SECRET_ACCESS_KEY=' + os.environ['WASABI_SECRET_ACCESS_KEY'],
                          'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                        ],
                        name='restic',
                        volumes={'/home/melvyn/Sync': {'bind': '/host/syncthing', 'mode': 'ro'}})
  print('Finished restic backup to Wasabi: syncthing')
  client.close()

def backupDataThree():
  print('Starting restic backup to Wasabi: libvirt')
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='restic/restic:0.9.6',
                        auto_remove=True,
                        command='--no-cache -r s3:https://s3.wasabisys.com/mdekort-backup/libvirt backup -H lmserver /host/libvirt',
                        detach=False,
                        environment=[
                          'AWS_ACCESS_KEY_ID=' + os.environ['WASABI_ACCESS_KEY_ID'],
                          'AWS_SECRET_ACCESS_KEY=' + os.environ['WASABI_SECRET_ACCESS_KEY'],
                          'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                        ],
                        name='restic',
                        volumes={'/safe01/libvirt': {'bind': '/host/libvirt', 'mode': 'ro'}})
  print('Finished restic backup to Wasabi: libvirt')
  client.close()

def backupPhotos():
  print('Starting rclone backup to StackStorage')
  client = docker.DockerClient(base_url='unix://var/run/docker.sock')
  client.containers.run(image='rclone/rclone:1.53',
                        auto_remove=True,
                        command='/bin/sh -c "rclone config create stackstorage webdav; rclone sync /data stackstorage:photos --create-empty-src-dirs"',
                        detach=False,
                        entrypoint='',
                        environment=[
                          'RCLONE_WEBDAV_VENDOR=owncloud',
                          'RCLONE_WEBDAV_URL=https://lordmatanza.stackstorage.com/remote.php/webdav/',
                          'RCLONE_WEBDAV_USER=' + os.environ['RCLONE_WEBDAV_USER'],
                          'RCLONE_WEBDAV_PASS=' + os.environ['RCLONE_WEBDAV_PASS']
                        ],
                        name='rclone',
                        volumes={'/safe01/photos': {'bind': '/data', 'mode': 'ro'}})
  print('Finished rclone backup to StackStorage')
  client.close()

schedule.every(1).hours.do(resetPermissions)
schedule.every(2).hours.do(dyndns)
schedule.every().day.at("02:00").do(backupDataOne)
schedule.every().day.at("02:15").do(backupDataTwo)
schedule.every().day.at("02:30").do(backupDataThree)
schedule.every().day.at("02:45").do(backupPhotos)

while 1:
  schedule.run_pending()
  time.sleep(1)
