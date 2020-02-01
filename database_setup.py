####### At begining of file #######

# Note: Any update on this database requires a change to a new database name
import os
import sys


from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Make an instance - Base from declarative_base
Base = declarative_base()


# Use Python classes to establish database tables
class Category(Base):
    """This class provides a means to store all categories in our database"""

    __tablename__ = 'category'

    # Mapping: connects rows of the category table to this class
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)



class Item(Base):
    """This class provides a means to store item information"""

    __tablename__ = 'item'

    # Mapping
    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    # picture = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)




####### Insert at end of file #######

# Make an instance - engine from create_engine. Point it to the database.
engine = create_engine ('sqlite:///catalog.db')
Base.metadata.create_all(engine)
