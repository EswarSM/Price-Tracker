"""
This is the server script for price tracker project the functionalities are:
1. get url data
2. add that url to favourites for tracking data either hourly or daily
3. Delete that url
4. Send notification if specified price conditions are met
5. View all data of urls sent for tracking
"""
# price = filter_price = price thresholds i.e th prices will be compared with
# these prices


import os
import requests
import smtplib
import json
import threading
import time
from bs4 import BeautifulSoup
from email.message import EmailMessage
from flask import request, jsonify, Flask
####################################
import database
from application import app
####################################

# app = Flask(__name__)


user_objects = []
# for tracking all the objects of Users class
one_hour_cycle_dict = {}
# keys: email of user, values: list of urls for specified user hourly basis
one_day_cycle_dict = {}
# keys: email of user, values: list of urls for specified user daily basis
one_hour_price_cycle_dict = {}
# keys: email of user, values: list of prices for specified user hourly basis
one_day_price_cycle_dict = {}
# keys: email of user, values: list of prices for specified user daily basis
notification_email_dict = {}
# keys: email of user, values: list of lists that contains
# details to sent with the email


class Users:
    """
    The class is created to keep track of the urls and price margins so
    that we can select specific urls
    """

    def __init__(self, name, email, phonenumber):
        """
        The constructor creates basic data of a user
        the dictionaries urls and prices are used for tracking
        """
        self.name = name
        self.email = email
        self.phonenumber = phonenumber
        self.urls = {}
        self.prices = {}

    def add_url(self, url, interval, price):
        """
        THis function adds urls and price thresholds for a specific user
        """
        flag = 0
        for key in self.urls.keys():
            if key == interval:
                self.urls.get(interval).append(url)
                self.prices.get(interval).append(price)
                flag = 1

        if flag == 0:
            self.urls[interval] = [url]
            self.prices[interval] = [price]

        if interval == "0":
            add_one_hour_dict(url, self.email, price)
            store_data(self.email, url, '1H', price)

        else:
            add_one_day_dict(url, self.email, price)
            store_data(self.email, url, '1D', price)

    def delete_url(self, url, interval):
        """
        This function is used to remove urls from cycle of checking prices
        and is devided into 3 sections
        """

        # This part of code removes url from self.urls and prices self.prices
        list_from_dict = self.urls.get(interval)
        index = list_from_dict.index(url)
        del self.urls.get(interval)[index]
        filter_price = self.prices.get(interval)[index]
        filter_price = float(filter_price)
        del self.prices.get(interval)[index]

        # The intervals are converted to '1H' for hour cycle and '1D' for 1
        # day because datas are stored in tables with syntax:
        # email_interval_title[0:6]
        title, price = get_data(url)
        if interval == "0":
            interval = "1H"
        else:
            interval = "1D"

        # This part of code is used to remove notifications
        # from notification dictionary
        for emails in list(notification_email_dict):
            if emails == self.email:
                for data in notification_email_dict.get(self.email):
                    print(data, "\n")
                    if (
                        data[0] == title
                        and data[1] == url
                        and data[2] == filter_price
                        and data[3] == interval
                    ):
                        list_of_lists_from_dict = notification_email_dict.get(
                            self.email
                        )
                        index = list_of_lists_from_dict.index(data)
                        del notification_email_dict.get(self.email)[index]
                        break

        # This part of code removes the url from one_hour_cycle_dict or
        # one_day_cycle_dict
        if interval == "1H":
            print("              DELETED                   ")
            list_from_dict = one_hour_cycle_dict.get(self.email)
            index = list_from_dict.index(url)
            del one_hour_cycle_dict.get(self.email)[index]
            del one_hour_price_cycle_dict.get(self.email)[index]

        else:
            list_from_dict = one_day_cycle_dict.get(self.email)
            index = list_from_dict.index(url)
            del one_day_cycle_dict.get(self.email)[index]
            del one_day_price_cycle_dict.get(self.email)[index]

        #################################################################
        # deleteion of data from DB
        f = f"{self.email}_{interval}_{title[0:6]}"
        os.remove(f)

        database.delete_product_data(email, interval, url)
        print('Product and Track datas deleted in DB')

        """
        Here I have created the name so delete it from the DB
        
        # # delete product and track data of a product

        
        database.delete_product_data(email, interval, url)
        print('Product and Track datas deleted')
        
        """
        ###################################################################


