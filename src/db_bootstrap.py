"""
Run the bootstrap procedure for the endpoint and database.
"""

import glob

try:
    import db_connection
    import endpoint
except ModuleNotFoundError:
    import src.db_connection as db_connection
    import src.endpoint as endpoint


def bootstrap():
    """
        Sets up the database.

        Args: None
        Returns: None
    """
    db = db_connection.DBConnection()  #pylint: disable=C0103
    db.create_tables()
    print("Created database tables")

    db.clear_data()

    db.insert_heart_beat(first=True)
    print("Bootstrap procedure complete")


if __name__ == '__main__':  #set up database and endpoint
    bootstrap()
    endpoint.run()
