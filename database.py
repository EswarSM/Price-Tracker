############ Imports ################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

############## App Configuration ###############

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///price_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

############ DB designing ####################


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    phone = db.Column(db.Integer(50))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    link = db.Column(db.String(50))
    expected_price = db.Column(db.Float(50))


class Track_list(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    time = db.Column(db.DateTime(timezone=True))
    price = db.Column(db.Float)


def add_user_data(name, email, phone):

    ############ Login - User verification ####################
    user_check = db.session.query(User).filter(User.email == email)

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
    return(db.session.query(User.id).filter(User.email == email).first())


def get_product_id(email, duration, link):
    user_id = get_user_id(email)
    return(db.session.query(Product.id).filter(
        Product.user_id == user_id, Product.duration == duration, Product.link == link).first())


def add_product_data(email, title, duration, link, expected_price):

    ############ add to fav - Product verification ####################
    user_id = get_user_id(email)

    product_check = db.session.query(Product).filter(
        Product.user_id == user_id, Product.duration == duration, Product.link == link, Product.title=title, Product.expected_price=expected_price)

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


def delete_product_data(email, duration, link):
    # Product delete
    user_id = get_user_id(email)
    product_data = db.session.query.(Product).filter(
        Product.user_id == user_id, Product.duration == duration, Product.link == link).first()
    db.session.delete(product_data)
    db.session.commit()
    return('Product deleted')


def add_track_list_data(email, duration, link, price):
    # Track  addition

    product_id = get_product_id(email, duration, link)

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    track = Track_list(product_id=product_id, time=now,
                       price=price)
    db.session.add(track)
    db.session.commit()
    return('Track data added')


def delete_track_data(email, duration, link):
    #  Track delete
    product_id = get_product_id(email, duration, link)
    track_data = db.session.query.(Track_list).filter(Track_list.product_id == product_id).all()
    db.session.delete(track_data)
    db.session.commit()
    return('Track data deleted')


def show_all_track_data(email):
    products = db.session.query(Product).join(User). \
        filter(User.email == email).all()
    all_track_list=[]
    for product in products:
        time_price = get_track_data(product.id)
        track_dict = {(product.link,product.duration):{product.title:time_price}}
        all_track_list.append(track_dict)
    return(all_track_list)


def get_track_data(product_id):

    ############ Track - Track retrieve ####################
    track_datas = db.session.query(Track_list.time, Track_list.price).filter(
        Track_list.product_id == product_id).all()
    time_list, price_list = [], []
    for time, price in track_datas:
        time_list.append(time)
        price_list.append(price)
    return dict(tuple(time_list): tuple(price_list))
# -----------------------

############ Delete - Product delete, Track delete ####################


if __name__ == '__main__':
    ############ DB creation ####################

    db.create_all()
