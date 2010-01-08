#!/usr/bin/python

class ServiceError:
    def __init__(self, message):
        self.message = message

class Service:
    def __init__(self, params):
        #   Init the instance vars
        self.ports = None
        self.protocols = []
        self.interfaces = None
        self.ip = None
        self.mac = None
        self.description = None

