from flask import Flask

import json
import jsonpickle
import sys
import configparser


class Compute_Spec:
    def __init__(self, id, vCpu, ram):
        self.id = id
        self.vCpu = vCpu
        self.ram = ram

class Network_Spec:
    def __init__(self, id, cidr):
        self.id = id
        self.cird = cidr

class Volume_Spec:
    def __init__(self, id, size):
        self.id = id
        self.size = size

class Record:
    def __init__(self, id, orderId, resourceType, spec, requester, startTime, startDate, endDate, endTime, duration, state):
        self.id = id
        self.orderId = orderId
        self.resourceType = resourceType
        self.spec = spec
        self.requester = requester
        self.startTime = startTime
        self.startDate = startDate
        self.endDate = endDate
        self.endTime = endTime
        self.duration = duration
        self.state = state

class ACCSMock:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("accs.ini")

    def get_user_usage(self, user_id, requester_id, provider_id, resource, start_date, end_date):
        recordId = int(self.config["compute"]["recordId"])
        orderId = self.config["compute"]["orderId"]
        r = None

        if resource == "compute":
            specId = int(self.config["compute"]["specId"])
            vCpu = int(self.config["compute"]["vCpu"])
            ram = int(self.config["compute"]["ram"])
            requester = self.config["compute"]["requester"]
            startTime = self.config["compute"]["startTime"]
            startDate = self.config["compute"]["startDate"]
            endDate = self.config["compute"]["endDate"]
            endTime = self.config["compute"]["endTime"]
            duration = int(self.config["compute"]["duration"])
            state = self.config["compute"]["state"]

            r = {
                    "id": recordId, 
                    "orderId": orderId,
                    "resourceType": "compute",
                    "spec": {
                                "id": specId, 
                                "vCpu":vCpu, 
                                "ram":ram
                            }, 
                    "requester": requester,
                    "startTime": startTime,
                    "startDate": startDate,
                    "endDate": endDate,
                    "endTime": endTime,
                    "duration": duration,
                    "state": state
                }
        elif resource == "volume":
            specId = int(self.config["volume"]["specId"])
            size = int(self.config["volume"]["size"])
            requester = self.config["volume"]["requester"]
            startTime = self.config["volume"]["startTime"]
            startDate = self.config["volume"]["startDate"]
            endDate = self.config["volume"]["endDate"]
            endTime = self.config["volume"]["endTime"]
            duration = int(self.config["volume"]["duration"])
            state = self.config["volume"]["state"]

            r = {
                    "id": recordId, 
                    "orderId": orderId,
                    "resourceType": "volume",
                    "spec": {
                                "id": specId, 
                                "size":size
                            },
                    "requester": requester,
                    "startTime": startTime,
                    "startDate": startDate,
                    "endDate": endDate,
                    "endTime": endTime,
                    "duration": duration,
                    "state": state
                }

        return jsonpickle.encode([r])

    def get_public_key(self):
        key_file_name = self.config["conf"]["public_key_file"]
        file = open(key_file_name)
        key = file.read()
        file.close()

        c = {"publicKey": key}

        return jsonpickle.encode(c)

app = Flask(__name__)

@app.route('/hello')
def hello():
    return 'dfjadofjadifjsdfd',200

m = ACCSMock()
@app.route('/accs/usage/<user_id>/<requester_id>/<provider_id>/<resource>/<start_date>/<end_date>', methods = ['GET'])
def get_user_usage(user_id, requester_id, provider_id, resource, start_date, end_date):
    return m.get_user_usage(user_id, requester_id, provider_id, resource, start_date, end_date),200

@app.route('/accs/publicKey', methods = ['GET'])
def get_public_key():
    return m.get_public_key(),200
app.run(host=sys.argv[1], port=sys.argv[2], debug=True)

