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
        historyId = self.config[compute_conf_label]["history_id"]
        state_history_1 = self.config[compute_conf_label]["state_history_1"]
        state_history_2 = self.config[compute_conf_label]["state_history_2"]

        if state == "FULFILLED":
            end_timestamp = datetime.strptime(end_date, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = datetime.strptime(start_date, REQUEST_TIME_FORMAT).timestamp()
            end_timestamp = end_timestamp - (end_timestamp - start_timestamp)/2.0
            start_timestamp = end_timestamp - duration
            
            startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            startDate = startTime
            endTime = datetime.fromtimestamp(end_timestamp).strftime(RESPONSE_TIME_FORMAT)
            endDate = endTime

            state_change_interval = (end_timestamp - start_timestamp)/4

            timestamp_state_1 = start_timestamp + state_change_interval
            timestamp_state_2 = start_timestamp + 2*state_change_interval

            timestamp_state_1_str = datetime.fromtimestamp(timestamp_state_1).strftime(RESPONSE_TIME_FORMAT)
            timestamp_state_2_str = datetime.fromtimestamp(timestamp_state_2).strftime(RESPONSE_TIME_FORMAT)
        else:
            end_timestamp = datetime.strptime(end_date, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = end_timestamp - duration
            startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            startDate = startTime
            endTime = None
            endDate = None

            state_change_interval = (end_timestamp - start_timestamp)/4

            timestamp_state_1 = start_timestamp + state_change_interval
            timestamp_state_2 = start_timestamp + 2*state_change_interval

            timestamp_state_1_str = datetime.fromtimestamp(timestamp_state_1).strftime(RESPONSE_TIME_FORMAT)
            timestamp_state_2_str = datetime.fromtimestamp(timestamp_state_2).strftime(RESPONSE_TIME_FORMAT)

        conf = {
                "id": recordId, 
                "orderId": orderId,
                "resourceType": "compute",
                "spec": {
                            "id": specId, 
                            "vCpu":vCpu, 
                            "ram":ram
                        },
                "stateHistory": {
                                    "id": historyId,
                                    "history": {
                                                    timestamp_state_1_str: state_history_1,
                                                    timestamp_state_2_str: state_history_2
                                               }
                                },
                "requester": requester,
                "startTime": startTime,
                "startDate": startDate,
                "endDate": endDate,
                "endTime": endTime,
                "duration": duration,
                "state": state
            }
        
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
        requester = self.config[volume_conf_label]["requester"]
        historyId = self.config[volume_conf_label]["history_id"]
        state_history_1 = self.config[volume_conf_label]["state_history_1"]
        state_history_2 = self.config[volume_conf_label]["state_history_2"]
        size = int(self.config[volume_conf_label]["size"])

        if state == "FULFILLED":
            end_timestamp = datetime.strptime(end_date, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = datetime.strptime(start_date, REQUEST_TIME_FORMAT).timestamp()
            end_timestamp = end_timestamp - (end_timestamp - start_timestamp)/2.0
            start_timestamp = end_timestamp - duration

            startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            startDate = startTime
            endTime = datetime.fromtimestamp(end_timestamp).strftime(RESPONSE_TIME_FORMAT)
            endDate = endTime


            state_change_interval = (end_timestamp - start_timestamp)/4

            timestamp_state_1 = start_timestamp + state_change_interval
            timestamp_state_2 = start_timestamp + 2*state_change_interval

            timestamp_state_1_str = datetime.fromtimestamp(timestamp_state_1).strftime(RESPONSE_TIME_FORMAT)
            timestamp_state_2_str = datetime.fromtimestamp(timestamp_state_2).strftime(RESPONSE_TIME_FORMAT)
        else:
            end_timestamp = datetime.strptime(end_date, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = end_timestamp - duration
            startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            startDate = startTime
            endTime = None
            endDate = None


            state_change_interval = (end_timestamp - start_timestamp)/4

            timestamp_state_1 = start_timestamp + state_change_interval
            timestamp_state_2 = start_timestamp + 2*state_change_interval

            timestamp_state_1_str = datetime.fromtimestamp(timestamp_state_1).strftime(RESPONSE_TIME_FORMAT)
            timestamp_state_2_str = datetime.fromtimestamp(timestamp_state_2).strftime(RESPONSE_TIME_FORMAT)

        conf = {
                "id": recordId, 
                "orderId": orderId,
                "resourceType": "volume",
                "spec": {
                            "id": specId, 
                            "size":size
                        },
                "stateHistory": {
                                    "id": historyId,
                                    "history": {
                                                    timestamp_state_1_str: state_history_1,
                                                    timestamp_state_2_str: state_history_2
                                               }
                                },
                "requester": requester,
                "startTime": startTime,
                "startDate": startDate,
                "endDate": endDate,
                "endTime": endTime,
                "duration": duration,
                "state": state
            }

        return conf

    def _get_network_usage(self, user_id, requester_id, provider_id, start_date, end_date):
        network_usage = []

        for network_conf_label in self.config["conf"]["network_conf_labels"].split(","):
            conf = self._get_network_conf(network_conf_label, user_id, requester_id, provider_id, start_date, end_date)
            network_usage.append(conf)
        
        return network_usage

    def _get_network_conf(self, network_conf_label, user_id, requester_id, provider_id, start_date, end_date):
        state = self.config[network_conf_label]["state"]
        duration = int(self.config[network_conf_label]["duration"])
        recordId = int(self.config[network_conf_label]["recordId"])
        orderId = self.config[network_conf_label]["orderId"]
        specId = int(self.config[network_conf_label]["specId"])
        cidr = self.config[network_conf_label]["cidr"]
        allocation_mode = self.config[network_conf_label]["allocation_mode"]
        requester = self.config[network_conf_label]["requester"]
        historyId = self.config[network_conf_label]["history_id"]
        state_history_1 = self.config[network_conf_label]["state_history_1"]
        state_history_2 = self.config[network_conf_label]["state_history_2"]

        if state == "FULFILLED":
            end_timestamp = datetime.strptime(end_date, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = datetime.strptime(start_date, REQUEST_TIME_FORMAT).timestamp()
            end_timestamp = end_timestamp - (end_timestamp - start_timestamp)/2.0
            start_timestamp = end_timestamp - duration

            startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            startDate = startTime
            endTime = datetime.fromtimestamp(end_timestamp).strftime(RESPONSE_TIME_FORMAT)
            endDate = endTime


            state_change_interval = (end_timestamp - start_timestamp)/4

            timestamp_state_1 = start_timestamp + state_change_interval
            timestamp_state_2 = start_timestamp + 2*state_change_interval

            timestamp_state_1_str = datetime.fromtimestamp(timestamp_state_1).strftime(RESPONSE_TIME_FORMAT)
            timestamp_state_2_str = datetime.fromtimestamp(timestamp_state_2).strftime(RESPONSE_TIME_FORMAT)
        else:
            end_timestamp = datetime.strptime(end_date, REQUEST_TIME_FORMAT).timestamp()
            start_timestamp = end_timestamp - duration
            startTime = datetime.fromtimestamp(start_timestamp).strftime(RESPONSE_TIME_FORMAT)
            startDate = startTime
            endTime = None
            endDate = None


            state_change_interval = (end_timestamp - start_timestamp)/4

            timestamp_state_1 = start_timestamp + state_change_interval
            timestamp_state_2 = start_timestamp + 2*state_change_interval

            timestamp_state_1_str = datetime.fromtimestamp(timestamp_state_1).strftime(RESPONSE_TIME_FORMAT)
            timestamp_state_2_str = datetime.fromtimestamp(timestamp_state_2).strftime(RESPONSE_TIME_FORMAT)

        conf = {
                "id": recordId, 
                "orderId": orderId,
                "resourceType": "network",
                "spec": {
                            "id": specId, 
                            "cidr":cidr,
                            "allocationMode":allocation_mode
                        },
                "stateHistory": {
                                    "id": historyId,
                                    "history": {
                                                    timestamp_state_1_str: state_history_1,
                                                    timestamp_state_2_str: state_history_2
                                               }
                                },
                "requester": requester,
                "startTime": startTime,
                "startDate": startDate,
                "endDate": endDate,
                "endTime": endTime,
                "duration": duration,
                "state": state
            }

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

@app.route('/accs/usage/<user_id>/<requester_id>/<provider_id>/<start_date>/<end_date>', methods = ['GET'])
def get_all_resources_user_usage(user_id, requester_id, provider_id, start_date, end_date):
    return accs_mock.get_all_resources_user_usage(user_id, requester_id, provider_id, start_date, end_date),200

@app.route('/accs/publicKey', methods = ['GET'])
def get_public_key():
    return accs_mock.get_public_key(),200

app.run(host=sys.argv[1], port=sys.argv[2], debug=True)
