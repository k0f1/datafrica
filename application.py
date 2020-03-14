from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

# Add database imports here
from sqlalchemy import create_engine, asc, desc, literal, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item


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

# NEW IMPORTS FOR THIS STEP
from flask import session as login_session
# As keyword b/c we already used the variable session in my database sqlalchemy.
import random, string


# Create ant-forgery state token
@app.route('/login')
def showLogin():
    # This method creates a unique session token with
    # each GET request sent to localhost:8000/login.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
        # state is a random mixed 32 character long string.
        # Store state from our login_session(a dict) in a variable state.
    login_session['state'] = state
    # return "The current session state is %s" %login_session['state']
    # STATE=state was later added after being created in login.html
    return render_template('login.html', STATE=state)



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

    # ADD LOGIN PERMISSION
    # If a user name is not detected for a given request.
    # render publiccatalog.html, else render catalog.html.
    if 'username' not in login_session:
        return render_template('publiccatalog.html',
                                categories = categories,
                                latestItems = latestItems)

    else:
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
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category = category).\
                order_by(Item.title).all()

    # return count of user "id" grouped by "name"
    itemTotal = session.query(func.count(
                                Item.id)).group_by(Item.category_id)

    # ADD LOGIN PERMISSION
    # If a user name is not detected for a given request.
    # Lets return publiccategory.html, else we return category.html.
    if 'username' not in login_session:
        return render_template('publiccategory.html',
                          categories = categories,
                          category = category,
                          items = items,
                          itemTotal = itemTotal)

    else:
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
    category = session.query(Category).filter_by(
                                name = category_name).one()
    item = session.query(Item).filter_by(title = item_title).one()

    # ADD LOGIN PERMISSION
    # If a user name is not detected for a given request.
    # Lets render publicitem.html
    if 'username' not in login_session:
        return render_template('publicitem.html',
                           category = category,
                           item = item)

    else:
        return render_template('item.html',
                           category = category,
                           item = item)


# "This page will be for adding a new Item"
@app.route('/catalog/new',
methods = ['GET', 'POST'])
def newItem():
    """ Returns:
        GET: newitem.html - form with input for item creation
        POST: if I get a post -redirect to 'showCatalog' after creating new item info.
    """
    # ADD LOGIN PERMISSION
    # If a user name is not detected for a given request.
    # Lets redirect to login page.
    if 'username' not in login_session:
        return redirect('/login')
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
    # ADD LOGIN PERMISSION
    # If a user name is not detected for a given request.
    # Lets redirect to login page.
    if 'username' not in login_session:
        return redirect('/login')

    editedItem = session.query(Item).filter_by(id = item_id).one()
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        if request.form['title']:
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
@app.route('/catalog/<category_name>/<item_title>/delete',
    methods = ['GET', 'POST'])
def deleteItem(category_name, item_title):
    # Add SQLAlchemy statements
    """Delete a specified item from the database.
        Args:
        item_title (str): Title of the item to be deleted.

        Returns:
        GET: deleteitem.html - form for confirmation prior to deletion of item.
        POST: if I get a post -redirect to 'showCategory' after item info deletion.
    """
    # ADD LOGIN PERMISSION
    # If a user name is not detected for a given request.
    # Lets redirect to login page.
    if 'username' not in login_session:
        return redirect('/login')

    # filter_by uses the names of the columns in a table
    category = session.query(Category).filter_by(name = category_name).one()
    itemToDelete = session.query(Item).filter_by(id =item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCategory',
                                category_name = category_name,
                                item_title = item_title))
    else:
        return render_template('deleteitem.html',
                                category = category_name,
                                item = itemToDelete)


@app.route('/catalog/cart/')
def showCart():

    """Renders cart.html page.
            Args: None
            Returns:
        GET: cart.html.
    """
    return render_template('cart.html')


# PUT is just like POST only that PUT is idempotent and POST is not.
# ie can make the same request repeatedly while producing the same result.
@app.route('/catalog/cart/add', methods = ['GET', 'PUT'])
def addToCart(item_title):

    """For a user to add a particular item to a cart,  a POST or PUT request has to be sent to the server. Lets modify the server to handle these requests. In application.py, add a route handler addToCart to handle POST or PUT requests for adding item to cart.
        Args:
        item_title (str): The name of the item.
        Returns:
        GET: renders cart.html.
        PUT: sends data of a particular item to the server to update the url.
    """
    addItemToCart = session.query(Item).\
                            filter_by(title=item_title).one()
    cartItems = [].append(addItemToCart)
    if request.method == 'PUT':
        if request.form['title']:
            addItemToCart.title = request.form['title']
        if request.form['description']:
            addItemToCart.description = request.form['description']
        if request.form['price']:
            addItemToCart.price = request.form['price']
        #If I get a POST, redirect to this url.
        return redirect(url_for('showCart'))
    else:
        return render_template('cart.html',
                            addItemToCart = addItemToCart,
                            item_title = item_title)




@app.route('/catalog/cart/<item_title>/delete', methods = ['GET', 'POST'])
def deleteCartItem(item_title):

    """Delete a specified item from the the shopping cart.
        Args:
        item_title (str): Title of the item to be deleted.

        Returns:
        GET: cart.html - showing information prior to deletion of item.
        POST: sends data to the server to update the resource.
    """
    deleteItemFromCart = session.query(Item).filter_by(title = item_title).one()
    if requests.method == 'POST':
        session.delete(deleteItemFromCart)
        # I do not wish to persist my cart
        #If I get a POST, redirect here
        return redirect_uri('showCart')
        return render_template('cart.html',
                            deleteItemFromCart = deleteItemFromCart)
    else:
        return render_template('cart.html',
                            deleteItemFromCart = deleteItemFromCart)






@app.route('/catalog/cart/review')
def reviewCheckout():
    """Review Your Order & Complete Checkout"""
    return render_template('display.html')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    #app.run(threaded=False)
    app.run(host = '0.0.0.0', port = 8000)
