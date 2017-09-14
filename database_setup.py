from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)


class Category(Base):
    __tablename__ = 'category'

    name = Column(String(), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
        }


class Item(Base):
    __tablename__ = 'item'

    name = Column(String(), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String())
    date_created = Column(DateTime(timezone=True), server_default=func.now()) # doesn't work properly
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'cat_id': self.category_id,
            'date_created': self.date_created,
            'user_id': self.user_id,
        }


# This should go at the end of the file

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
