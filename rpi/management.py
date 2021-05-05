from flask import Blueprint, jsonify, request
from environs import Env
import logging
import psycopg2
import json
import jwt
import time

import RPi.GPIO as GPIO

from rpi.member import Member
from rpi.pelbox_member import PelBox

from rpi import common
from rpi.keycloak import Keycloak

relay = 21
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

GPIO.setup(relay,GPIO.OUT)
GPIO.output(relay , 0)

logging.basicConfig()
log = logging.getLogger()
logging.root.setLevel(logging.NOTSET)
logging.basicConfig(level=logging.NOTSET)

management = Blueprint("management", __name__)

env = Env()
env.read_env()

class Motor():
    def __init__(self, In1, In2):
        self.In1 = In1
        self.In2 = In2
        GPIO.setup(self.In1,GPIO.OUT)
        GPIO.setup(self.In2,GPIO.OUT)
        
        self.pwm1 = GPIO.PWM(self.In1, 100) # Apply full voltage to device
        self.pwm2 = GPIO.PWM(self.In2, 100) # Apply full voltage to device
        self.pwm1.start(0) # start with motor off
        self.pwm2.start(0) # start with motor off
        
    def moveForward(self, speed, t=0): # 'speed' allows the user to input spee
        GPIO.output(self.In1, GPIO.LOW)
        GPIO.output(self.In2, GPIO.HIGH)
        self.pwm2.ChangeDutyCycle(speed)
        time.sleep(t)                        # delay
        
    def moveBackward(self, speed, t=0): # 'speed' allows the user to input spee
        GPIO.output(self.In1, GPIO.HIGH)
        GPIO.output(self.In2, GPIO.LOW)
        self.pwm1.ChangeDutyCycle(speed)
        time.sleep(t)                        # delay
    
    def stop(self):
        self.pwm1.ChangeDutyCycle(0)
        self.pwm2.ChangeDutyCycle(0)

motor1  = Motor(13, 6)
motor2  = Motor(17, 27)
motor3  = Motor(23, 24)

previous_user_expanded_value = None
box_expanded_to_full = False

keycloak = Keycloak(env.str("ADMIN_CLIENT_SECRET"), env.str("MEMBER_CLIENT_SECRET"), env.str("KEYCLOAK_HOST"))

try:
    log.info(f"Connecting to {env.str('DB_NAME')} database from Raspberry Pi")
    conn = psycopg2.connect(host=env.str("DB_HOST"),
                            port=env.str("DB_PORT"),
                            database=env.str("DB_NAME"),
                            user=env.str("DB_USER"),
                            password=env.str("DB_PASSWORD"))
    log.info(f"Connected to {env.str('DB_NAME')} database")
except Exception as e:
    log.critical(e)

@management.route("/locking_state", methods=["GET"])
def locking_state():
    try:
        data_json = dict(request.headers)
        data_json = {key: None if data_json[key] == "" else data_json[key] for key in data_json}

        logged_in, status_code = keycloak.is_member_logged(data_json["Access-Token"])
        if status_code == 200 and logged_in:
            username = jwt.decode(data_json["Access-Token"], verify=False)["preferred_username"]
            member_details = common.get_member_details(username)
            member = Member.new(*member_details)

            pelbox_settings = common.get_pelbox_settings(member.id)
            pelbox = PelBox.new(*pelbox_settings)

            status = pelbox.user_security_key != None and pelbox.user_security_key == env.str("APP_SECRET")
            common.set_box_connected(pelbox.user_security_key, member.id, status)
            return jsonify({"success": status, "settings": pelbox.json_data()}), 200, {"ContentType":"application/json"}
        elif status_code == 200 and not logged_in:
            return jsonify({"success": False, "message": f"Member is not logged in"}), 401, {"ContentType":"application/json"}
        else:
            return jsonify({"success": False, "message": f"Something went wrong"}), 500, {"ContentType":"application/json"}
    except KeyError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "Missing arguments"}), 400, {"ContentType":"application/json"}
    except json.decoder.JSONDecodeError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "JSON is badly formatted"}), 400, {"ContentType":"application/json"}

