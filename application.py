#! /usr/bin/env python3

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, g


# Add database imports here
from sqlalchemy import create_engine, asc, desc, literal, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User





# NEW IMPORTS FOR THIS STEP
from flask import session as login_session
# As keyword b/c we already used the variable session in my database sqlalchemy.
import random, string


# Add other imports here

# NEW IMPORTS FOR SHOPPING CART
from flask import session as cart_session


# NEW IMPORTS FOR THIS STEP
from flask import session as login_session
# As keyword b/c we already used the variable session my database sqlalchemy.
import random, string



#IMPORTS FOR THIS STEP (oauth server side)
from oauth2client import client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)


# DECLARE MY CLIENT ID BY REFERENCING THE CLIENT SECRETS FILE
client_id = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Ehelt Catalog App"





# Make an instance of create engine
engine = create_engine ('sqlite:///catalog.db')


# Bind the engine to the metadata of the Base class
# To establish conversation with the database and act as staging zone
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

# Create DB session instance
session = DBSession()



# Create ant-forgery state token
@app.route('/login')
def showLogin():
    # This method creates a unique session token.This token is sent along side
    # the one-time code sent by google via GET request sent to
    # localhost:8000/login.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in range(32))
                # state is a random mixed 32 character long string.
                # Store state from our login_session(a dict)
                # in a variable state.
    login_session['state'] = state
    #return "The current session state is %s" %login_session['state']
    # to see what are current state look like. STATE is sent back with oauth.
    return render_template('login.html', STATE=state)




# HANDLER OF CODE SENT BACK FROM CALLBACK METHOD - one time code from google
@app.route('/gconnect', methods=['GET', 'POST'])
def gconnect():
    # Call request args get for my code to examine the state
    # token passed in and compares it to the state of the login session.
    if request.args.get('state') != login_session['state']:
        # If there is mismatch
        response = make_response(json.dumps('invalid state token'), 401)
        response.headers['content-Type'] = 'application/json'
        return response
    # If there is a match
    # Obtain authorization code from my server with request data function
    # Request is variable that holds data and information about code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json',
            scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # Access all credentials including access code.
        credentials = oauth_flow.step2_exchange(code)
        # retreive only the access token in json format.
        access_token = credentials.access_token.to_json()
    # If an error happen along the way
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #Append this token to the following url
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
          % access_token)
          #Create a json GET request with these two lines,
          # containing the url and access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    # Only the it_token part is extracted from credential object.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != client_id:
        response = make_response(
            json.dumps("token's client ID does not match the app's."), 401
        )
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if the user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current  user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one.
    # Get user id on the email address stored in our log-in session
    # stored in the variable user_id.
    user_id = getUerID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id



# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """This method revokes a current user's token"""

    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s'), access_token
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given   user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response



