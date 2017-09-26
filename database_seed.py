# This was originally lotsofmenus.py from the course


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User


engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


def create_user(name, email):
    new_user = User(name=name, email=email)
    session.add(new_user)
    session.commit()
    return new_user.id


def get_userID(email):
    return session.query(User.id).filter_by(email=email).scalar()


# Users


create_user('Muhammad Ali', 'muhammad@boom.com')
create_user('Tom Dwan', 'tom.dwan@pwned.com')

# Categories

cat1 = Category(name="Poker", user_id=get_userID('tom.dwan@pwned.com'))

session.add(cat1)
session.commit()

item2 = Item(name="Playing cards",
             description="Standard 52 plastic cards deck",
             category=cat1,
             user_id=get_userID('tom.dwan@pwned.com'))

session.add(item2)
session.commit()


item1 = Item(name="Chips set",
             description="Plastic chips in a suitcase.",
             category=cat1,
             user_id=get_userID('tom.dwan@pwned.com'))

session.add(item1)
session.commit()

item2 = Item(name="Poker Tracker",
             description="Tracking software for online poker",
             category=cat1,
             user_id=get_userID('tom.dwan@pwned.com'))

session.add(item2)
session.commit()

item3 = Item(name="Super System",
             description="Doyle Brunson's classic book",
             category=cat1,
             user_id=get_userID('tom.dwan@pwned.com'))

session.add(item3)
session.commit()


# Menu for Climbing
cat2 = Category(name="Climbing", user_id=get_userID('muhammad@boom.com'))

session.add(cat2)
session.commit()


item1 = Item(name="Rope",
             description="80m Mamut 7.8mm rope",
             category=cat2,
             user_id=get_userID('muhammad@boom.com'))

session.add(item1)
session.commit()

item2 = Item(name="Harness",
             description="Sport climbing, lightweight Petzl harness",
             category=cat2,
             user_id=get_userID('muhammad@boom.com'))

session.add(item2)
session.commit()

item3 = Item(name="Set of quickdraws",
             description="12 quickdraws",
             category=cat2,
             user_id=get_userID('muhammad@boom.com'))

session.add(item3)
session.commit()

item4 = Item(name="Climbing shoes",
             description="Pair of comfy 5/10. :)",
             category=cat2,
             user_id=get_userID('muhammad@boom.com'))

session.add(item4)
session.commit()

item5 = Item(name="Chalk bag",
             description="Compact bag for chalk",
             category=cat2,
             user_id=get_userID('muhammad@boom.com'))

session.add(item5)
session.commit()

item6 = Item(name="Climbing shorts",
             description="Light, durable pair of shorts",
             category=cat2,
             user_id=get_userID('muhammad@boom.com'))

session.add(item6)
session.commit()


# Boxing
cat1 = Category(name="Boxing", user_id=get_userID('muhammad@boom.com'))

session.add(cat1)
session.commit()


item1 = Item(name="Gloves",
             description="16oz training gloves",
             category=cat1,
             user_id=get_userID('muhammad@boom.com'))

session.add(item1)
session.commit()

item2 = Item(name="Bandages",
             description="Cotton, 4m long wrap bandages.",
             category=cat1,
             user_id=get_userID('muhammad@boom.com'))

session.add(item2)
session.commit()

item3 = Item(name="Boxing shoes",
             description="Light, easy to pivot pair of shoes",
             category=cat1,
             user_id=get_userID('muhammad@boom.com'))

session.add(item3)
session.commit()

item4 = Item(name="Skipping rope",
             description="Speed rope for fast jumping.",
             category=cat1,
             user_id=get_userID('muhammad@boom.com'))

session.add(item4)
session.commit()

print("added items!")
