#!/usr/bin/env python3

import os
import schedule
import threading
import time
import functools
import docker
from flask import Flask, abort


app = Flask(__name__)


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
    client.containers.run(image='alpine:latest',
                          auto_remove=True,
                          command='-O sonarr.zip http://sonarr:8989/api/system/backup?apikey=' + os.environ['SONARR_TOKEN'],
                          detach=False,
                          entrypoint='wget',
                          name='sonarr-backup',
                          network='media_default',
                          volumes={
                              '/safe01/backups/lmserver': {'bind': '/backups', 'mode': 'rw'}
                              },
                          user=8888,
                          working_dir='/backups'
                          )


@with_logging
def backupRadarr(client):
    client.containers.run(image='alpine:latest',
                          auto_remove=True,
                          command='-O radarr.zip http://radarr:7878/api/system/backup?apikey=' + os.environ['RADARR_TOKEN'],
                          detach=False,
                          entrypoint='wget',
                          name='radarr-backup',
                          network='media_default',
                          volumes={
                              '/safe01/backups/lmserver': {'bind': '/backups', 'mode': 'rw'}
                              },
                          user=8888,
                          working_dir='/backups'
                          )


@with_logging
def backupNZBHydra2(client):
    client.containers.run(image='alpine:latest',
                          auto_remove=True,
                          command='-O nzbhydra2.zip http://nzbhydra2:5076/internalapi/backup/backup',
                          detach=False,
                          entrypoint='wget',
                          name='nzbhydra2-backup',
                          network='media_default',
                          volumes={
                              '/safe01/backups/lmserver': {'bind': '/backups', 'mode': 'rw'}
                              },
                          user=8888,
                          working_dir='/backups'
                          )


@with_logging
def backupEmby(client):
    client.containers.run(image='alpine:latest',
                          auto_remove=True,
                          command='c -zf /backups/emby.tar.gz config plugins data/collections data/playlists data/displaypreferences.db data/users.db data/library.db metadata',
                          detach=False,
                          entrypoint='tar',
                          name='emby-backup',
                          volumes={
                              '/safe01/backups/lmserver': {'bind': '/backups', 'mode': 'rw'},
                              'media_emby': {'bind': '/emby', 'mode': 'ro'}
                              },
                          user=8888,
                          working_dir='/emby'
                          )


@with_logging
def backupFlexget(client):
    client.containers.run(image='alpine:latest',
                          auto_remove=True,
                          command='c -zf /backups/flexget.tar.gz config.yml variables.yml db-config.sqlite db-config-jobs.sqlite',
                          detach=False,
                          entrypoint='tar',
                          name='flexget-backup',
                          volumes={
                              '/safe01/backups/lmserver': {'bind': '/backups', 'mode': 'rw'},
                              'media_flexget': {'bind': '/flexget', 'mode': 'ro'}
                              },
                          user=8888,
                          working_dir='/flexget'
                          )


@with_logging
def backupNZBGet(client):
    client.containers.run(image='alpine:latest',
                          auto_remove=True,
                          command='-c /nzbget/nzbget.conf > /backups/nzbget.conf.gz',
                          detach=False,
                          entrypoint='gzip',
                          name='nzbget-backup',
                          volumes={
                              '/safe01/backups/lmserver': {'bind': '/backups', 'mode': 'rw'},
                              'media_nzbget': {'bind': '/nzbget', 'mode': 'ro'}
                              },
                          user=8888
                          )


