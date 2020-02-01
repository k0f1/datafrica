from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

# Add database imports here
from sqlalchemy import create_engine, asc, desc, literal, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
# from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

# Make an instance of create engine
engine = create_engine('sqlite:///catalog.db')
# engine = create_engine ('sqlite:///catalogupdate.db')

# Bind the engine to the metadata of the Base class
# To establish conversation with the database and act as staging zone
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

# Create DB session instance
session = DBSession()

# Add other imports here


# Show all Categories and latest Item-list associated with them
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    # Add SQLAlchemy statements
    """Show the homepage displaying the categories and latest items.
        Returns:
        A web page with the 20 latest items that have added.
    """

    categories = session.query(Category).all()
    # result[::-1] return the slice of every elelement of result in reverse
    latestItems = session.query(Item).order_by(desc(Item.id))[0:20]
    return render_template('catalog.html',
                           categories = categories,
                           latestItems = latestItems)



# "Show item-list associated with a specific category
@app.route('/catalog/<category_name>/items')
def showCategory(category_name):
    # Add SQLAlchemy statements
    """Show items belonging to a specified category.
        Args:
        category_name (str): The name of the category to which the item
        belongs.
        Returns:
        A web page showing all the items in the specified category plus all categories.
    """
    category = session.query(Category).filter_by(name = category_name).one()
    categories = session.query(category).all()
    items = session.query(Item).filter_by(category = category).\
                order_by(Item.name).all()

    # Return count of item "id" grouped by category_name.
    itemTotal = session.query(func.count(
                                Item.id)).group_by(Category.name)
    return render_template('category.html',
                          categories = categories,
                          category = category,
                          items = items,
                          itemTotal = itemTotal)


# "This page is the Item for %s" % item_id
@app.route('/catalog/<category_name>/<item_title>/')
def showItem(category_name, item_title):
    # Add SQLAlchemy statements
    """Show details of a particular item belonging to a specified category.
        Args:
        category_name (str): The name of the category to which the item
            belongs.
        item_title (str): The name of the item.
        Returns:
        A web page showing information of the requested item.
    """
    category = session.query(Category).filter_by(name = category_name).one()
    item = session.query(Item).filter_by(title = item_title).one()
    return render_template('item.html',
                           category = category,
                           item = item)


# "This page will be for adding a new Item"
@app.route('/catalog/new',
methods = ['GET', 'POST'])
def newItem():
    """ Returns:
        GET: newitem.html - form with input for item creation
        POST: if i get a post -redirect to 'showCatalog' after creating new item info.
    """
     # Add SQLAlchemy statements
    if request.method == 'POST':
        newItem = Item(title = request.form['title'], description = request.form['description'], price = request.form['price'] , category_id = category_id)
        session.add(newItem)
        seesion.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newitem.html')


# "This page is for editing Item %s" % item_id
@app.route('/catalog//<category_name>/<item_title>/edit',
methods = ['GETS', 'POST'])
def editItem(category_name, item_title):
    # Add SQLAlchemy statements
    """Edit the details of the specified item.
        Args:
        item_title (str): Title of item to be edited.
        category_name (str): Optionally, can also specify the category to
            which the item belongs to.

        Returns:
        GET: edititem.html - form with inputs to edit item info
        POST: if I get a post - redirect to 'showCategory' after updating item info.
    """

    editedItem = session.query(Item).filter_by(id = item_id).one()
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        if request.form['']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
            return redirect(url_for('showCategory',
                                   category_name = category_name,
                                   item_title = item_title))
    else:
        return render_template('edititem.html',
                              item = editeditem,
                              category_name =  category_name,
                              item_title = item_title)


# "This page is for deleting Item %s" %item_id
@app.route('/catalog/<category_name>/<item_title>/delete')
def deleteItem(category_name, item_title):
    # Add SQLAlchemy statements
    """Delete a specified item from the database.
        Args:
        item_title (str): Title of the item to be deleted.

        Returns:
        GET: deleteitem.html - form for confirmation prior to deletion of item.
        POST: if I get a post -redirect to 'showCategory' after item info deletion.
    """

    category = session.query(Category).filter_by(name = category_name).one()
    itemToDelete = session.query(Item).filter_by(id =item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCategory', category_name = category_name))
    else:
        return render_template('deleteitem.html', category = category_name,
            item = itemToDelete)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(threaded=False)
    app.run(host = '0.0.0.0', port = 8000)
