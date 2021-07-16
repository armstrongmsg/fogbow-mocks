from flask import Flask

import jsonpickle
import sys
import configparser


class RASMock:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("ras.ini")

    def pause_user_resources(self, user_id, provider):
        pass

    def hibernate_user_resources(self, user_id, provider):
        pass

    def stop_user_resources(self, user_id, provider):
        pass

    def resume_user_resources(self, user_id, provider):
        pass

    def purge_user(self, user_id, provider):
        pass
    
    def get_public_key(self):
        key_file_name = self.config["conf"]["public_key_file"]
        file = open(key_file_name)
        key = file.read()
        file.close()

        key = key.replace("\n", "")
        return jsonpickle.encode({"publicKey": key})

app = Flask(__name__)
ras_mock = RASMock()

@app.route('/ras/computes/pause/<user_id>/<provider>', methods = ['POST'])
def pause_user_resources(user_id, provider):
    ras_mock.pause_user_resources(user_id, provider)
    return "",200

@app.route('/ras/computes/hibernate/<user_id>/<provider>', methods = ['POST'])
def hibernate_user_resources(user_id, provider):
    ras_mock.hibernate_user_resources(user_id, provider)
    return "",200

@app.route('/ras/computes/stop/<user_id>/<provider>', methods = ['POST'])
def stop_user_resources(user_id, provider):
    ras_mock.stop_user_resources(user_id, provider)
    return "",200

@app.route('/ras/computes/resume/<user_id>/<provider>', methods = ['POST'])
def resume_user_resources(user_id, provider):
    ras_mock.resume_user_resources(user_id, provider)
    return "",200

@app.route('/ras/admin/purge/<user_id>/<provider>', methods = ['DELETE'])
def purge_user(user_id, provider):
    ras_mock.purge_user(user_id, provider)
    return "",200

@app.route('/ras/publicKey', methods = ['GET'])
def get_public_key():
    return ras_mock.get_public_key(),200

app.run(host=sys.argv[1], port=sys.argv[2], debug=True)