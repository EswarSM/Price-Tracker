############ Imports ################

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

############## App Configuration ###############

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
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


############ DB creation ####################

if __name__ == '__main__':
    db.create_all()

############ Login - User verification ####################
user_check = db.session.query(User).filter(User.email == email)
# .first()
# .all()

############ Login - User addition ####################
if(not user_check):
    user = User(name=name, email=email,
                phone=phone)
    db.session.add(user)
    db.session.commit()

############ add to fav - Product verification ####################
product_check = db.session.query(Product).filter(
    Product.user_id == user_id, Product.duration == duration, Product.link == link)

############ add to fav - Product  addition, Track addition ####################

# Product  addition
if(not product_check):
    product = Product(user_id=user_id, title=title,
                      duration=duration, link=link, expected_price=expected_price)
    db.session.add(product)
    db.session.commit()

# Track  addition
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
track = Track_list(product_id=product_id, time=now,
                   price=price)
db.session.add(track)
db.session.commit()

############ Track - Track retrieve ####################
track_datas = db.session.query(Track_list).filter(
    Track_list.product_id == product_id).all()

############ Delete - Product delete, Track delete ####################

# Product delete
product_data = db.session.query.(Product).filter(Product.user_id == user_id, Product.duration == duration, Product.link == link).all()
db.session.delete(product_data)
db.session.commit()

#  Track delete
track_data = db.session.query.(Track_list).filter(Track_list.product_id == product_id).all()
db.session.delete(track_data)
db.session.commit()

# Loop - Track addition
