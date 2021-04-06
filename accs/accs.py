from flask import Flask
from datetime import datetime

import json
import jsonpickle
import sys
import configparser


REQUEST_TIME_FORMAT = "%Y-%m-%d"
RESPONSE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000+00:00"


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
        usage = None

        if resource == "compute":
            usage = self._get_compute_usage(user_id, requester_id, provider_id, start_date, end_date)
        elif resource == "volume":
            usage = self._get_volume_usage(user_id, requester_id, provider_id, start_date, end_date)

        return jsonpickle.encode(usage)

    def _get_compute_usage(self, user_id, requester_id, provider_id, start_date, end_date):
        compute_usage = []

        for compute_conf_label in self.config["conf"]["compute_conf_labels"].split(","):
            conf = self._get_compute_conf(compute_conf_label, user_id, requester_id, provider_id, start_date, end_date)
            compute_usage.append(conf)
        
        return compute_usage

    def _get_compute_conf(self, compute_conf_label, user_id, requester_id, provider_id, start_date, end_date):
        state = self.config[compute_conf_label]["state"]
        duration = int(self.config[compute_conf_label]["duration"])
        recordId = int(self.config[compute_conf_label]["recordId"])
        orderId = self.config[compute_conf_label]["orderId"]
        specId = int(self.config[compute_conf_label]["specId"])
        vCpu = int(self.config[compute_conf_label]["vCpu"])
        ram = int(self.config[compute_conf_label]["ram"])
        requester = self.config[compute_conf_label]["requester"]

        if state == "FULFILLED":
            end_timestamp = datetime.strptime(end_date, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = datetime.strptime(start_date, REQUEST_TIME_FORMAT).timestamp()
            end_timestamp = end_timestamp - (end_timestamp - start_timestamp)/2.0
            start_timestamp = end_timestamp - duration
            
            startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            startDate = startTime
            endTime = datetime.fromtimestamp(end_timestamp).strftime(RESPONSE_TIME_FORMAT)
            endDate = endTime
        else:
            end_timestamp = datetime.strptime(end_date, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = end_timestamp - duration
            startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            startDate = startTime
            endTime = None
            endDate = None

        conf = {
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
        print(conf)
        return conf

    def _get_volume_usage(self, user_id, requester_id, provider_id, start_date, end_date):
        volume_usage = []

        for volume_conf_label in self.config["conf"]["volume_conf_labels"].split(","):
            conf = self._get_volume_conf(volume_conf_label, user_id, requester_id, provider_id, start_date, end_date)
            volume_usage.append(conf)
        
        return volume_usage

    def _get_volume_conf(self, volume_conf_label, user_id, requester_id, provider_id, start_date, end_date):
        state = self.config[volume_conf_label]["state"]
        duration = int(self.config[volume_conf_label]["duration"])
        recordId = int(self.config[volume_conf_label]["recordId"])
        orderId = self.config[volume_conf_label]["orderId"]
        specId = int(self.config[volume_conf_label]["specId"])
        size = int(self.config[volume_conf_label]["size"])
        requester = self.config[volume_conf_label]["requester"]

        if state == "FULFILLED":
            end_timestamp = datetime.strptime(end_date, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = datetime.strptime(start_date, REQUEST_TIME_FORMAT).timestamp()
            end_timestamp = end_timestamp - (end_timestamp - start_timestamp)/2.0
            start_timestamp = end_timestamp - duration

            startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            startDate = startTime
            endTime = datetime.fromtimestamp(end_timestamp).strftime(RESPONSE_TIME_FORMAT)
            endDate = endTime
        else:
            end_timestamp = datetime.strptime(end_date, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = end_timestamp - duration
            startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            startDate = startTime
            endTime = None
            endDate = None

        conf = {
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

        print(conf)
        return conf

    def get_public_key(self):
        key_file_name = self.config["conf"]["public_key_file"]
        file = open(key_file_name)
        key = file.read()
        file.close()

        key = key.replace("\n", "")
        c = {"publicKey": key}

        return jsonpickle.encode(c)

app = Flask(__name__)
accs_mock = ACCSMock()

@app.route('/accs/usage/<user_id>/<requester_id>/<provider_id>/<resource>/<start_date>/<end_date>', methods = ['GET'])
def get_user_usage(user_id, requester_id, provider_id, resource, start_date, end_date):
    return accs_mock.get_user_usage(user_id, requester_id, provider_id, resource, start_date, end_date),200

@app.route('/accs/publicKey', methods = ['GET'])
def get_public_key():
    return accs_mock.get_public_key(),200

app.run(host=sys.argv[1], port=sys.argv[2], debug=True)