@app.route("/")
def fun():
    """
    HOME PAGE just gives a string
    """
    return "SERVER!!!!!!!!!!!!!!!"


@app.route("/api/v1/resources/login", methods=["POST"])
def add_user():
    """
    The function takes in a dictionary (user credentials) as a parameter and
    adds them to DB a return message is sent to show status
    """
    dictionary = request.form.to_dict()
    name, email, phonenumber = (
        dictionary["name"],
        dictionary["email"],
        dictionary["phonenumber"],
    )
    Email = email
    email = Users(name, email, phonenumber)
    user_objects.append(email)
    print('before user-------------')
    print(name, email, phonenumber)
    add_user = database.add_user_data(name, Email, phonenumber)
    print(add_user, 'in DB')
    ####################################################################
    """
    SAI add the user credentials to DB
    
    # # adding user data
    
    add_user = database.add_user_data(name, email, phonenumber)
    return add_user
    
    """
    #####################################################################

    return "User added"


@app.route("/api/v1/search", methods=["GET"])
def send_url_details():
    """
    The function takes in a string (url) as a parameter, gets title and price
    of url and returns dictionary of title and price as keys
    """
    url = request.data.decode()
    url = modify_url(url)
    title, price = get_data(url)
    dictionary = {"Title": title, "Price": price}
    return dictionary


@app.route("/api/v1/resources/add_t0_fav", methods=["POST"])
def add_to_fav():
    """
    The function takes in a dictionary (email,interval of time to check, url,
    price to be checked) as a parameter and adds them to User class and
    global dictionaries depending on intervals to be used in threads
    """
    dictionary = request.form.to_dict()
    email, interval, url, price = (
        dictionary["email"],
        dictionary["interval"],
        dictionary["url"],
        dictionary["price"],
    )
    class_obj = None

    for user in user_objects:
        if email == user.email:
            class_obj = user
            break

    url = modify_url(url)
    title, price2 = get_data(url)

    add_product = database.add_product_data(email,
                                            title, interval, url, price)
    print(add_product, 'in DB')

    class_obj.add_url(url, interval, price)

    ####################################################################
    """
    SAI add the user credentials to DB
    
    # # adding product data
    
    add_product = database.add_product_data(email,
#       title, interval, url, price)
    return add_product
    
    """
    #####################################################################
    return "Added"


@app.route("/api/v1/resources/delete", methods=["POST"])
def delete_url():
    """
    The function takes in a dictionary (email,interval of time to check, url)
    as a parameter and removes them from User class and global
    dictionaries depending on intervals
    """
    dictionary = request.form.to_dict()
    email, interval, url = (
        dictionary["email"],
        dictionary["interval"],
        dictionary["url"],
    )

    class_obj = None

    for user in user_objects:
        if email == user.email:
            class_obj = user
            break

    class_obj.delete_url(url, interval)

    return "Deleted"


