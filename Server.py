"""
This is the server script for price tracker project the functionalities are:
1. get url data
2. add that url to favourites for tracking data either hourly or daily
3. Delete that url
4. Send notification if specified price conditions are met
5. View all data of urls sent for tracking
"""

import datetime as dt
import Database
import requests
import smtplib
import threading
import time
from bs4 import BeautifulSoup
from email.message import EmailMessage
from flask import request, jsonify, Flask


app = Flask(__name__)


# All Apis to add user,product view details and delete product
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
    adds them to user table of DB, a return message is sent to show status
    like already present or added
    """
    dictionary = request.form.to_dict()
    name, email, phonenumber = (
        dictionary["name"],
        dictionary["email"],
        dictionary["phonenumber"],
    )

    status = db1.add_user(name, email, phonenumber)
    print(status)

    return status


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
    price to be checked) as a parameter and adds them to products table
    returns status ndicating added, already present
    """
    dictionary = request.form.to_dict()
    email, interval, url, price = (
        dictionary["email"],
        dictionary["interval"],
        dictionary["url"],
        dictionary["price"],
    )

    url = modify_url(url)
    title, current_price = get_data(url)
    status = db1.add_url(email, title, url, interval, price)

    return status


@app.route("/api/v1/resources/delete", methods=["POST"])
def delete_url():
    """
    The function takes in a dictionary (email,interval of time to check, url)
    as a parameter and removes them from User class and global
    dictionaries depending on intervals
    """
    dictionary = request.form.to_dict()
    email, interval, url, price, title = (
        dictionary["email"],
        dictionary["interval"],
        dictionary["url"],
        dictionary["price"],
        dictionary["title"],
    )

    print("server", email, title, url, interval, price)
    status = db1.delete_product(email, title, url, interval, price)
    status = str(status)

    return status


@app.route("/api/v1/resources/track", methods=["GET"])
def track_urls():
    """
    The function takes in a string (email) as a parameter, gets all tables
    related to user in DB and
    returns data in json format
    """
    email = request.data.decode()
    dict = db1.user_tracker_details(email)
    return jsonify(dict)


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


# three threads hour day and notification cycle
def hour_cycle():
    """
    Gets details from products table that are marked for hour wise checking
    and checks the title and price of the product
    """
    while True:
        time.sleep(30)
        try:
            list_of_emailids, list_of_urls, list_of_prices = db1.get_url("0")
            if list_of_urls:
                for i in range(0, len(list_of_urls), 1):
                    save_data(
                        list_of_emailids[i], list_of_urls[i],
                        list_of_prices[i], "0"
                    )
        except:
            continue


def day_cycle():
    """
    Gets details from products table that are marked for day wise checking
    and checks the title and price of the product
    """
    while True:
        time.sleep(45)
        try:
            list_of_emailids, list_of_urls, list_of_prices = db1.get_url("1")
            if list_of_urls:
                for i in range(len(list_of_urls)):
                    save_data(
                        list_of_emailids[i], list_of_urls[i], list_of_prices[i], "1"
                    )
        except:
            continue


def notification_cycle():
    """
    Sends notifications periodically to the users
    """
    while True:
        time.sleep(15)
        try:
            (
                list_of_emails,
                list_of_titles,
                list_of_urls,
                list_of_prices,
                list_of_durations,
            ) = db1.get_notification_details()
            for i in range(len(list_of_emails)):
                data = [list_of_titles[i], list_of_urls[i], list_of_prices[i]]
                # print(list_of_emails[i])
                # print(data)
                # send_email(lists_of_emails[i], data)
        except:
            continue


# function to send mail
def send_email(receiever_mail, data):
    """
    The function sends mail to the user regarding fall of price
    """
    sender_email = "pricetracker207@gmail.com"
    sender_password = "Pricetracker@123"

    title = data[0]
    url = data[1]
    price = data[2]

    body = "Hello, we got news for you!! the price of the product:\n"
    body = body + f"{title} has fallen to specified price, {price}. "
    body = body + "Here is the link for the product\n"
    body = body + url

    msg = EmailMessage()
    msg["Subject"] = "Your product updates are here!"
    msg["From"] = sender_email
    msg["To"] = receiever_mail
    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
        print("\n\nsent\n\n")


# to add values to tracker table
def save_data(emaid_id, url, filter_price, interval):
    """
    1.This function saves data in the track table of database for price
    tracking.
    2. checks price with price margin given by user and adds the
    details needed for sending notification in notification table of db
    """
    title, price = get_data(url)
    time_stamp = dt.datetime.now()
    # print("executing save")

    status = db1.add_track(
        emaid_id, time_stamp, url, price, title, interval, filter_price
    )
    # print(status)

    price_margin = float(filter_price)
    price = float(price)
    if price_margin >= price:
        status = db1.add_notification(emaid_id, title, url, filter_price, interval)
        # print(status)
        # return status


# modify url to remove unwanted variables from url
def modify_url(url):
    """
    to get product ID for easy product tracking
    """
    BASE_URL = "https://www.amazon.in/dp/"

    positon1 = url.find("/B0")
    ascin = url[positon1 + 1 : positon1 + 11]
    url = BASE_URL + ascin
    # print(ascin)
    # print(url)
    return url


if __name__ == "__main__":
    """
    Initial entry point to program
    """
    print("\nMODIFIED\n")
    hour = threading.Thread(target=hour_cycle, daemon=True)
    day = threading.Thread(target=day_cycle, daemon=True)
    notification = threading.Thread(target=notification_cycle, daemon=True)

    hour.start()
    day.start()
    notification.start()
    app.run(debug=True, port=9876)
