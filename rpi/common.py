import psycopg2
import logging
import requests
from environs import Env

import simplejson as sjson

logging.basicConfig()
log = logging.getLogger()
logging.root.setLevel(logging.NOTSET)
logging.basicConfig(level=logging.NOTSET)

env = Env()
env.read_env()

try:
    log.info(f"Connecting to {env.str('DB_NAME')} database from rpi.common module")
    conn = psycopg2.connect(host=env.str("DB_HOST"),
                            port=env.str("DB_PORT"),
                            database=env.str("DB_NAME"),
                            user=env.str("DB_USER"),
                            password=env.str("DB_PASSWORD"))
    log.info(f"Connected to {env.str('DB_NAME')} database")
except Exception as e:
    log.critical(e)

def member_exists(username, email):
    """
        Fetches rows from a memembers table.

        Retrivies rows that have in their column either username or email supplied from the arguments section.

        Args:
            username: members username, string type
            email: member email, string type

        Returns:
            If there are any rows matching username or an email returns True, otherwise False
    """
    try:
        cur = conn.cursor()
        query = "SELECT * FROM members WHERE username = %s OR email = %s"

        cur.execute(query, (username, email))
        row = cur.fetchone()
        cur.close()

        return row
    except Exception as e:
        log.critical(e)

def get_member_details(username):
    """
        Returns member details by the username provided.
    """
    try:
        cur = conn.cursor()
        query = """
            SELECT m.id, m.username, m.email, md.first_name, md.last_name, md.gender, md.country, md.city, md.city_address, md.postal_code, md.phone_number, m.phone_token, o.name as organization_name, m.organization_id, o.email
            FROM members m
            INNER JOIN member_details md ON m.id = md.member_id
            LEFT JOIN organizations o ON m.organization_id = o.id
            WHERE m.username = %s;
        """

        cur.execute(query, (username,))
        row = cur.fetchone()
        cur.close()

        return row
    except Exception as e:
        log.critical(e)

def get_pelbox_settings(member_id):
    """
        Returns pelbox details by the member id provided.
    """
    try:
        cur = conn.cursor()
        query = """
           	SELECT rd.id, rd.security_key, rd.user_security_key, rd.host, rd.member_id, rd.connected, bl.locked, bl.dismantle, bl.expanding_value
           	FROM rpi_devices rd
            INNER JOIN box_locking bl ON bl.member_id = rd.member_id
           	WHERE rd.member_id = %s
        """

        cur.execute(query, (member_id,))
        row = cur.fetchone()
        cur.close()

        return row
    except Exception as e:
        log.critical(e)

def update_first_name(first_name, username):
    """
        Updates member first name by the first_name provided where the key is username.
    """
    try:
        cur = conn.cursor()

        query = """
            WITH member_information (id)
            AS 
            (
                SELECT id FROM members WHERE username = %s
            )
            UPDATE member_details md
            SET first_name = %s
            FROM member_information
            WHERE md.member_id = member_information.id
        """

        cur.execute(query, (username,first_name))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def update_last_name(last_name, username):
    """
        Updates member last name by the last_name provided where the key is username.
    """
    try:
        cur = conn.cursor()

        query = """
            WITH member_information (id)
            AS 
            (
                SELECT id FROM members WHERE username = %s
            )
            UPDATE member_details md
            SET last_name = %s
            FROM member_information
            WHERE md.member_id = member_information.id
        """

        cur.execute(query, (username,last_name))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def update_city(city, username):
    """
        Updates member city by the city provided where the key is username.
    """
    try:
        cur = conn.cursor()

        query = """
            WITH member_information (id)
            AS 
            (
                SELECT id FROM members WHERE username = %s
            )
            UPDATE member_details md
            SET city = %s
            FROM member_information
            WHERE md.member_id = member_information.id
        """

        cur.execute(query, (username,city))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def update_city_address(city_address, username):
    """
        Updates member city_address by the city_address provided where the key is username.
    """
    try:
        cur = conn.cursor()

        query = """
            WITH member_information (id)
            AS 
            (
                SELECT id FROM members WHERE username = %s
            )
            UPDATE member_details md
            SET city_address = %s
            FROM member_information
            WHERE md.member_id = member_information.id
        """

        cur.execute(query, (username,city_address))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def update_postal_code(postal_code, username):
    """
        Updates member postal_code by the postal_code provided where the key is username.
    """
    try:
        cur = conn.cursor()

        query = """
            WITH member_information (id)
            AS 
            (
                SELECT id FROM members WHERE username = %s
            )
            UPDATE member_details md
            SET postal_code = %s
            FROM member_information
            WHERE md.member_id = member_information.id
        """

        cur.execute(query, (username,postal_code))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def get_countries():
    """
        Return all countries with country codes.
    """
    try:
        cur = conn.cursor()

        query = """
            SELECT id, name, code 
            FROM country_list
        """

        cur.execute(query)
        rows = cur.fetchall()
        cur.close()

        return [{row[2].lower(): {"id": row[0], "name": row[1]}} for row in rows]
    except Exception as e:
        log.critical(e)

