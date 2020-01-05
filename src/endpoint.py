"""
The endpoint provides a clean REST API  to query and modify the database.
"""
import atexit
from pytz import utc
from flask import Flask, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler


try:
    import db_connection
    from db_bootstrap import bootstrap
    from misc import roll_dice_for_corrupted_files
except ModuleNotFoundError:
    from src import db_connection
    from src.db_bootstrap import bootstrap
    from src.misc import roll_dice_for_corrupted_files



app = Flask(__name__)  #pylint: disable=C0103
CORS(app)


def job_function():
    try:
        db = db_connection.DBConnection()
    except IOError:
        return "Could not connect to DB", 504, {
            'ContentType': 'text/plain'
        }
    db.insert_heart_beat()


cron = BackgroundScheduler()
cron.configure(timezone=utc)
cron.add_job(job_function, 'interval', minutes=1)
cron.start()


@app.before_first_request
def before_first_request_func():
    print('Calling bootstrap before first request')
    bootstrap()


@app.route('/', methods=['GET'])
def database_info():
    """
        Returns the all data stored in the database.

        Args: None
           
        Returns: 
            Response 200 and JSON String where values are list of records 
            indexed by table name as key. 
            Response 504 in case of connection error
    """
    try:
        db = db_connection.DBConnection()
    except IOError:
        return "Could not connect to DB", 504, {
            'ContentType': 'text/plain'
        }
    return db.get_database_info(), 200, {'ContentType': 'application/json'}


@app.route('/info', methods=['GET'])
def connection_stats():
    """
        Returns the connection stats for database connection

        Args: None
           
        Returns: 
            Response 200 and JSON String of connection stats - see 
            DBConnection class for more info.
            Response 504 in case of connection error
    """
    try:
        db = db_connection.DBConnection()
    except IOError:
        return "Could not connect to DB", 504, {
            'ContentType': 'text/plain'
        }
    return db.get_connection_stats(), 200, {'ContentType': 'application/json'}


@app.route('/insertFiles', methods=['POST'])
def insert_files_data():
    """
    Takes a post request with a JSON object of form
    { "Files" : ["file_name_1", "file_name_2", ...] }

    Args: None

    """
    try:
        db = db_connection.DBConnection()
    except IOError:
        return "Database connection not possible", 504, {
            'ContentType': 'text/plain'
        }
    files = request.get_json()
    files = roll_dice_for_corrupted_files(files)
    db.insert_files_names(files['Files'])
    return "Successful Insertion", 200, {'ContentType': 'application/json'}


# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: cron.shutdown(wait=False))


def run():
    """
    Start up Flask endpoint on port 8081
    """
    bootstrap()
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8081)

