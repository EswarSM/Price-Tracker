"""
This is the Database script for price tracker project.
The functionalities are:
1. add_user_data
2. get_user_id
3. get_product_id
4. add_product_data
5. add_track_list_data
6. show_all_track_data
7. get_track_data
8. delete_product_data
9. delete_track_data
"""


############ Imports ################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from application import app
############## App Configuration ###############

# app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///price_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

############ DB designing ####################
db = SQLAlchemy(app)


class User(db.Model):
    """ 
    This Class is the User Table.
    It has 4 columns
    1. id - primary key
    2. name
    3. email
    4. phone
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    phone = db.Column(db.Integer)


class Product(db.Model):
    """ 
    This Class is the Product Table.
    It has 6 columns
    1. id - primary key
    2. user_id - foreign key
    3. title
    4. duration
    5. link
    6. expected_price
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    link = db.Column(db.String(50))
    expected_price = db.Column(db.Float(50))


class Track_list(db.Model):
    """ 
    This Class is the Product Table.
    It has 4 columns
    1. id - primary key
    2. product_id - foreign key
    3. time
    4. price

    """
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    time = db.Column(db.String(50))
    price = db.Column(db.Float)


def add_user_data(name, email, phone):

    ############ Login - User verification ####################
    user_check = db.session.query(User).filter(User.email == email).first()
    # checks whether the User details already exists

    ############ Login - User addition ####################
    if(user_check):
        return('Exists')
    else:
        user = User(name=name, email=email,
                    phone=phone)
        db.session.add(user)
        db.session.commit()
        return('Created')


def get_user_id(email):
    # the the user_id for the corresponding email
    user_id = db.session.query(User.id).filter(User.email == email).first()
    return(user_id[0])


def get_product_id(email, duration, link):
    # the the product_id for the corresponding email

    user_id = get_user_id(email)
    product_id = db.session.query(Product.id).filter(
        Product.user_id == user_id, Product.duration == duration, Product.link == link).first()
    return(product_id[0])


def add_product_data(email, title, duration, link, expected_price):

    ############ add to fav - Product verification ####################
    user_id = get_user_id(email)

    # checks whether the Product details already exists

    product_check = db.session.query(Product).filter(
        Product.user_id == user_id, Product.duration == duration, Product.link == link, Product.title == title, Product.expected_price == expected_price).first()

    ############ add to fav - Product  addition ####################

    # Product  addition
    if(product_check):
        return('Exists')
    else:
        product = Product(user_id=user_id, title=title,
                          duration=duration, link=link, expected_price=expected_price)
        db.session.add(product)
        db.session.commit()
        return('Created')


def add_track_list_data(email, duration, link, price):
    # Track  addition

    product_id = get_product_id(email, duration, link)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    track = Track_list(product_id=product_id, time=str(now),
                       price=price)
    db.session.add(track)
    db.session.commit()
    return('Track data added')


def show_all_track_data(email):
    # returns the track data of all products of a particular User
    products = db.session.query(Product).join(User). \
        filter(User.email == email).all()
    all_track_list = []
    for product in products:
        time_price = get_track_data(product.id)
        track_dict = {(product.link, product.duration,
                       product.title): time_price}
        all_track_list.append(track_dict)

    return(all_track_list)


def get_track_data(product_id):

    ############ Track - Track retrieve ####################

    # returns the track data of particular Product

    time_price_dict = dict()
    track_datas = db.session.query(Track_list.time, Track_list.price).filter(
        Track_list.product_id == product_id).all()
    time_list, price_list = [], []
    for time, price in track_datas:
        time_price_dict[time] = price

    return time_price_dict
# -----------------------

############ Delete - Product delete, Track delete ####################


def delete_product_data(email, duration, link):
    # Product delete

    # deletes all the details of a particular product

    user_id = get_user_id(email)
    product_data = db.session.query(Product).filter(
        Product.user_id == user_id, Product.duration == duration, Product.link == link).first()
    print(delete_track_data(email, duration, link))
    db.session.delete(product_data)
    db.session.commit()
    return('Product deleted')


def delete_track_data(email, duration, link):
    #  Track delete

    # deletes all the Track data of a particular product

    product_id = get_product_id(email, duration, link)
    track_datas = db.session.query(Track_list).filter(
        Track_list.product_id == product_id).all()
    for track_data in track_datas:
        db.session.delete(track_data)
        db.session.commit()
    return('Track data deleted')


if __name__ == '__main__':
    ############ DB creation ####################

    db.create_all()
