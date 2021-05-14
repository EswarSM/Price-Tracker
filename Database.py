import mysql.connector

# Main functions add user, add product, get details of product, delete a product
def add_user(name, email, phonenumber):
    """
    Takes in email, username, phonenumber and adds them to user table
    """
    mydb = mysql.connector.connect(
        host="localhost", user="root", password="krish2222na", database="krishdb"
    )
    mycursor = mydb.cursor()

    condition = check_user(email)

    if condition:
        return "Already present"

    else:
        add_command = "insert into user (name, email, phonenumber) values(%s, %s, %s);"
        data = (name, email, phonenumber)
        mycursor.execute(add_command, data)

        mydb.commit()

    mydb.close()
    return "added user data"


def add_url(email, title, url, duration, price):
    """
    Takes in email,title,url,duration and price margin and adds the to product table
    """
    mydb = mysql.connector.connect(
        host="localhost", user="root", password="krish2222na", database="krishdb"
    )
    mycursor = mydb.cursor()

    get_email_id = "select emailID from user where email = %s"
    data = (email, )
    mycursor.execute(get_email_id, data)
    tuple_of_email = mycursor.fetchone()

    email_id = tuple_of_email[0]
    # print(email_id)

    condition = check_product(email_id, url, duration, price)
    # print(condition)

    if condition:
        return "URL already added with these conditions"

    else:
        add_command = "insert into products (title, emailID, url, duration, price, notification) values(%s, %s, %s, %s, %s, '0');"
        data = (title, email_id, url, duration, price)
        mycursor.execute(add_command, data)

        mydb.commit()

    mydb.close()
    return "added product data"


def add_track(email_id, time_stamp, url, price, title, interval, filter_price):
    """
    Adds the price and product details to track tablse so that it can be abstracted and viewed
    """
    try:
        mydb = mysql.connector.connect(
            host="localhost", user="root", password="krish2222na", database="krishdb"
        )
        mycursor = mydb.cursor()

        # print(filter_price)
        product_id = get_product_id(email_id, url, filter_price, title, interval)
        # print("product id:  " , product_id)


        add_command = "insert into tracker (time, productID, price)  values(%s, %s, %s);"
        data = (time_stamp, product_id, price)

        mycursor.execute(add_command, data)

        mydb.commit()
        mydb.close()
        return "successfully added to tracker"

    except Exception as ex:
        return ex


def add_notification(email_id, title, url, filter_price, interval):
    """
    Adds details required for sending notifications to notification table
    """
    try:
        mydb = mysql.connector.connect(
            host="localhost", user="root", password="krish2222na", database="krishdb"
        )
        mycursor = mydb.cursor()

        # print("add_notification,      " ,email_id)

        product_id = get_product_id(email_id, url, filter_price, title, interval)
        # print("product_id=" ,product_id)

        update_command = "update products set notification = '1' where productID = %s"
        data = [product_id, ]

        mycursor.execute(update_command, data)
        mydb.commit()
        mydb.close()

        return "notification added"
    
    except Exception as ex:
        return ex


def user_tracker_details(email):
    """
    gets product racked details for a user
    """
    try:
        mydb = mysql.connector.connect(
            host="localhost", user="root", password="krish2222na", database="krishdb"
        )
        mycursor = mydb.cursor()

        product_id_command = "select productID, title, url, duration, price from products where emailID = (select emailID from user where email = %s)"
        data = (email, )
        mycursor.execute(product_id_command, data)
        list_of_id = mycursor.fetchall()

        list_of_emailids = []
        list_of_product_details = []
        for elements in list_of_id:
            list_of_emailids.append(elements[0])
            key = f"{elements[1]}, {elements[2]}, {elements[3]}, {elements[4]}"
            list_of_product_details.append(key)
        # print(list_of_emailids)
        # print(list_of_product_details)

        
        user_details_list = []
        for ids in list_of_emailids:
            tracker_detail_command = "select time,price from tracker where productID = %s"
            data = (ids,)
            mycursor.execute(tracker_detail_command, data)
            details = mycursor.fetchall()
            # print(details)
            # print("\n\n")

            dict = {}
            for elements in details:
                dict[elements[0]] = elements[1]
            # print(dict)
            # print("\n\n")
            user_details_list.append(dict)


        user_product_details = {}
        for position in range(len(list_of_product_details)):
            user_product_details[list_of_product_details[position]] = user_details_list[position]

        return user_product_details

    except Exception as ex:
        return ex

