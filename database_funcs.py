import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

engine = create_engine(os.environ["DATABASE_URL"])
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Database helper functions

def is_owner_item(user_id, item_id=-1):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    return item.user_id == user_id


def is_owner_category(user_id, category_id=-1):
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    if category is None or user_id is None:
        return False
    else:
        return category.user_id == user_id


def item_exists(item_id=-1):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    if item is None:
        return False
    else:
        return True


def category_exists(category_id=-1):
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    if category is None:
        return False
    else:
        return True


def category_list():
    categories = session.query(Category).all()
    return [(category.name, str(category.id)) for category in categories]


def getUserID(email):
    return session.query(User.id).filter_by(email=email).scalar()


def get_name(id):
    return session.query(User.name).filter_by(id=id).scalar()


def createUser(login_session):
    new_user = User(name=login_session['username'],
                    email=login_session['email'])
    session.add(new_user)
    session.commit()
    return new_user.id


def updateUser(login_session):
    email = login_session['email']
    user = session.query(User).filter_by(email=email).one_or_none()

    if user is not None:
        user.email = login_session['email']
        user.name = login_session['username']
    session.commit()