# FACEBOOK SIGN IN
@app.route('/fbconnect', methods=['GET', 'POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print ("access token received %s ") % access_token
    # Below, exchange the short-lived token for a long-lived server side token
    # with GET /oauth/access_token?grant_type=fb_exchange_token&client_id=
    # {app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads( # I have to send my app secret to Facebook
        # to verify my identity.
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/v5.0/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v5.0/me"

    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/\nv5.0/me?access_token=%s&fields=id,name,email' % token

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Welcome splash screen
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output



@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['facebook_id']
    return "you have been logged out"

#####


# LOCAL PERMISSION SYSTEM
# User Helper Functions
# Local permission system, leverages the information
# stored in the log in session object, and uses the server side logic
# in the datatbase to control the user experience based on
# provided credential. To implement LPS, our database has
# to start storing information in a more user specifci manner.
# We need a table of users, so we can identify what data belongs to whom.
# This step include work on lotsofitems as well.


# createUser takes in login_session as input
def createUser(login_session):

    """create new user in our database, extracting all
    the fields neccessary to populate it from information
    gathered from the login_session"""

    newUser = User(name=login_session['username'],
        email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    # Then returns a user_id of the new user created
    return user.id



def getUserInfo(user_id):

    """If a user ID is passed into this method,
    it simply returns the user object associated with this ID number."""

    user = session.query(User).filter_by(id=user_id).one()
    # Returns user object associated with this number.
    return user



def getUserID(email):

    """This method, takes an email address and return and ID,
    if that email address belongs to  user stored in our database"""

    try:
        user = session.query(User).filter_by(email=email).one()
        # Returns an ID number if the email address belongs to
        # a user stored in our database.
        return user.id
    except:
        # If not, it returns None.
        return None

# END OF LOCAL PERMISSION



#JSON APIs to view Catalog Information
@app.route('/catalog/json')
def catalogJSON():
    categories = session.query(Category).all()
    return jsonify(Category =[i.serialize for i in categories])



@app.route('/catalog/items/json')
def itemsJSON():
    Items = session.query(Item).all()
    return jsonify(Items = [i.serialize for i in items])



@app.route('/catalog/<category_name>/<item_title>/json')
def productItemJSON(category_name, item_title):
    Product_Item = session.query(Item).filter_by(title = item_title).one()
    return jsonify(Product_Item = Product_Item.serialize)



# Show all Categories and latest Item-list associated with them
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    # Add SQLAlchemy statements
    """Show the index page displaying the categories and latest items 20 items added to the database."""
    categories = session.query(Category).all()
    # result[::-1] return the slice of every elelement of result in reverse
    latestItems = session.query(Item).order_by(desc(Item.id))[0:20]
    # If there is a username value in the login_session, we would
    # render one template or the other.
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
    """Takes in a specified category_name and returns the the items associated with it. Renders a web page showing all the categories on one side and the items on the other side of the page.
    """
    # The filter_by function always returns a collection of objects
    # .one method ensures only one category is returned
    category = session.query(Category).\
            filter_by(name = category_name).one()
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id = category.id).all()
    # # return count of item "id" grouped by category_id
    categoryItems = session.query(func.count(
                            Item.id)).filter_by(
                            category_id = category.id).one()

    # # If there is a username value in the login_session, we would
    # render one template or the other.
    if 'username' not in login_session:
        # Decide which page to show, public or private
        return render_template('publiccategory.html',
                                categories = categories,
                                category = category,
                                items = items,
                                categoryItems = categoryItems)
    else:
        return render_template('category.html',
                          categories = categories,
                          category = category,
                          items = items,
                          categoryItems = categoryItems)




# "This page is the Item for %s" % item_id
@app.route('/catalog/<category_name>/<item_title>/')
def showItem(category_name, item_title):
    # Add SQLAlchemy statements
    """Renders product information web page of an item.
    """
    category = session.query(Category).\
            filter_by(name = category_name).one()
    item = session.query(Item).filter_by(title = item_title).one()

    # # # If there is a username value in the login_session, we would
    # render one template or the other.
    if 'username' not in login_session:
        # Decide which page should be visible to the public
        # And which one should be private
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
    """ Renders a form for input of a new item - GET request.
        if I get a post -redirect to 'showCatalog' after creating new item info.
    """

    # ADD LOGIN PERMISSION
    # Protect app modification from non-users
    # If a username is not detected for a given request.
    # Lets redirect to login page.


    # Verify that a user is logged in by
    # checking if the username has a variable filled in
    if 'username' not in login_session:
        return redirect('/login')
     # Add SQLAlchemy statements
    if request.method == 'POST':
        newItem = Item(title = request.form['title'], description = request.form['description'], price = request.form['price'] , category_id = category_id, user_id=login_session['user_id'])
        session.add(newItem)
        flash('New Item %s successfully Created' % newItem)
        seesion.commit()
        # Decide which page should be visible to the public
        # And which one should be private
        return redirect(url_for('showCatalog'))
    else:
        return render_template('publiccatalog.html')




# "This page is for editing Item %s" % item_id
@app.route('/catalog//<category_name>/<item_title>/edit',
methods = ['GETS', 'POST'])
def editItem(category_name, item_title):
    # Add SQLAlchemy statements
    """Edit the details of the specified item.
        Returns a GET with edititem.html - form with inputs to edit item info
        if I get a post - redirect to 'showCategory' after updating item info.
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
        if request.form['picture']:
            editedItem.picture = request.form['picture']
            return redirect(url_for('showCategory',
                                   category_name = category_name,
                                   item_title = item_title))
    else:
        return render_template('edititem.html',
                              item = editeditem,
                              category_name = category_name,                              item_title = item_title)




# "This page is for deleting Item %s" %item_id
@app.route('/catalog/<category_name>/<item_title>/delete',
    methods = ['GET', 'POST'])
def deleteItem(category_name, item_title):
    # Add SQLAlchemy statements
    """Delete a specified item from the database.
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




@app.route('/catalog/cart')
def shoppingCart():
    # Cart = Basket
    """Displays content of shopping cart. The cart is a list held in the session that contains all items added.
    """
    if "cart" not in cart_session:
        flash("Your Shopping Basket is Empty")
        return render_template("cart.html", total = 0)
    else:
        items = cart_session['cart']
        for item in items:
            item.id = id
            item.title = title
            item.description = description
            item.price = price
            qty = count(item.id)
            subtotal = qty*price
            total = len(items)
            return render_template("cart.html")



@app.route('/catalog/<category_name>/<item_title>/add_item')
def addItemToCart(category_name, item_title):
    """ Shopping cart functionality using session variables to hold
        cart list.
        Intended behavior: when an item is added to a cart, redirect them to the shopping cart page, while displaying the message "Successfully added to Basket"
    """
    # Retreive the item JSON data.
    url = '/catalog/<category_name>/<item_title>/add_item'
    # Build my response here
    # Configure qty to be equal to success status(200) count
    h = httplib2.Http()
    result = h.request(url, 'GET')[1] # response is [1]
    data = json.loads(result)
    if result['status'] == '200':
        cart_session['item.id'] = data["id"]
        cart_session['title'] = data["title"]
        cart_session['description'] = data["description"]
        cart_session['price'] = data["price"]
        flash("New Item added to the Basket")
        return render_template("cart.html")
    else:
        return render_template('item.html',
                           category = category,
                           item = item)






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
        cart_session.delete(deleteItemFromCart)
        return redirect_uri('shoppingCart')
    else:
        return render_template('cart.html',
                            deleteItemFromCart = deleteItemFromCart)




@app.route('/catalog/checkout/')
def checkout():
    """Review Your Order & Complete Checkout"""
    flash("Sorry, checkout is still to be implemented")
    return render_template('display.html')




@app.route('/logout')
def disconnect():
    """Checks if the provider has been set in login_session"""

    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))





if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(threaded=False)
    app.run(host = '0.0.0.0', port = 8000)