def update_member_country_name(country_name, username):
    """
        Updates member country_name by the country_name provided where the key is username.
    """
    try:
        cur = conn.cursor()

        query = """
            WITH member_information (id)
            AS 
            (
                SELECT id FROM members WHERE username = %s
            )
            UPDATE member_details md
            SET country = %s
            FROM member_information
            WHERE md.member_id = member_information.id
        """

        cur.execute(query, (username,country_name))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def get_country_code_by_country_name(country_name):
    """
        Returns country code by country name.
    """
    try:
        cur = conn.cursor()

        query = """
            SELECT code FROM country_list
            WHERE name = %s
        """

        cur.execute(query, (country_name,))
        row = cur.fetchone()

        return row
    except Exception as e:
        log.critical(e)

def is_member_in_organization(username):
    """
        Checks is member in organization.
    """
    try:
        cur = conn.cursor()

        query = """
            SELECT organization_id FROM members
            WHERE username = %s
        """

        cur.execute(query, (username,))
        row = cur.fetchone()

        return row
    except Exception as e:
        log.critical(e)

def update_member_gender(gender, username):
    """
        Updates member gender by the gender provided where the key is username.
    """
    try:
        cur = conn.cursor()

        query = """
            WITH member_information (id)
            AS 
            (
                SELECT id FROM members WHERE username = %s
            )
            UPDATE member_details md
            SET gender = %s
            FROM member_information
            WHERE md.member_id = member_information.id
        """

        cur.execute(query, (username,gender))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def get_member_orders_details_all(username):
    """
        Return count and sum of all member orders
    """
    try:
        query = """
            WITH member_information (id)
            AS 
            (
                SELECT id FROM members WHERE username = %s
            )
            SELECT count(*), sum(o.price)
            FROM orders o
            INNER JOIN member_information mi ON mi.id = o.member_id 
        """

        cur = conn.cursor()
        cur.execute(query, (username,))
        
        row = cur.fetchone()

        cur.close()
        return row
    except Exception as e:
        log.critical(e)

def get_all_member_orders(username):
    """
        Return all member orders
    """
    try:
        query = """
            WITH member_information (id)
            AS
            (
                SELECT id FROM members WHERE username = %s
            )
            SELECT oc.category_name, o.price, o.product_title, o.product_image, os.status_name, o.product_short_description
            FROM orders o
            INNER JOIN member_information mi ON mi.id = o.member_id 
            INNER JOIN order_category oc ON o.order_category = oc.id
            INNER JOIN order_status os ON o.product_order_status = os.id 
        """

        cur = conn.cursor()
        cur.execute(query, (username,))
        
        rows = cur.fetchall()
        orders = []
        for row in rows:
           orders.append(
               {
                   "category_name": row[0],
                   "price": sjson.dumps(row[1], use_decimal=True),
                   "product_title": row[2],
                   "product_image": row[3],
                   "status_name": row[4],
                   "product_short_description": row[5]
               }
           ) 

        cur.close()
        return orders
    except Exception as e:
        log.critical(e)

def get_unread_notifications(username):
    """
        Return all member orders
    """
    try:
        query = """
            WITH member_information (id)
            AS
            (
                SELECT id FROM members WHERE username = %s
            )
            SELECT n.id, n.notification_title, n.notification_text, n.notification_image_url, n.created_at
            FROM notifications n
            INNER JOIN member_information mi ON mi.id = n.member_id 
            WHERE is_read = false
        """

        cur = conn.cursor()
        cur.execute(query, (username,))
        
        rows = cur.fetchall()
        notifications = []
        for row in rows:
           notifications.append(
               {
                   "id": row[0],
                   "notification_title": row[1],
                   "notification_text": row[2],
                   "notification_image_url": row[3],
                   "created_at": row[4]
               }
           ) 

        cur.close()
        return notifications
    except Exception as e:
        log.critical(e)