@app.route("/api/v1/resources/track", methods=["GET"])
def track_urls():
    """
    The function takes in a string (email) as a parameter, gets all tables
    related to user in DB and
    returns data in json format
    """
    email = request.data.decode()
    print(email)
    data = [
        {
            "Anganandheswaran": 12.25,
            "Nanda Kumar S": 15.25,
            "Ram Kumar": 4.5,
            "Vignesh Shankar": 133.25,
            "suhail.ahamed": 2.7,
        },
        {
            "Anganandheswaran": 12.25,
            "Nanda Kumar S": 15.25,
            "Ram Kumar": 4.5,
            "Vignesh Shankar": 133.25,
            "suhail.ahamed": 2.7,
        },
        {
            "Anganandheswaran": 12.25,
            "Nanda Kumar S": 15.25,
            "Ram Kumar": 4.5,
            "Vignesh Shankar": 133.25,
            "suhail.ahamed": 2.7,
        },
        {
            "Anganandheswaran": 12.25,
            "Nanda Kumar S": 15.25,
            "Ram Kumar": 4.5,
            "Vignesh Shankar": 133.25,
            "suhail.ahamed": 2.7,
        },
    ]

    data = database.show_all_track_data(email)
    print('In DB')
    print(data)
    return json.dumps(str(data))
    # return jsonify(data)
    ##########################################################################
    """
    SAI GET ALL RELEVANT TABLE AND SEND IT AS A JSON GET TABLE
    DATA AS A DICTIONARY CREATE A LIST OF DICTIONARY USE JSONIY
    SO THAT IT IS CONVERTED TO JSON AND SEND
    
    # # get all track data of a User
    
    data = database.show_all_track_data(email)
    return data
    
    """

    ##########################################################################


def get_data(url):
    """
    function takes in url and webscrpas ttle and price and returns
    them as strings
    """
    key = "User-Agent"
    value1 = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    value2 = "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    value = value1 + value2
    headers = {key: value}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    if soup.find(id="productTitle"):
        title = soup.find(id="productTitle").get_text()
        title = title.strip()

    else:
        title = soup.find(id="title").get_text()
        title = title.strip()

    if soup.find(id="priceblock_dealprice"):
        price = soup.find(id="priceblock_dealprice").get_text()
        price.strip()
        price = price[2:]
        price = price.replace(",", "")
        price = float(price)

    elif soup.find(id="priceblock_saleprice"):
        price = soup.find(id="priceblock_saleprice").get_text()
        price.strip()
        price = price[2:]
        price = price.replace(",", "")
        price = float(price)

    else:
        price = soup.find(id="priceblock_ourprice").get_text()
        price.strip()
        price = price[2:]
        price = price.replace(",", "")
        price = float(price)

    return title, price


def add_one_hour_dict(url, email, price):
    """
    function takes in url, email and price and adds them to one_hour_cycle_dict
    """
    global one_hour_cycle_dict
    if one_hour_cycle_dict:
        for key in one_hour_cycle_dict.keys():
            if key == email:
                one_hour_cycle_dict.get(email).append(url)
                one_hour_price_cycle_dict.get(email).append(price)
                return
        one_hour_cycle_dict[email] = [url]
        one_hour_price_cycle_dict[email] = [price]
    else:
        one_hour_cycle_dict[email] = [url]
        one_hour_price_cycle_dict[email] = [price]


def add_one_day_dict(url, email, price):
    """
    function takes in url, email and price thresholds and adds them to
    one_day_cycle_dict
    """
    global one_day_cycle_dict
    if one_day_cycle_dict:
        for key in one_day_cycle_dict.keys():
            if key == email:
                one_day_cycle_dict.get(email).append(url)
                one_day_price_cycle_dict.get(email).append(price)
                return
        one_day_cycle_dict[email] = [url]
        one_day_price_cycle_dict[email] = [price]
    else:
        one_day_cycle_dict[email] = [url]
        one_day_price_cycle_dict[email] = [price]


def add_notification_dict(title, email, url, filter_price, interval):
    """
    function takes in url, email, price and interval and adds them to
    notification_email_dict
    """
    details = [title, url, filter_price, interval]
    global notification_email_dict

    if notification_email_dict:
        for key in notification_email_dict.keys():
            if key == email:
                all_lists = notification_email_dict.get(email)
                for lists in all_lists:
                    if (
                        lists[0] == title
                        and lists[1] == url
                        and lists[2] == filter_price
                        and lists[3] == interval
                    ):
                        # print("already in notifications")
                        return
                notification_email_dict.get(email).append(details)
                return
        notification_email_dict[email] = [details]
    else:
        notification_email_dict[email] = [details]