@with_logging
def backupLMServer(client):
    client.containers.run(image='restic/restic:latest',
                          auto_remove=True,
                          command='--no-cache -r b2:mdekort-backup-lmserver backup -H lmserver /host/backups',
                          detach=False,
                          environment=[
                            'B2_ACCOUNT_ID=' + os.environ['B2_ACCOUNT_ID'],
                            'B2_ACCOUNT_KEY=' + os.environ['B2_ACCOUNT_KEY'],
                            'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                          ],
                          name='restic',
                          volumes={
                              '/safe01/backups': {'bind': '/host/backups', 'mode': 'ro'}
                              }
                          )


@with_logging
def cleanupLMServer(client):
    client.containers.run(image='restic/restic:latest',
                          auto_remove=True,
                          command='--no-cache -r b2:mdekort-backup-lmserver forget --prune --keep-last 21',
                          detach=False,
                          environment=[
                            'B2_ACCOUNT_ID=' + os.environ['B2_ACCOUNT_ID'],
                            'B2_ACCOUNT_KEY=' + os.environ['B2_ACCOUNT_KEY'],
                            'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                          ],
                          name='restic'
                          )


@with_logging
def backupSyncthing(client):
    client.containers.run(image='restic/restic:latest',
                          auto_remove=True,
                          command='--no-cache -r b2:mdekort-backup-syncthing backup -H lmserver /host/syncthing',
                          detach=False,
                          environment=[
                            'B2_ACCOUNT_ID=' + os.environ['B2_ACCOUNT_ID'],
                            'B2_ACCOUNT_KEY=' + os.environ['B2_ACCOUNT_KEY'],
                            'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                          ],
                          name='restic',
                          volumes={
                              '/home/melvyn/Sync': {'bind': '/host/syncthing', 'mode': 'ro'}
                              }
                          )


@with_logging
def cleanupSyncthing(client):
    client.containers.run(image='restic/restic:latest',
                          auto_remove=True,
                          command='--no-cache -r b2:mdekort-backup-syncthing forget --prune --keep-last 21',
                          detach=False,
                          environment=[
                            'B2_ACCOUNT_ID=' + os.environ['B2_ACCOUNT_ID'],
                            'B2_ACCOUNT_KEY=' + os.environ['B2_ACCOUNT_KEY'],
                            'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                          ],
                          name='restic'
                          )


@with_logging
def backupLibvirt(client):
    client.containers.run(image='restic/restic:latest',
                          auto_remove=True,
                          command='--no-cache -r b2:mdekort-backup-libvirt backup -H lmserver /host/libvirt',
                          detach=False,
                          environment=[
                            'B2_ACCOUNT_ID=' + os.environ['B2_ACCOUNT_ID'],
                            'B2_ACCOUNT_KEY=' + os.environ['B2_ACCOUNT_KEY'],
                            'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                          ],
                          name='restic',
                          volumes={
                              '/safe01/libvirt': {'bind': '/host/libvirt', 'mode': 'ro'}
                              }
                          )


@with_logging
def cleanupLibvirt(client):
    client.containers.run(image='restic/restic:latest',
                          auto_remove=True,
                          command='--no-cache -r b2:mdekort-backup-libvirt forget --prune --keep-last 21',
                          detach=False,
                          environment=[
                            'B2_ACCOUNT_ID=' + os.environ['B2_ACCOUNT_ID'],
                            'B2_ACCOUNT_KEY=' + os.environ['B2_ACCOUNT_KEY'],
                            'RESTIC_PASSWORD=' + os.environ['RESTIC_PASSWORD']
                          ],
                          name='restic'
                          )


@with_logging
def backupPhotos(client):
    client.containers.run(image='amazon/aws-cli:latest',
                          auto_remove=True,
                          command='s3 sync /data/ s3://' + os.environ['AWS_BACKUP_BUCKET'] + '/photos/ --delete --only-show-errors',
                          detach=False,
                          environment=[
                            'AWS_ACCESS_KEY_ID=' + os.environ['LMBACKUP_ACCESS_KEY_ID'],
                            'AWS_SECRET_ACCESS_KEY=' + os.environ['LMBACKUP_SECRET_ACCESS_KEY']
                          ],
                          name='awscli',
                          volumes={
                              '/safe01/photos': {'bind': '/data', 'mode': 'ro'}
                              }
                          )


@with_logging
def job_dyndns():
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    client.containers.run(image='melvyndekort/route53-dyndns:latest',
                          auto_remove=True,
                          detach=False,
                          environment=[
                            'AWS_HOSTED_ZONE_ID=' + os.environ['DYNDNS_HOSTED_ZONE_ID'],
                            'FQDN=' + os.environ['FQDN'],
                            'AWS_ACCESS_KEY_ID=' + os.environ['DYNDNS_ACCESS_KEY_ID'],
                            'AWS_SECRET_ACCESS_KEY=' + os.environ['DYNDNS_SECRET_ACCESS_KEY']
                          ],
                          name='dyndns'
                          )
    client.close()


def waitUntilContainerStops(client, name):
    counter = 0
    while True:
        if (counter >= 30):
            raise Exception(f"Container {name} was running longer than expected")

        try:
            client.containers.get(name)
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
    backupNZBHydra2(client)
    waitUntilContainerStops(client, 'nzbhydra2-backup')
    backupEmby(client)
    waitUntilContainerStops(client, 'emby-backup')
    backupFlexget(client)
    waitUntilContainerStops(client, 'flexget-backup')
    backupNZBGet(client)
    waitUntilContainerStops(client, 'nzbget-backup')

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


@app.route('/', methods=['GET'])
def get_jobs():
    output = '''
<html>
<head>
<title>Scheduler</title>
<script>
function startjob(tag) {
    var req = new XMLHttpRequest();
    req.open('POST', window.location.href + '/' + tag);
    req.send();
}
</script>
</head>
<body>
'''
    for job in schedule.jobs:
        tags = ''
        for tag in job.tags:
            tags += tag
        time = job.next_run.strftime("%Y-%m-%d %H:%M:%S")
        output += f'{tags} | {time} | <button onclick="startjob(\'{tags}\')">start</button><br/>\n'
    return output + '</body></html>'


@app.route('/<tag>', methods=['POST'])
def trigger_job(tag):
    print(f'JOB TRIGGERED: {tag}')
    for job in schedule.jobs:
        for mytag in job.tags:
            if mytag == tag:
                job.run()
                return ''
    abort(404)


def run_flask():
    app.run('0.0.0.0', use_reloader=False)


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


if __name__ == "__main__":
    run_threaded(run_flask)

    schedule.every(1).hours.tag('dyndns').do(run_threaded, job_dyndns)
    schedule.every().day.at("02:00").tag('backups').do(run_threaded, job_backups)

    while 1:
        schedule.run_pending()
        time.sleep(1)