def update_read_notification(id):
    """
        Updates member first name by the first_name provided where the key is username.
    """
    try:
        cur = conn.cursor()

        query = """
            UPDATE notifications
            SET is_read = true
            WHERE id = %s
        """

        cur.execute(query, (id,))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def get_organization_orders(organization_id):
    """
        Return all orders that organization needs to deliver
    """
    try:
        query = """
            SELECT o.id, od.id, o.product_title, o.price, md.city, md.city_address, od.created_at, o.product_image, od.courier_id
            FROM orders o
            INNER JOIN organization_deliveries od ON o.id = od.order_id
            INNER JOIN member_details md ON o.member_id = md.member_id 
            WHERE od.organization_id = %s AND od.is_delivered = false
        """

        cur = conn.cursor()
        cur.execute(query, (organization_id,))
        
        rows = cur.fetchall()
        orders = []
        for row in rows:
           orders.append(
               {
                   "order_id": row[0],
                   "organization_delivery_id": row[1],
                   "product_title": row[2],
                   "price": row[3],
                   "city": row[4],
                   "city_address": row[5],
                   "created_at": row[6],
                   "product_image": row[7],
                   "courier_id": row[8]
               }
           ) 

        cur.close()
        return orders
    except Exception as e:
        log.critical(e)

def get_organization_deliveries(organization_id, username):
    """
        Return all deliveries assigned to member
    """
    try:
        query = """
            SELECT o.id, od.id, o.product_title, o.price, md.city, md.city_address, od.created_at, o.product_image, od.courier_id
            FROM orders o
            INNER JOIN organization_deliveries od ON o.id = od.order_id
            INNER JOIN member_details md ON o.member_id = md.member_id 
            WHERE od.organization_id = %s AND od.is_delivered = false AND od.courier_id = (SELECT id FROM members WHERE username = %s)
        """

        cur = conn.cursor()
        cur.execute(query, (organization_id, username))
        
        rows = cur.fetchall()
        deliveries = []
        for row in rows:
           deliveries.append(
               {
                   "order_id": row[0],
                   "organization_delivery_id": row[1],
                   "product_title": row[2],
                   "price": row[3],
                   "city": row[4],
                   "city_address": row[5],
                   "created_at": row[6],
                   "product_image": row[7],
                   "courier_id": row[8]
               }
           ) 

        cur.close()
        return deliveries
    except Exception as e:
        log.critical(e)

def take_order_delivery(username, order_id):
    """
        Updates courier delivery by given order id
    """
    try:
        cur = conn.cursor()

        query = """
            WITH member_information (id)
            AS 
            (
                SELECT id FROM members WHERE username = %s
            )
            UPDATE organization_deliveries od
            SET courier_id = member_information.id
            FROM member_information 
            WHERE od.order_id = %s
        """

        cur.execute(query, (username, order_id))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def leave_order_delivery(order_id):
    """
        Updates courier delivery by given order id to null
    """
    try:
        cur = conn.cursor()

        query = """
            UPDATE organization_deliveries od
            SET courier_id = null
            WHERE od.order_id = %s
        """

        cur.execute(query, (order_id,))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def update_security_key(security_key, member_id):
    """
        Updates security for the pelbox provided by the member id
    """
    try:
        cur = conn.cursor()

        query = """
            UPDATE rpi_devices
            SET user_security_key = %s 
            WHERE member_id = %s
        """

        cur.execute(query, (security_key, member_id))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def set_box_connected(security_key, member_id, status):
    """
        Set that box is connected
    """
    try:
        cur = conn.cursor()

        query = """
            UPDATE rpi_devices
            SET connected = %s
            WHERE security_key = %s AND member_id = %s
        """

        cur.execute(query, (status, security_key, member_id,))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def update_locking(member_id, state):
    """
        Update box locking
    """
    try:
        cur = conn.cursor()

        query = """
            UPDATE box_locking
            SET locked = %s
            WHERE member_id = %s
        """

        cur.execute(query, (state, member_id,))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def update_dismantle(member_id, state):
    """
        Update box dismantle
    """
    try:
        cur = conn.cursor()

        query = """
            UPDATE box_locking
            SET dismantle = %s
            WHERE member_id = %s
        """

        cur.execute(query, (state, member_id,))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)

def update_expanding_value(member_id, expanding_value):
    """
        Update box expanding_value
    """
    try:
        cur = conn.cursor()

        query = """
            UPDATE box_locking
            SET expanding_value = %s
            WHERE member_id = %s
        """

        cur.execute(query, (expanding_value, member_id,))
        conn.commit()

        cur.close()
    except Exception as e:
        log.critical(e)