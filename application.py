#! /usr/bin/env python3

import os

from flask import Flask
from flask import render_template, request, redirect, jsonify, url_for, flash
# File upload import here
from flask import send_from_directory
from werkzeug.utils import secure_filename
from file_organizer import allowed_file, delete_image
from sqlalchemy.orm.exc import NoResultFound

# Add database imports here
from sqlalchemy import create_engine, asc, desc, literal, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

# NEW IMPORTS FOR THIS STEP
from flask import session as login_session
# As keyword b/c we already used the variable session
# in my database sqlalchemy.

# NEW IMPORTS FOR THIS STEP
from flask import session as login_session
# As keyword b/c we already used the variable session my database sqlalchemy.
import random
import string

# IMPORTS FOR THIS STEP (oauth server side)
from oauth2client import client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

UPLOAD_FOLDER = '/vagrant/catalog/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DECLARE MY CLIENT ID BY REFERENCING THE CLIENT SECRETS FILE
client_id = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Ehelt Catalog App"

# Make an instance of create engine
# engine = create_engine ('sqlite:///catalog.db')
engine = create_engine('sqlite:///catalogwithusers.db')
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
    # return "The current session state is %s" %login_session['state']
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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # Access all credentials including access code.
        credentials = oauth_flow.step2_exchange(code)
        # retreive only the access token in json format.
        access_token = credentials.access_token
    # If an error happen along the way
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Append this token to the following url
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo\
                ?access_token = %s' % access_token)
    # Create a json GET request with these two lines,
    # containing the url and access_token
    h = httplib2.Http()
    result = json.loads((h.request(url, 'GET')[1]).decode('utf-8'))

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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if the user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                    'Current  user is already connected.'), 200)
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
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;\
                border-radius: 150px;-webkit-border-radius: \
                150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """This method revokes a current user's token"""

    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
                        'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s'), access_token
    print('User name is: ')
    print(login_session['username'])
    url = ('https://accounts.google.com/o/oauth2\
            /revoke?token = %s' % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
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
        response = make_response(json.dumps(
                    'Failed to revoke token for given   user.', 400))
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
    print("access token received %s ") % access_token
    # Below, exchange the short-lived token for a long-lived server side token
    # with GET /oauth/access_token?grant_type=fb_exchange_token&client_id=
    # {app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    # send my app secret to Facebook to verify my identity.
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/v5.0/oauth\
            /access_token?grant_type=fb_exchange_token&\
            client_id = %s&client_secret = %s&fb_exchange_token = %s'\
            % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v5.0/me"
    '''
        Due to the formatting for the result from the server token
        exchange we have to split the token first on commas
        and select the first index which gives us the key :
        value for the server access token then we split it
        on colons to pull out the actual token value
        and replace the remaining quotes with nothing so
        that it can be used directly in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/\
            v5.0/me?access_token=%s&fields=id,name,email' % token

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
    url = 'https://graph.facebook.com/v2.8/\
            me/picture?access_token = %s&redirect = 0\
            &height = 200&width = 200' % token
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
    output += ' " style = "width: 300px; height: \
                300px;border-radius: 150px;-webkit-border-radius: \
                150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s\
            /permissions?access_token = %s' % (facebook_id, access_token)
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

    newUser = User(
                    name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
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
    except None:
        # If not, it returns None.
        return None

# END OF LOCAL PERMISSION


# JSON APIs to view Catalog Information
@app.route('/catalog/json')
def catalogJSON():
    categories = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in categories])


@app.route('/catalog/items/json')
def itemsJSON():
    Items = session.query(Item).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/<category_name>/<int:category_id>/<item_title>\
/<int:item_id>/json')
def productItemJSON(category_name, item_title):
    Product_Item = session.query(Item).filter_by(
                        title=item_title).one_or_none()
    return jsonify(Product_Item=Product_Item.serialize)


@app.route('/index')
def showIndex():
    return render_template("index.html")


# Show all Categories and latest Item-list associated with them
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    # Add SQLAlchemy statements
    """Show the index page displaying the categories and
    latest items 20 items added to the database.
    """
    # To protect each category or each category or
    # item based on whoever created it.
    categories = session.query(Category).all()

    # result[::-1] return the slice of every elelement of result in reverse
    latestItems = session.query(Item).order_by(desc(Item.id))[0:20]

    # If there is a username value in the login_session, we would
    # render one template or the other.

    # # # If there is a username value in the login_session, we would
    # render one template or the other.
    # If a user isn't logged in or isn't the original creator
    if 'username' not in login_session:
        return render_template('index.html')
    else:
        return render_template(
            'catalog.html',
            categories=categories,
            latestItems=latestItems,
            # A parameter for conditional login/out
            login_session=login_session)


# "Show item-list associated with a specific category
@app.route('/catalog/<category_name>/<int:category_id>/items')
def showCategory(category_name, category_id):
    # Add SQLAlchemy statements
    """Takes in a specified category_name and returns the
        the items associated with it. Renders a web page
        showing all the categories on one side and the items
         on the other side of the page.
    """
    # NOTE IMPORTANT!
    # In other to handle cases where requested items does not exist,
    # in the database. As it is, if you access the
    # URL: http://localhost:8000/catalog/Frisbee/10/Joylight/250000/.
    # The .one() method in filter_by will return:
    # sqlalchemy.orm.exc.NoResultFound
    # NoResultFound: No row was found for one ()
    # A better way to do that would be using one_or_none().
    # This function returns an object NoneType if it doesn't
    # exist and then you do a PageNotFound when the object is None.
    try:
        category = session.query(Category).\
                filter_by(id=category_id).one_or_none()
    except None:
        return PageNotFound

    categories = session.query(Category).all()
    items = session.query(Item).filter_by(
                    category=category).order_by(asc(Item.title))
    # # return count of item "id" grouped by category_id
    categoryItems = session.query(func.count(
                            Item.id)).filter_by(
                            category_id=category.id).one()

    # # If a user isn't logged in or isn't the original creator, we would
    # render one template or the other. # Decide which page to show,
    # index or category.html
    if 'username' not in login_session:
        return redirect('/login')
    else:
        return render_template(
            'category.html',
            categories=categories,
            category=category,
            items=items,
            categoryItems=categoryItems)


# Role required - creator
@app.route('/catalog/create', methods=['GET', 'POST'])
def newCategory():
    """ Renders a form for input of a new Category - GET request.
        if I get a post -redirect to 'showCatalog' after creating
        new Category info.
    """
    # ADD LOGIN PERMISSION
    # If a username is not detected for a given request.
    # Lets redirect to login page.
    if 'username' not in login_session:
        return redirect('/login')
        # Create an if statement that looks for a post request.
        # By calling request method
    if request.method == 'POST':
        # Extract the name field from my form. .get used b/c of bad request key
        newCategory = Category(
                        name=request.form['name'],
                        user_id=login_session.get('user_id'))
        session.add(newCategory)
        session.commit()
        flash('New Category %s Successfully \
                Created' % newCategory.name)
        # To redirect my user back to the main page.
        # I can use a helper function
        # Url for takes the name of the function as the first arg,
        # and a number of key args, each corresponding to the variable
        # part of the URL rule.
        return redirect(url_for('showCatalog'))
    else:
        # If my server did not receive a post request, it will go ahead
        # and render the template for the new HTML template that i created.
        return render_template('newcategory.html')


# Role required -employee creator
@app.route('/catalog/<category_name>/<int:category_id>\
/edit', methods=['GET', 'POST'])
def editACategoryName(category_name, category_id):
    """1. First execute a query to find the exact item we want
            to update:  Find entry and store it in a variable
        2. Next Reset values: we declare the new name of
        the variable
        3. Next we add the variable to our session
        4. Finally we commit the the session the database
 """
    # Execute a query to find the category and store it in
    # a variable editedCategory.
    try:
        categoryToEdit = session.query(Category).\
                    filter_by(id=category_id).one_or_none()
    except None:
        return PageNotFound

    # ADD LOGIN PERMISSION
    # Protect app modification from non-users
    # If a username is not detected for a given request.
    # Lets redirect to login page.
    if 'username' not in login_session:
        return redirect('/login')
    # Verify that a user is logged in by
    # checking if the username has a variable filled in
    # If a user isn't logged in "Alert message"
    if categoryToEdit.user.id != login_session['user_id']:
        return "<script>function myFunction() {alert( 'You are not\
                 authorized to edit this category.');}\
                 </script><body onload='myFunction()'>"

    # Create an if statement that looks for a post request.
    # By calling request method
    if request.method == 'POST':
        # Then create an if statement that looks for a name in the form.
        # By calling request form get.
        if request.form['name']:
            # Now reset the name of the category to the new name from the form
            categoryToEdit.name = request.form['name']
        # To edit, you don't need to add it again.
        session.commit()
        flash('Category successfully edited %s' % categoryToEdit.name)
        # Redirect the user back to the home page.
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'editacategoryname.html',
            category=categoryToEdit)


# Role required - employee creator
@app.route('/catalog/<category_name>/<int:category_id>\
/delete', methods=['GET', 'POST'])
def deleteCategory(category_name, category_id):
    # Execute a query to find the category and store it in a variable.
    try:
        category = session.query(Category).\
                        filter_by(id=category_id).one_or_none()
    except None:
        return PageNotFound

    try:
        categoryToDelete = session.query(Category).\
                    filter_by(id=category_id).one_or_none()
    except None:
        return PageNotFound
    creator = getUserInfo(category.user_id)

    # ADD LOGIN PERMISSION
    # If a user name is not detected for a given request.
    # Lets redirect to login page.
    if 'username' not in login_session:
        return redirect('/login')
    # To protect each item based on whoever created it.
    # If a user isn't logged in or isn't the original creator
    if categoryToDelete.user.id != login_session['user_id']:
        # The script gives not only an alert that you are not,
        # but also we stay where we are right here.
        return "<script>function myFunction() {alert('You are not\
                authorized to delete this category.\
                Please create your own category in order\
                 to edit categories.');}</script><body onload='myFunction()'>"
    else:
        render_template('deletecategory.html',
                        category=categoryToDelete,
                        creator=creator)
    # Create an if statement that looks for a post request.
    # By calling request method
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash('%s Successfully Deleted' % categoryToDelete.name)
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
                            'deletecategory.html',
                            category=categoryToDelete)


@app.route('/catalog/myitems/')
def showUserItems():
    """If logged in, show the user the items they have added."""
    if 'username' not in login_session:
        return redirect('/login')

    user_id = get_user_id(login_session['email'])

    categories = session.query(Category).all()
    items = session.query(Item).filter_by(user_id=user_id).all()

    if not items:
        flash("You haven't add any animals yet.")
        redirect(url_for('showCatalog'))

    return render_template('useritems.html',
                           categories=categories,
                           items=items)


# "This page is the Item for %s" % item_id
@app.route('/catalog/<category_name>/<int:category_id>\
/<item_title>/<int:item_id>/')
def showItem(category_name, category_id, item_title, item_id):
    # Add SQLAlchemy statements
    """Renders product information web page of an item.
    """
    try:
        category = session.query(Category).\
            filter_by(id=category_id).one_or_none()

    except None:
        return PageNotFound

    try:
        item = session.query(Item).filter_by(id=item_id).one_or_none()
    except None:
        return PageNotFound

    creator = getUserInfo(item.user_id)

    # # # If there is a username value in the login_session, we would
    # render one template or the other.
    if 'username' not in login_session:
        return redirect(url_for('/login'))
        # Decide which page should be visible to the public
        # And which one should be private
    else:
        return render_template(
                            'item.html',
                            category=category,
                            item=item,
                            creator=creator)

# Role required: User- creator
# "This page will be for adding a new Item"
@app.route('/catalog/new', methods=['GET', 'POST'])
def newItem():
    """ Renders a form for input of a new item -
        GET request. if I get a post -redirect to
        'showItem' after creating new item.
    """
    # ADD LOGIN PERMISSION
    # Protect app modification from non-users
    # If a username is not detected for a given request.
    # Lets redirect to login page.

    if 'username' not in login_session:
        return redirect('/login')

    categories = session.query(Category).all()

    # Add SQLAlchemy statements
    if request.method == 'POST':
        # This is key to retreiving category from the form.
        try:
            category = (session.query(Category).filter_by(
                        name=request.form.get('category')).one_or_none())
        except None:
            return PageNotFound

        newItem = Item(
                    category=category,
                    title=request.form['title'],
                    description=request.form['description'],
                    price=request.form['price'],
                    user_id=login_session['user_id'])
        # access the file from the files dictionary
        # on request object:
        # file = request.files['file']

        # Process optional item image.
        image_file = request.files['file']
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            if os.path.isdir(app.config['UPLOAD_FOLDER']) is False:
                os.mkdir(app.config['UPLOAD_FOLDER'])
            image_file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))
            newItem.image_filename = filename
        elif request.form['basic_url']:
            newItem.basic_url = request.form['basic_url']

        session.add(newItem)
        session.commit()
        flash('New Item %s successfully Created' % newItem.title)
        # Now define the url variable path to the newItem created.

        creator = getUserInfo(newItem.user_id)
        # Show response to my post request in the client.
        return redirect(url_for(
                'showItem',
                category_name=category_name,
                category_id=category_id,
                item_title=item_title,
                item_id=item_id,
                creator=creator))
    else:
        return render_template('newitem.html', categories=categories)


# Role required user- creator
# "This page is for editing Item %s" % item_id
@app.route('/catalog//<category_name>/<int:category_id>\
/<item_title>/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(category_name, category_id, item_title, item_id):
    """Edit the details of the specified item.
        Returns a GET with edititem.html - form with
        inputs to edit item info
        if I get a post - redirect to 'showCategory'
        after updating item info.
    """
    # ADD LOGIN PERMISSION
    # If a user name is not detected for a given request.
    # Lets redirect to login page.
    if 'username' not in login_session:
        return redirect('/login')
    # Add SQLAlchemy statements
    categories = session.query(Category).all()

    try:
        category = session.query(Category).\
                    filter_by(id=category_id).one_or_none()
    except None:
        return PageNotFound

    try:
        editedItem = session.query(Item).filter_by(
                            id=item_id).one_or_none()
    except None:
        # If a NoneType object is returned
        return PageNotFound
    return redirect(url_for('showCatalog'))

    # To protect each item based on whoever created it.
    creator = getUserInfo(editedItem.user_id)

    # ADD ALERT MESSAGE TO PROTECT.
    # If a user isn't logged in or isn't the original creator
    if 'username' not in login_session or\
            creator.id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not\
                authorized to edit this item. Please create your\
                own item in order to edit items.');}\
                </script><body onload='myFunction()'>"

    if request.method == 'POST':
        # This is key to retreiving the category from the form.
        category = (session.query(Category).filter_by(
                    name=request.form.get('category')).one())
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.files['file']:
            editedItem.image_filename = request.files['file']

        # Process optional item image
        image_file = request.files['file']
        if image_file and allowed_file(image_file.filename):
            if editedItem.image_filename:
                delete_image(editedItem.image_filename)
            filename = secure_filename(image_file.filename)
            if os.path.isdir(app.config['UPLOAD_FOLDER']) is False:
                os.mkdir(app.config['UPLOAD_FOLDER'])
            image_file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))

            editedItem.image_filename = filename
            editedItem.basic_url = None

        elif ('delete_image' in request.form and
              request.form['delete_image'] == 'delete'):
            if editedItem.image_filename:
                delete_image(editedItem.image_filename)

        if not image_file and request.form['basic_url']:
            editedItem.basic_url = request.form['basic_url']
            if editedItem.image_filename:
                delete_image(editedItem.image_filename)

        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for(
                'showCategory',
                category_name=category_name,
                category_id=category_id))
    else:
        return render_template(
                'edititem.html',
                category=category,
                categories=categories,
                item=editedItem)


# Role required: User creator
# "This page is for deleting Item %s" %item_id
@app.route('/catalog/<category_name>/<int:category_id>\
/<item_title>/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, category_id, item_title, item_id):
    # Add SQLAlchemy statements
    """Delete a specified item from the database.
        Returns: GET: deleteitem.html - form for confirmation prior
        to deletion of item.
        POST: if I get a post -redirect to 'showCategory'
        after item info deletion.
    """
    # ADD LOGIN PERMISSION
    # If a user name is not detected for a given request.
    # Lets redirect to login page.
    if 'username' not in login_session:
        return redirect('/login')
    # filter_by uses the names of the columns in a table
    try:
        category = session.query(Category).\
                    filter_by(id=category_id).one_or_none()
    except None:
        return PageNotFound

    try:
        itemToDelete = session.query(Item).filter_by(
                            id=item_id).one_or_none()
    except None:
        return PageNotFound

    creator = getUserInfo(itemToDelete.user_id)
    # ADD ALERT MESSAGE TO PROTECT.
    # If a user isn't logged in or isn't the original creator
    if 'username' not in login_session or\
            creator.id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not\
                authorized to edit this item. Please create\
                 your own item in order to edit items.');}\
                 </script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for(
                    'showCategory',
                    category_name=category_name,
                    category_id=category_id))
    else:
        return render_template(
                    'deleteitem.html',
                    category=category,
                    item=itemToDelete)


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


@app.route('/item_images/<filename>')
def show_item_image(filename):
    """Route to serve user uploaded images.
    Args:
        filename (str): Filename of the image to serve to the client.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    # app.run(ssl_context='adhoc')
    app.run(threaded=False)
    app.config['UPLOAD_FOLDER'] = True
    app.run(host='0.0.0.0', port=8000)
