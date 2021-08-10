from flask import Flask
from datetime import datetime

import json
import jsonpickle
import sys
import configparser
import time
import os

REQUEST_TIME_FORMAT = "%Y-%m-%d_%H:%M:%S"
RESPONSE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000+00:00"


class Compute_Spec:
    def __init__(self, id, vCpu, ram):
        self.id = id
        self.vCpu = vCpu
        self.ram = ram

    def __init__(self, config, label):
        self.id = int(config[label]["specId"]) 
        self.vCpu = int(config[label]["vCpu"])
        self.ram = int(config[label]["ram"])

    def get_repr(self):
        return {
                "id": self.id, 
                "vCpu": self.vCpu, 
                "ram": self.ram
                }


class Network_Spec:
    def __init__(self, id, cidr):
        self.id = id
        self.cird = cidr

    def __init__(self, config, label):
        self.id = int(config[label]["specId"])
        self.cidr = config[label]["cidr"]
        self.allocation_mode = config[label]["allocation_mode"]

    def get_repr(self):
        return {
                "id": self.id, 
                "cidr": self.cidr,
                "allocationMode": self.allocation_mode
                }


class Volume_Spec:
    def __init__(self, id, size):
        self.id = id
        self.size = size

    def __init__(self, config, label):
        self.id = int(config[label]["specId"])
        self.size = int(config[label]["size"])
        
    def get_repr(self):
        return {
                "id": self.id, 
                "size": self.size
                }


class Record:
    def __init__(self, id, orderId, resourceType, spec, historyId, state_history_1, state_history_2, 
    requester, startDate, endDate, duration, state):
        self.id = id
        self.orderId = orderId
        self.resourceType = resourceType
        self.spec = spec
        self.historyId = historyId
        self.state_history_1 = state_history_1
        self.state_history_2 = state_history_2
        self.requester = requester
        self.startDate = startDate
        self.endDate = endDate
        self.duration = duration
        self.state = state

        if state == "CLOSED":
            end_timestamp = datetime.strptime(self.endDate, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = datetime.strptime(self.startDate, REQUEST_TIME_FORMAT).timestamp()
            end_timestamp = end_timestamp - (end_timestamp - start_timestamp)/2.0
            start_timestamp = end_timestamp - self.duration
            self.startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            self.startDate = self.startTime
            self.endTime = datetime.fromtimestamp(end_timestamp).strftime(RESPONSE_TIME_FORMAT)
            self.endDate = endTime
        else:
            end_timestamp = datetime.strptime(self.endDate, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = end_timestamp - duration
            self.startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            self.startDate = self.startTime
            self.endTime = None
            self.endDate = None

        state_change_interval = (end_timestamp - start_timestamp)/4

        timestamp_state_1 = start_timestamp + state_change_interval
        timestamp_state_2 = start_timestamp + 2*state_change_interval

        self.timestamp_state_1_str = datetime.fromtimestamp(timestamp_state_1).strftime(RESPONSE_TIME_FORMAT)
        self.timestamp_state_2_str = datetime.fromtimestamp(timestamp_state_2).strftime(RESPONSE_TIME_FORMAT)

    def get_repr(self):
        return {
                "id": self.id, 
                "orderId": self.orderId,
                "resourceType": self.resourceType,
                "spec": self.spec,
                "stateHistory": {
                                    "id": self.historyId,
                                    "history": {
                                                    self.timestamp_state_1_str: self.state_history_1,
                                                    self.timestamp_state_2_str: self.state_history_2
                                               }
                                },
                "requester": self.requester,
                "startTime": self.startTime,
                "startDate": self.startDate,
                "endDate": self.endDate,
                "endTime": self.endTime,
                "duration": self.duration,
                "state": self.state
            }


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

    def get_all_resources_user_usage(self, user_id, requester_id, provider_id, start_date, end_date):
        compute_usage = self._get_compute_usage(user_id, requester_id, provider_id, start_date, end_date)
        volume_usage = self._get_volume_usage(user_id, requester_id, provider_id, start_date, end_date)
        network_usage = self._get_network_usage(user_id, requester_id, provider_id, start_date, end_date)

        usage = []
        usage.extend(compute_usage)
        usage.extend(volume_usage)
        usage.extend(network_usage)

        return jsonpickle.encode(usage)

    def _get_compute_usage(self, user_id, requester_id, provider_id, start_date, end_date):
        compute_usage = []

        for compute_conf_label in self.config["conf"]["compute_conf_labels"].split(","):
            conf = self._get_generic_conf("compute", compute_conf_label, start_date, end_date)
            compute_usage.append(conf)
        
        return compute_usage

    def _get_volume_usage(self, user_id, requester_id, provider_id, start_date, end_date):
        volume_usage = []

        for volume_conf_label in self.config["conf"]["volume_conf_labels"].split(","):
            conf = self._get_generic_conf("volume", volume_conf_label, start_date, end_date)
            volume_usage.append(conf)
        
        return volume_usage

    def _get_network_usage(self, user_id, requester_id, provider_id, start_date, end_date):
        network_usage = []

        for network_conf_label in self.config["conf"]["network_conf_labels"].split(","):
            conf = self._get_generic_conf("network", network_conf_label, start_date, end_date)
            network_usage.append(conf)
        
        return network_usage

    def _get_generic_conf(self, conf_type, conf_label, start_date, end_date):
        state = self.config[conf_label]["state"]
        duration = int(self.config[conf_label]["duration"])
        recordId = int(self.config[conf_label]["recordId"])
        orderId = self.config[conf_label]["orderId"]
        requester = self.config[conf_label]["requester"]
        historyId = self.config[conf_label]["history_id"]
        state_history_1 = self.config[conf_label]["state_history_1"]
        state_history_2 = self.config[conf_label]["state_history_2"]
        
        if conf_type == "compute":
            spec = Compute_Spec(self.config, conf_label).get_repr()
        elif conf_type == "network":
            spec = Network_Spec(self.config, conf_label).get_repr()
        else:
            spec = Volume_Spec(self.config, conf_label).get_repr()

        return Record(recordId, orderId, conf_type, spec, historyId, state_history_1, state_history_2, 
        requester, start_date, end_date, duration, state).get_repr()

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

@app.route('/accs/usage/<user_id>/<requester_id>/<provider_id>/<start_date>/<end_date>', methods = ['GET'])
def get_all_resources_user_usage(user_id, requester_id, provider_id, start_date, end_date):
    return accs_mock.get_all_resources_user_usage(user_id, requester_id, provider_id, start_date, end_date),200

@app.route('/accs/publicKey', methods = ['GET'])
def get_public_key():
    return accs_mock.get_public_key(),200

app.run(host=sys.argv[1], port=sys.argv[2], debug=True)
