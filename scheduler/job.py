from dataclasses import dataclass, field

from scheduler import docker

@dataclass()
class Job:
    """Class to define a scheduled job."""

    name: str
    jobtype: str
    schedule: str
    command: str = field(default=None)
    network: str = field(default=None)
    image: str = field(default=None)
    container: str = field(default=None)
    user: str = field(default=None)
    environment: list[str] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)

    def is_container_running(self):
        if docker.get_running_by_name(self.container):
            return True
        else:
            return False

    def get_containers(self):
        return docker.get_running_by_job(self.name)

    def get_image_or_container(self):
        if self.jobtype == 'exec':
            return self.container
        if self.jobtype == 'run':
            return self.image