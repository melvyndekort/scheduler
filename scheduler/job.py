"""Job dataclass for scheduled tasks."""
from dataclasses import dataclass, field
from scheduler import docker


@dataclass()
class Job:  # pylint: disable=too-many-instance-attributes
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
    env_file: list[str] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)

    def is_running(self):
        """Check if the job's container is currently running."""
        if self.jobtype == 'exec':
            return docker.is_running(self.container)
        if self.jobtype == 'run':
            return docker.is_running(self.name)
        return False

    def get_image_or_container(self):
        """Get the image name for run jobs or container name for exec jobs."""
        if self.jobtype == 'exec':
            return self.container
        if self.jobtype == 'run':
            return self.image
        return None
