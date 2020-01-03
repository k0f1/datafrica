from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

# Add database imports here
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item


# Make an instance of create engine
engine = create_engine('sqlite:///catalog.db')

# Bind the engine to the metadata of the Base class
# To establish conversation with the database and act as staging zone
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

# Create DB session instance
session = DBSession()

# Add other imports here


# Show all Categories and latest Items added to the database.
@app.route('/')
@app.route('/catalog')
def showCatalog():
    # Add SQLAlchemy statements
    categories = session.query(Category).order_by(asc(Category.name))
    latestItems = session.query(Item).order_by(desc(Item.id)).limit(20)
    return render_template('catalog.html', categories = categories,
        latestItems = latestItems)



# "Show a Category and items associated with it
# for Category %s" % category_id
@app.route('/catalog/category/<int:category_id>')
def showCategory(category_id):
    # Add SQLAlchemy statements
    category = session.query(Category).filter_by(id = category.id).one()
    items = session.query(Item).filter_by(category_id = category_id).all()
    return render_template('category.html', category = category,
        items = items)


# "This page is the Item for %s" % item_id
@app.route('/catalog/category/<int:category_id>/item/<int:item_id>')
def showItem(category_id, item_id):
    # Add SQLAlchemy statements
    category = session.query(Category).filter_by(id = category_id).one()
    item = session.query(Item).filter_by(id = item_id).one()
    return render_template('item.html', category = category_id,
        item = item_id)


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
@app.route('/catalog//category<int:category_id>/item/<int:item_id>/edit',
methods = ['GETS', 'POST'])
def editItem(category_id, item_id):

    """ Returns:
        GET: edititem.html - form with inputs to edit item info
        POST: if I get a post - redirect to 'showCategory' after updating item info.
    """
    # Add SQLAlchemy statements
    editedItem = session.query(Item).filter_by(id = item_id).one()
    category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        if request.form['']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
            return redirect(url_for('showCategory', category_id = category_id))
    else:
        return render_template('edititem.html', item = editeditem,
        category_id =  category_id, item_id = item_id)


# "This page is for deleting Item %s" %item_id
@app.route('/catalog/category/<int:category_id>/item/<int:item_id>/delete')
def deleteItem(category_id, item_id):
    """ Returns:
        GET: deleteitem.html - form for confirmation prior to deletion of item.
        POST: if I get a post -redirect to 'showCategory' after item info deletion.
    """

    # Add SQLAlchemy statements
    category = session.query(Category).filter_by(id = category_id).one()
    itemToDelete = session.query(Item).filter_by(id =item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCategory', category_id = category_id))
    else:
        return render_template('deleteitem.html', category = category_id,
            item = itemToDelete)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
