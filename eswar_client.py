import json
import requests

URL = "http://127.0.0.1:9876"

name = input("name: ")
email = input("email: ")
phonenumber = input("phonenumber: ")

dictionary = dict()
dictionary["name"] = name
dictionary["email"] = email
dictionary["phonenumber"] = phonenumber


def send_login():
    response = requests.post(URL + "/api/v1/resources/login", data=dictionary)
    print(response.text)


def search_button():
    url = input("enter url to be searched:  ")
    response = requests.get(URL + "/api/v1/search", data=url)
    print(response.text)


def add_to_fav():
    url = input("enter url to be added:  ")
    response = requests.get(URL + "/api/v1/search", data=url)  # **
    print(response.text)  # **

    interval = input("0 for 1 hour \n1 for 1 day\n")
    price = input("enter price margin:  ")
    email = dictionary["email"]
    data = {"email": email, "interval": interval, "price": price, "url": url}
    response = requests.post(URL + "/api/v1/resources/add_t0_fav", data=data)
    print(response.text)


def delete_button():
    url = input("enter url to be added:  ")
    interval = input("0 for 1 hour \n1 for 1 day\n")
    email = dictionary["email"]
    data = {"email": email, "interval": interval, "url": url}

    response = requests.post(URL + "/api/v1/resources/delete", data=data)
    print(response.text)


def track_button():
    response = requests.get(URL + "/api/v1/resources/track",
                            data=dictionary["email"])
    json_incoming_files = json.loads(
        response.text
    )  # this gives a dictionary of dictionaries
    print(json_incoming_files)
    """
    HENCE you will get all needed data to be displayed as chart or tables
    """


if __name__ == "__main__":
    send_login()
    # search_button()
    while True:
        choice = input(
            "1 for search\n2 for add\n3 for delete\n4 for track\n0 to exit\n"
        )
        if choice == "1":
            search_button()
        elif choice == "2":
            add_to_fav()
        elif choice == "3":
            delete_button()
        elif choice == "4":
            track_button()
        elif choice == "0":
            break
        else:
            continue
