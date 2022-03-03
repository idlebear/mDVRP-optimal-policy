from config import SERVICE_TIME

class Task:
    def __init__(self, id, location, time, service_time = SERVICE_TIME):
        self.id = id
        self.location = location
        self.time = time
        self.serviced = False
        self.time_serviced = -1
        self.service_time = service_time