def hour_cycle():
    """
    This threads runs continuosly to check price and comapre them with filter
    price and send notification if price drops cycle = 1 hour
    """
    while True:
        if one_hour_cycle_dict:
            for key in list(one_hour_cycle_dict):
                for value in range(len(one_hour_cycle_dict[key])):
                    url = one_hour_cycle_dict.get(key)[value]
                    filter_price = one_hour_price_cycle_dict.get(key)[value]
                    # url = one_hour_cycle_dict[key][value]
                    # print(url)
                    # print(filter_price)

                    store_data(key, url, "1H", filter_price)
        time.sleep(20)  # for testing


def day_cycle():
    """
    This threads runs continuosly to check price and comapre them with filter
    price and send notification if price drops cycle = 1 day
    """
    while True:
        if one_day_cycle_dict:
            for key in list(one_day_cycle_dict):
                for value in range(len(one_day_cycle_dict[key])):
                    url = one_day_cycle_dict.get(key)[value]
                    filter_price = one_day_price_cycle_dict.get(key)[value]
                    # url = one_day_cycle_dict[key][value]

                    store_data(key, url, "1D", filter_price)
        time.sleep(20)  # for testing


def notification_cycle():
    """
    Sends notifications periodically to the users
    """
    while True:
        if notification_email_dict:
            for key in list(notification_email_dict):
                print(key)
                for value in notification_email_dict[key]:
                    print(value[0])
                    print(value[3])
                    print(value[2])
                    print(value[1])
                    send_email(key, value)
                    print("\n\n")

        time.sleep(60)


def send_email(receiever_mail, data):
    """
    The function sends mail to the user regarding fall of price
    """
    sender_email = 'pricetracker207@gmail.com'
    sender_password = 'Pricetracker@123'

    title = data[0]
    url = data[1]
    price = data[2]

    body = "Hello, we got news for you!! the price of the product:\n"
    body = body + f"{title} has fallen to specified price, {price}. "
    body = body + "Here is the link for the product\n"
    body = body + url

    msg = EmailMessage()
    msg['Subject'] = "Your product updates are here!"
    msg['From'] = sender_email
    msg['To'] = receiever_mail
    msg.set_content(body)

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
        print("\n\nsent\n\n")


def store_data(email, url, interval, filter_price):
    title, price = get_data(url)
    f = f"{email}_{interval}_{title[0:6]}"
    print(email, url)
    if(interval == '1H'):
        inter = '0'
    else:
        inter = '1'
    database.add_track_list_data(email, inter, url, price)
    print('added Track list in DB')

    #########################################################################
    with open(f, mode="a") as writter:
        writter.write(str(price) + "\n")

    """
    SAI I have created the table name creae table wih this name in db
    
    # # adding track list data
    
    database.add_track_list_data(email, interval, url, price)
    
    
    """
    #########################################################################
    price = float(price)
    filter_price = float(filter_price)

    if filter_price >= price:
        add_notification_dict(title, email, url, filter_price, interval)


def modify_url(url):
    """
    to get product ID for easy product tracking
    """
    BASE_URL = "https://www.amazon.in/dp/"

    positon1 = url.find('/B0')
    ascin = url[positon1 + 1: positon1 + 11]
    url = BASE_URL + ascin
    # print(ascin)
    # print(url)
    return url


if __name__ == "__main__":
    """
    Initial entry point to program
    """
    print("\nMODIFIED\n")

    database.db.create_all()

    hour = threading.Thread(target=hour_cycle, daemon=True)
    day = threading.Thread(target=day_cycle, daemon=True)
    notification = threading.Thread(target=notification_cycle, daemon=True)

    hour.start()
    day.start()
    notification.start()
    app.run(debug=True, port=9876)
