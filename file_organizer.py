# File management functions for managing user uploaded image files.

import os


def allowed_file(filename):
    """Check if the filename has one of the allowed extensions.
    Args:
        filename (str): Name of file to check.
    """
    return ('.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS)


def delete_file(filename):
    """Delete an item image file from the filesystem.
    Args:
        filename (str): Name of file to be deleted.
    """
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    except OSError as e:
        print ("Error deleting image file %s") % filename