@management.route("/set_locking", methods=["PUT"])
def locking():
    try:
        data_json = json.loads(request.data.decode("utf-8"))
        data_json = {key: None if data_json[key] == "" else data_json[key] for key in data_json}
 
        logged_in, status_code = keycloak.is_member_logged(data_json["access_token"])
        if status_code == 200 and logged_in:
            username = jwt.decode(data_json["access_token"], verify=False)["preferred_username"]
            member_details = common.get_member_details(username)
            member = Member.new(*member_details)

            common.update_locking(member.id, data_json["locked"])
            return jsonify({"success": True}), 200, {"ContentType":"application/json"}
        elif status_code == 200 and not logged_in:
            return jsonify({"success": False, "message": f"Member is not logged in"}), 401, {"ContentType":"application/json"}
        else:
            return jsonify({"success": False, "message": f"Something went wrong"}), 500, {"ContentType":"application/json"}
    except KeyError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "Missing arguments"}), 400, {"ContentType":"application/json"}
    except json.decoder.JSONDecodeError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "JSON is badly formatted"}), 400, {"ContentType":"application/json"}

@management.route("/dismantle_state", methods=["GET"])
def dismantle_state():
    try:
        data_json = dict(request.headers)
        data_json = {key: None if data_json[key] == "" else data_json[key] for key in data_json}

        logged_in, status_code = keycloak.is_member_logged(data_json["Access-Token"])
        if status_code == 200 and logged_in:
            username = jwt.decode(data_json["Access-Token"], verify=False)["preferred_username"]
            member_details = common.get_member_details(username)
            member = Member.new(*member_details)

            pelbox_settings = common.get_pelbox_settings(member.id)
            pelbox = PelBox.new(*pelbox_settings)

            status = pelbox.user_security_key != None and pelbox.user_security_key == env.str("APP_SECRET")
            common.set_box_connected(pelbox.user_security_key, member.id, status)
            return jsonify({"success": status, "settings": pelbox.json_data()}), 200, {"ContentType":"application/json"}
        elif status_code == 200 and not logged_in:
            return jsonify({"success": False, "message": f"Member is not logged in"}), 401, {"ContentType":"application/json"}
        else:
            return jsonify({"success": False, "message": f"Something went wrong"}), 500, {"ContentType":"application/json"}
    except KeyError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "Missing arguments"}), 400, {"ContentType":"application/json"}
    except json.decoder.JSONDecodeError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "JSON is badly formatted"}), 400, {"ContentType":"application/json"}

@management.route("/set_dismantle", methods=["PUT"])
def dismantle():
    try:
        data_json = json.loads(request.data.decode("utf-8"))
        data_json = {key: None if data_json[key] == "" else data_json[key] for key in data_json}
 
        logged_in, status_code = keycloak.is_member_logged(data_json["access_token"])
        if status_code == 200 and logged_in:
            username = jwt.decode(data_json["access_token"], verify=False)["preferred_username"]
            member_details = common.get_member_details(username)
            member = Member.new(*member_details)

            common.update_dismantle(member.id, data_json["dismantle"])
            if data_json["dismantle"]:
                GPIO.output(relay, 1)
            else:
                GPIO.output(relay, 0)
            return jsonify({"success": True}), 200, {"ContentType":"application/json"}
        elif status_code == 200 and not logged_in:
            return jsonify({"success": False, "message": f"Member is not logged in"}), 401, {"ContentType":"application/json"}
        else:
            return jsonify({"success": False, "message": f"Something went wrong"}), 500, {"ContentType":"application/json"}
    except KeyError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "Missing arguments"}), 400, {"ContentType":"application/json"}
    except json.decoder.JSONDecodeError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "JSON is badly formatted"}), 400, {"ContentType":"application/json"}

def move_motors_full_forward(current_value):
    motor1.moveForward(100, 5 - current_value) # Move Forward with 80% voltage for value seconds
    time.sleep(0.25) 
    motor1.stop()

    global box_expanded_to_full
    box_expanded_to_full = True
    motor2.moveForward(100, 2)
    time.sleep(1) 
    motor2.stop()

