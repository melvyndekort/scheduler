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
    user: str = field(default='')
    environment: list[str] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)
    keep_containers: bool = field(default=False)

    def is_running(self):
        if self.jobtype == 'exec':
            return docker.is_running(self.container)
        elif self.jobtype == 'run':
            return docker.is_running(self.name)

    def get_image_or_container(self):
        if self.jobtype == 'exec':
            return self.container
        if self.jobtype == 'run':
            return self.image