def delete_product(email, title, url, duration, filter_price):
    """
    Delete a specific product tracking
    """
    try:
        mydb = mysql.connector.connect(
                host="localhost", user="root", password="krish2222na", database="krishdb"
            )
        mycursor = mydb.cursor()

        emailid_command = "select emailID from user where email = %s"
        data = [email]
        mycursor.execute(emailid_command, data)
        tuple_emailid = mycursor.fetchone()
        email_id = tuple_emailid[0]
        # print("deleteeee,      " ,email_id)

        url = url[1::]
        filter_price = filter_price[1:]
        duration = duration[1:]
        # print(url, filter_price, title, duration)
        product_id = get_product_id(email_id, url, filter_price, title, duration)


        delete_command = "delete from products where productID = %s"
        data = (product_id, )

        mycursor.execute(delete_command, data)
        mydb.commit()


        delete_tracker_details_command = "delete from tracker where productID = %s"
        data = (product_id, )

        mycursor.execute(delete_tracker_details_command, data)
        mydb.commit()

        mydb.close()
        return "Deletion sucessful"

    except Exception as ex:
        return ex


# get function used to get data to populate table
def get_url(duration):
    """
    Gets details from product able for periodic checking of price
    """
    mydb = mysql.connector.connect(
        host="localhost", user="root", password="krish2222na", database="krishdb"
    )
    mycursor = mydb.cursor()

    get_url_command = "select emailID,url, price from products where duration = (%s)"
    data = (duration,)

    mycursor.execute(get_url_command, data)

    list_of_tuples = mycursor.fetchall()
    lists_of_emailids = []
    lists_of_urls = []
    lists_of_price = []

    for tuples in list_of_tuples:
        lists_of_emailids.append(tuples[0])
        lists_of_urls.append(tuples[1])
        lists_of_price.append(tuples[2])

    mydb.close()

    if len(lists_of_emailids) >= 1:
        return (lists_of_emailids, lists_of_urls, lists_of_price)
    else:
        return None


def get_notification_details():
    """
    function returns the data to send notification to user
    """
    mydb = mysql.connector.connect(
        host="localhost", user="root", password="krish2222na", database="krishdb"
    )
    mycursor = mydb.cursor()

    get_url_command = "select * from products where notification = '1'"

    mycursor.execute(get_url_command)

    list_of_tuples = mycursor.fetchall()
    list_of_emailids = []
    list_of_titles = []
    list_of_urls = []
    list_of_prices = []
    list_of_durations = []

    for tuples in list_of_tuples:
        list_of_emailids.append(tuples[2])
        list_of_titles.append(tuples[1])
        list_of_urls.append(tuples[3])
        list_of_prices.append(tuples[5])
        list_of_durations.append(tuples[4])


    list_of_emails = []

    for ids in list_of_emailids:
        get_email_command = "select email from user where emailID = %s"
        data = [ids]
        mycursor.execute(get_email_command, data)
        tuple_of_email = mycursor.fetchone()
        list_of_emails.append(tuple_of_email[0])

    mydb.close()

    if len(list_of_emails) >= 1:
        return (
            list_of_emails,
            list_of_titles,
            list_of_urls,
            list_of_prices,
            list_of_durations,
        )
    else:
        return None


def get_product_id(email_id, url, price, title, interval):
    """
    gives the product ID
    """
    mydb = mysql.connector.connect(
        host="localhost", user="root", password="krish2222na", database="krishdb"
    )
    mycursor = mydb.cursor()

    #print(email_id, url, price, title, interval,"\n\n")

    product_id_command = "select productID from products where (emailID = %s and url = %s and price = %s and title = %s and duration = %s)"
    data = (email_id, url, price, title, interval)

    mycursor.execute(product_id_command, data)
    tuple_of_productID = mycursor.fetchone()

    product_id = tuple_of_productID[0]
    # print(product_id)

    mydb.close()

    return product_id

# checking for duplicate values used by add function to not add duplicate values
def check_user(email):
    """
    checks for duplicate values in user table
    """
    mydb = mysql.connector.connect(
        host="localhost", user="root", password="krish2222na", database="krishdb"
    )
    mycursor = mydb.cursor()

    command = "select * from user where (email = %s)"
    data = (email,)

    mycursor.execute(command, data)

    condition = mycursor.fetchall()

    mydb.close()

    if condition:
        return True

    else:
        return False


def check_product(email_id, url, duration, price):
    """
    checks for duplicate values in products table
    """
    mydb = mysql.connector.connect(
        host="localhost", user="root", password="krish2222na", database="krishdb"
    )
    mycursor = mydb.cursor()


    command = "select * from products where  (emailID = %s and url = %s and duration = %s and price = %s)"
    data = (email_id, url, duration, price)


    mycursor.execute(command, data)


    condition = mycursor.fetchall()

    mydb.close()

    if condition:
        return True

    else:
        return False