def move_motors_full_backward(current_value):
    motor1.moveBackward(100, 5 - current_value) # Move Forward with 80% voltage for value seconds
    time.sleep(0.25) 
    motor1.stop()

    global box_expanded_to_full
    box_expanded_to_full = False
    motor2.moveBackward(100, 2)
    time.sleep(1)
    motor2.stop()

def move_motors_forward(value):
    motor1.moveForward(100, 1) # Move Forward with 80% voltage for value seconds
    time.sleep(0.25) 
    motor1.stop()

def move_motors_back(value):
    motor1.moveBackward(100, 1)
    time.sleep(0.25)
    motor1.stop()

@management.route("/set_expanding_value", methods=["PUT"])
def expanding_value():
    try:
        data_json = json.loads(request.data.decode("utf-8"))
        data_json = {key: None if data_json[key] == "" else data_json[key] for key in data_json}
 
        logged_in, status_code = keycloak.is_member_logged(data_json["access_token"])
        if status_code == 200 and logged_in:
            username = jwt.decode(data_json["access_token"], verify=False)["preferred_username"]
            member_details = common.get_member_details(username)
            member = Member.new(*member_details)

            pelbox_settings = common.get_pelbox_settings(member.id)
            pelbox = PelBox.new(*pelbox_settings)

            global previous_user_expanded_value
            if previous_user_expanded_value == None:
                previous_user_expanded_value = pelbox.expanding_value

            expanding_value = data_json["expanding-value"]
            if expanding_value == 5:
                move_motors_full_forward(pelbox.expanding_value)
            elif expanding_value == 0:
                move_motors_full_backward(pelbox.expanding_value)
            elif previous_user_expanded_value < expanding_value:
                move_motors_forward(expanding_value)
            else:
                move_motors_back(expanding_value)

            previous_user_expanded_value = expanding_value

            common.update_expanding_value(member.id, expanding_value)
            return jsonify({"success": True}), 200, {"ContentType":"application/json"}
        elif status_code == 200 and not logged_in:
            return jsonify({"success": False, "message": f"Member is not logged in"}), 401, {"ContentType":"application/json"}
        else:
            return jsonify({"success": False, "message": f"Something went wrong"}), 500, {"ContentType":"application/json"}
    except KeyError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "Missing arguments"}), 400, {"ContentType":"application/json"}
    except json.decoder.JSONDecodeError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "JSON is badly formatted"}), 400, {"ContentType":"application/json"}


@management.route("/set_door_status", methods=["PUT"])
def set_door_status():
    try:
        data_json = json.loads(request.data.decode("utf-8"))
        data_json = {key: None if data_json[key] == "" else data_json[key] for key in data_json}
 
        logged_in, status_code = keycloak.is_member_logged(data_json["access_token"])
        if status_code == 200 and logged_in:
            username = jwt.decode(data_json["access_token"], verify=False)["preferred_username"]
            member_details = common.get_member_details(username)
            member = Member.new(*member_details)

            pelbox_settings = common.get_pelbox_settings(member.id)
            pelbox = PelBox.new(*pelbox_settings)

            door_status = data_json["door_status"]
            if door_status == "open" and pelbox.door_open == False:
                motor3.moveForward(100, 8)
                time.sleep(2)
                motor3.stop()
            elif door_status == "close" and pelbox.door_open == True:
                motor3.moveBackward(100, 8)
                time.sleep(2)
                motor3.stop()

            common.update_door_status(member.id, True if door_status == "open" else False)
            return jsonify({"success": True}), 200, {"ContentType":"application/json"}
        elif status_code == 200 and not logged_in:
            return jsonify({"success": False, "message": f"Member is not logged in"}), 401, {"ContentType":"application/json"}
        else:
            return jsonify({"success": False, "message": f"Something went wrong"}), 500, {"ContentType":"application/json"}
    except KeyError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "Missing arguments"}), 400, {"ContentType":"application/json"}
    except json.decoder.JSONDecodeError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "JSON is badly formatted"}), 400, {"ContentType":"application/json"}
