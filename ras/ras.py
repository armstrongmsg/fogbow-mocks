from flask import Flask

import jsonpickle
import sys
import configparser


class RASMock:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("ras.ini")

        key_file_name = self.config["conf"]["public_key_file"]
        file = open(key_file_name)
        key = file.read()
        file.close()

        self.key = key.replace("\n", "")

        self.pause_return_code = int(self.config["response_code"]["pause"])
        self.hibernate_return_code = int(self.config["response_code"]["hibernate"])
        self.stop_return_code = int(self.config["response_code"]["stop"])
        self.resume_return_code = int(self.config["response_code"]["resume"])
        self.purge_return_code = int(self.config["response_code"]["purge"])

    def pause_user_resources(self, user_id, provider):
        return self.pause_return_code

    def hibernate_user_resources(self, user_id, provider):
        return self.hibernate_return_code

    def stop_user_resources(self, user_id, provider):
        return self.stop_return_code

    def resume_user_resources(self, user_id, provider):
        return self.resume_return_code

    def purge_user(self, user_id, provider):
        return self.purge_return_code
    
    def get_public_key(self):
        return jsonpickle.encode({"publicKey": self.key})

app = Flask(__name__)
ras_mock = RASMock()

@app.route('/ras/computes/pause/<user_id>/<provider>', methods = ['POST'])
def pause_user_resources(user_id, provider):
    return_code = ras_mock.pause_user_resources(user_id, provider)
    return "",return_code

@app.route('/ras/computes/hibernate/<user_id>/<provider>', methods = ['POST'])
def hibernate_user_resources(user_id, provider):
    return_code = ras_mock.hibernate_user_resources(user_id, provider)
    return "",return_code

@app.route('/ras/computes/stop/<user_id>/<provider>', methods = ['POST'])
def stop_user_resources(user_id, provider):
    return_code = ras_mock.stop_user_resources(user_id, provider)
    return "",return_code

@app.route('/ras/computes/resume/<user_id>/<provider>', methods = ['POST'])
def resume_user_resources(user_id, provider):
    return_code = ras_mock.resume_user_resources(user_id, provider)
    return "",return_code

@app.route('/ras/admin/purge/<user_id>/<provider>', methods = ['DELETE'])
def purge_user(user_id, provider):
    return_code = ras_mock.purge_user(user_id, provider)
    return "",return_code

@app.route('/ras/publicKey', methods = ['GET'])
def get_public_key():
    return ras_mock.get_public_key(),200

app.run(host=sys.argv[1], port=sys.argv[2], debug=True)