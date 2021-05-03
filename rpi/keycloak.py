import json
import requests
import logging
import jwt

logging.basicConfig()
log = logging.getLogger()
logging.root.setLevel(logging.NOTSET)
logging.basicConfig(level=logging.NOTSET)

class Keycloak:
    def __init__(self, admin_client_secret, member_client_secret, host):
        self.access_token = None
        self.refresh_token = None
        self.admin_client_secret = admin_client_secret
        self.member_client_secret = member_client_secret
        self.host = host

        self.admin_log_in()

    def admin_log_in(self):
        """
            Performs admin login on object instantiation.

            If login is successfull it will set access and refresh token.
        """
        url = f"http://{self.host}:8080/auth/realms/master/protocol/openid-connect/token"
        payload = f"grant_type=client_credentials&client_id=admin-cli&client_secret={self.admin_client_secret}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            log.info("Successfully logged in to keycloak as admin-cli")
            response_json = json.loads(response.text.encode("utf8"))

            self.access_token = response_json["access_token"]
            self.refresh_token = response_json["refresh_token"]
        else:
            log.critical("There is a problem logging to Keycloak as admin-cli")

    def verify_admin_token(self):
        """
            Verify is the access token valid.

            If the access token is not valid it will use refresh token to get new access token.
        """
        url = f"http://{self.host}:8080/auth/admin/realms/pelbox/users?username=test&enabled=true"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            log.info("Keycloak admin token not valid. Refreshing")
            self.refresh_admin_tokens()
        else:
            log.info("Keycloak admin token valid.")

    def refresh_admin_tokens(self):
        """
            Get new access and refresh token.
        """
        url = f"http://{self.host}:8080/auth/realms/master/protocol/openid-connect/token"
        payload = f"grant_type=refresh_token&client_id=admin-cli&refresh_token={self.refresh_token}&client_secret={self.admin_client_secret}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            response_json = json.loads(response.text.encode("utf8"))
            self.access_token = response_json["access_token"]
            self.refresh_token = response_json["refresh_token"]
        elif response.status_code == 400:
            log.critical("Token is not active. New admin login.")
            self.admin_log_in()
        else:
            log.critical("Can't get new acccess and refresh token.")
            log.critical(json.loads(response.text.encode("utf8")))


    def register(self, member):
        """
            Register member within keycloak.

            Based on the member object of type Member define payload with the appropriate values and perform insert
            on the /users endpoint within the realm.
        """
        self.verify_admin_token()

        url = f"http://{self.host}:8080/auth/admin/realms/pelbox/users"
        payload = {
            "email": member.email,
            "enabled": "true",
            "username": member.username,
            "credentials": [
                {
                    "type": "password",
                    "temporary": "false",
                    "value": member.password
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            log.info("Member is successfully register within keycloak.")
            return True
        else:
            log.critical("There is an error with registring member within keycloak")
            log.critical(response.text.encode("utf8"))
            return False

    def member_login(self, member):
        """
            Login member withing keycloak.

            If member credentials are good member with be logged in and tokens will be returned.
        """
        url = f"http://{self.host}:8080/auth/realms/pelbox/protocol/openid-connect/token"
        payload = f"client_id=pelbox-users&grant_type=password&client_secret={self.member_client_secret}&scope=openid&username={member.username}&password={member.password}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, headers=headers, data=payload)
        response_json = json.loads(response.text.encode("utf8"))

        if response.status_code == 200:
            response_json["success"] = True
            return response_json

        if "error" in response_json:
            return {"success": False, "message": response_json["error_description"]}

    def is_member_logged(self, access_token):
        """
            Check is member logged in.

            Based on the id provided from the URI into this function verify member session.

            Args:
                id: member id within application
            Returns:
                If session is present it will return true, otherwise false
        """
        self.verify_admin_token()
        
        try:
            id = jwt.decode(access_token, verify=False)["sub"]
        except jwt.exceptions.DecodeError as e:
            log.critical(e)
            return False, 500

        url = f"http://{self.host}:8080/auth/admin/realms/pelbox/users/{id}/sessions"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_json = json.loads(response.text.encode("utf8"))
            if len(response_json) >= 1:
                return True, 200
            else:
                return False, 200
        else:
            return False, 500

    def get_member_id(self, username):
        self.verify_admin_token()

        url = f"http://{self.host}:8080/auth/admin/realms/pelbox/users?username={username}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_json = json.loads(response.text.encode("utf8"))
            id = response_json[0]["id"]
            return id
        return None