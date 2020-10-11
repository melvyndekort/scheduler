#!/usr/bin/env python3

import os
import schedule
import threading
import time
import functools
import docker
from pprint import pprint


def with_logging(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print('Job "%s" started' % func.__name__)
        result = func(*args, **kwargs)
        print('Job "%s" completed' % func.__name__)
        return result
    return wrapper


@with_logging
def backupSonarr(client):
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


@with_logging
def backupRadarr(client):
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


@with_logging
def backupLMServer(client):
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


@with_logging
def cleanupLMServer(client):
    client.containers.run(image='restic/restic:0.9.6',
                          auto_remove=True,
                          command='--no-cache -r s3:https://s3.wasabisys.com/mdekort-backup/lmserver forget --prune --keep-last 21',
                          detach=False,
                          environment=[
                            'AWS_ACCESS_KEY_ID=' + os.environ['WASABI_ACCESS_KEY_ID'],
                            'AWS_SECRET_ACCESS_KEY=' + os.environ['WASABI_SECRET_ACCESS_KEY'],
                            'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                          ],
                          name='restic')


@with_logging
def backupSyncthing(client):
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


@with_logging
def cleanupSyncthing(client):
    client.containers.run(image='restic/restic:0.9.6',
                          auto_remove=True,
                          command='--no-cache -r s3:https://s3.wasabisys.com/mdekort-backup/syncthing forget --prune --keep-last 21',
                          detach=False,
                          environment=[
                            'AWS_ACCESS_KEY_ID=' + os.environ['WASABI_ACCESS_KEY_ID'],
                            'AWS_SECRET_ACCESS_KEY=' + os.environ['WASABI_SECRET_ACCESS_KEY'],
                            'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                          ],
                          name='restic')


@with_logging
def backupLibvirt(client):
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


@with_logging
def cleanupLibvirt(client):
    client.containers.run(image='restic/restic:0.9.6',
                          auto_remove=True,
                          command='--no-cache -r s3:https://s3.wasabisys.com/mdekort-backup/libvirt forget --prune --keep-last 21',
                          detach=False,
                          environment=[
                            'AWS_ACCESS_KEY_ID=' + os.environ['WASABI_ACCESS_KEY_ID'],
                            'AWS_SECRET_ACCESS_KEY=' + os.environ['WASABI_SECRET_ACCESS_KEY'],
                            'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                          ],
                          name='restic')


@with_logging
def backupPhotos(client):
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


@with_logging
def job_resetPermissions():
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    client.containers.run(image='melvyndekort/resetperms:1.2',
                          auto_remove=True,
                          detach=False,
                          environment=[
                            'SETUID=8888',
                            'SETGID=8888',
                            'DIRS=' + os.environ['PERMDIRS']
                          ],
                          name='resetperms',
                          volumes={'/safe01': {'bind': '/host/safe01', 'mode': 'rw'},
                                   '/data01': {'bind': '/host/data01', 'mode': 'rw'}})
    client.close()


@with_logging
def job_dyndns():
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
    client.close()


def waitUntilContainerStops(client, name):
    counter = 0
    while True:
        if (counter >= 30):
            raise Exception(f"Container {name} was running longer than expected")

        try:
            client.get(name)
            counter += 1
            time.sleep(1)
        except docker.errors.NotFound:
            break


@with_logging
def job_backups():
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    backupSonarr(client)
    waitUntilContainerStops(client, 'sonarr-backup')
    backupRadarr(client)
    waitUntilContainerStops(client, 'radarr-backup')

    backupLMServer(client)
    waitUntilContainerStops(client, 'restic')
    cleanupLMServer(client)
    waitUntilContainerStops(client, 'restic')

    backupSyncthing(client)
    waitUntilContainerStops(client, 'restic')
    cleanupSyncthing(client)
    waitUntilContainerStops(client, 'restic')

    backupLibvirt(client)
    waitUntilContainerStops(client, 'restic')
    cleanupLibvirt(client)
    waitUntilContainerStops(client, 'restic')

    backupPhotos(client)

    client.close()


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def main():
    #schedule.every(1).hours.do(run_threaded, job_resetPermissions)
    schedule.every(2).hours.do(run_threaded, job_dyndns)
    schedule.every().day.at("02:00").do(run_threaded, job_backups)

    print('Loaded jobs:')
    pprint(schedule.jobs)
    
    while 1:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__": 
    main()
