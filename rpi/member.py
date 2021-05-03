import json

class Member:
    def __init__(self, data):
        data_json = json.loads(data.decode("utf-8"))

        self.id = None
        self.username = data_json["username"]
        self.email = data_json["email"]
        self.password = data_json["password"]
        self.phone_token = data_json["phone_token"]

        self.access_token = None
        self.refresh_token = None
        self.first_name = None
        self.last_name = None
        self.gender = None
        self.country = None
        self.city = None
        self.city_address = None
        self.postal_code = None
        self.phone_number = None
        self.organization_name = None
        self.organization_id = None
        self.organization_email = None

    @staticmethod
    def new(id, username, email, first_name, last_name, gender, country, city, city_address, postal_code, phone_number, phone_token, organization_name, organization_id, organization_email):
        new_data = {
            "id": id,
            "username": username, 
            "email": email,
            "password": "",
            "first_name": first_name, 
            "last_name": last_name, 
            "gender": gender, 
            "country": country, 
            "city": city, 
            "city_address": city_address, 
            "postal_code": postal_code, 
            "phone_number": phone_number,
            "phone_token": phone_token,
            "organization_name": organization_name,
            "organization_id": organization_id,
            "organization_email": organization_email
        }

        member = Member(json.dumps(new_data).encode("utf-8"))
        member.id = new_data["id"]
        member.first_name = new_data["first_name"]
        member.last_name = new_data["last_name"]
        member.gender = new_data["gender"]
        member.country = new_data["country"]
        member.city = new_data["city"]
        member.city_address = new_data["city_address"]
        member.postal_code = new_data["postal_code"]
        member.phone_number = new_data["phone_number"]
        member.phone_token = new_data["phone_token"]
        member.organization_name = new_data["organization_name"]
        member.organization_id = new_data["organization_id"]
        member.organization_email = new_data["organization_email"]

        return member

    def json_data(self):
        return {
            "id": self.id,
            "username": self.username, 
            "email": self.email,
            "password": "",
            "first_name": self.first_name, 
            "last_name": self.last_name, 
            "gender": self.gender, 
            "country": self.country, 
            "city": self.city, 
            "city_address": self.city_address, 
            "postal_code": self.postal_code, 
            "phone_number": self.phone_number,
            "phone_token": self.phone_token,
            "organization_name": self.organization_name,
            "organization_id": self.organization_id,
            "organization_email": self.organization_email
        }