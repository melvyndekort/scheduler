class Job:

    def __init__(self, name, jobtype, image, schedule, command):
        self.name = name
        self.jobtype = jobtype
        self.image = image
        self.schedule = schedule
        self.command = command
        self.containers = []

    def addContainer(self, container):
        self.containers.append(container)
