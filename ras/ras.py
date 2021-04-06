from flask import Flask

import jsonpickle
import sys
import configparser


class RASMock:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("ras.ini")

    def pause_user_resources(self, user_id):
        pass

    def resume_user_resources(self, user_id):
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

@app.route('/ras/compute/pause/<user_id>', methods = ['POST'])
def pause_user_resources(user_id):
    ras_mock.pause_user_resources(user_id)
    return "",200

@app.route('/ras/compute/resume/<user_id>', methods = ['POST'])
def resume_user_resources(user_id):
    ras_mock.resume_user_resources(user_id)
    return "",200

@app.route('/ras/publicKey', methods = ['GET'])
def get_public_key():
    return ras_mock.get_public_key(),200

app.run(host=sys.argv[1], port=sys.argv[2], debug=True)