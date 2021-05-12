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
    response = requests.get(URL + "/api/v1/search", data=url)
    print(response.text)

    interval = input("0 for 1 hour \n1 for 1 day\n")
    price = input("enter price margin:  ")
    email = dictionary["email"]
    data = {"email": email, "interval": interval, "price": price, "url": url}
    response = requests.post(URL + "/api/v1/resources/add_t0_fav", data=data)
    print(response.text)


def delete_button():
    response = requests.get(URL + "/api/v1/resources/track",
                            data=dictionary["email"])
    json_incoming_files = json.loads(response.text)

    while True:
        end = 0
        l = []
        for i,details in enumerate(json_incoming_files):
            print(f"{i} to delete {details}")
            end = i+1
            l.append(details)
        print("--100 to exit---:     ")
        choice = int(input("select choice: "))

        if choice >= end:
            continue
        elif choice == 100:
            break
        else:
            string = l[choice]
            title, url, interval, filter_price = string.split(",")
            print(title, url, interval, filter_price)
            email = dictionary["email"]
            
            data = {"email": email, "interval": interval, "url": url, "price": filter_price, "title" : title}
            response = requests.post(URL + "/api/v1/resources/delete", data=data)
            print(response.text)            
            
            break


def track_button():
    response = requests.get(URL + "/api/v1/resources/track",
                            data=dictionary["email"])
    json_incoming_files = json.loads(
        response.text
    )  
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
