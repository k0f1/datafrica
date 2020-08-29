# File management functions for managing user uploaded image files.

import os
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory


UPLOAD_FOLDER = '/var/www/datafrica/datafrica/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the filename has one of the allowed extensions.
    Args:
        filename (str): Name of file to check.
    """
    return ('.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS)


def delete_image(filename):
    """Delete an item image file from the filesystem.
    Args:
        filename (str): Name of file to be deleted.
    """
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    except OSError as e:
        print ("Error deleting image file %s") % filename
