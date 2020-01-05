"""
This module contains all the database information.
There is a Database class to define the schema of the database.
The DBConnection class provides a clean interface to perform operations
on the database.
"""

import json
import os
import time
import random
import psycopg2
from psycopg2 import sql
import sqlalchemy
from sqlalchemy import create_engine


class CorruptFileException(Exception):
    pass


class Database:
    """
    This class is responsible for defining the PostgreSQL database schema.

    Attributes:
        columns: dictionary mapping table names to column names
        schemas: dictionary mapping table names to schema
    """
    _columns = {
        "files": [
            "fileName"
        ],
        "heartbeat": [
            "pid", "TimeStamp"
        ]
    }

    _schemas = {
        "files":
        "(fileName TEXT PRIMARY KEY)",
        "heartbeat":
        "(pid TEXT PRIMARY KEY, TimeStamp FLOAT8)"
    }

    @classmethod
    def get_columns(cls):
        """
        Getter method for columns
        """
        return cls._columns

    @classmethod
    def get_schemas(cls):
        """
        Getter method for schemas
        """
        return cls._schemas


class DBConnection:
    """
    This class is for initiating the connection with the PostgreSQL database.

    Attributes:
        _engine: API object used to interact with database.
        _conn: handles connection (encapsulates DB session)
        _cur:  cursor object to execute PostgreSQl commands
    """

    def __init__(self,
                 db_user=os.environ['POSTGRES_USER'],
                 db_password=os.environ['POSTGRES_PASSWORD'],
                 host_addr="database:5432",
                 max_num_tries=20):
        """
        Initiates a connection with the PostgreSQL database
        It waits in between retries

        Args:
            db_user: username
            db_password: password
            host_addr: host address of the form <host>:<port>
                    the default port is 5432 and the host is "database".
            max_num_tries: the maximum number of tries the __init__ method
            should try to connect to the database for.
        Returns: None

        """
        db_name = os.environ['POSTGRES_DB']

        engine_params = (f'postgresql+psycopg2://{db_user}:{db_password}@'
                         f'{host_addr}/{db_name}')
        num_tries = 1

        while True:
            try:
                self._engine = create_engine(engine_params)
                self._conn = self._engine.raw_connection()
                self._cur = self._conn.cursor()
                break
            except (sqlalchemy.exc.OperationalError,
                    psycopg2.OperationalError):
                # Use binary exponential waits
                time.sleep(random.randint(0, 2**num_tries))
                if num_tries > max_num_tries:
                    raise IOError("Database unavailable")
                num_tries += 1

    def create_tables(self):
        """
        Creates the tables based on schema definition

        Args: None
        Returns: None
        """
        for table, schema in Database.get_schemas().items():
            self._cur.execute(
                sql.SQL("CREATE TABLE IF NOT EXISTS {} {}").format(
                    sql.Identifier(table), sql.SQL(schema)))
        self._conn.commit()

    def insert_heart_beat(self, first=False):
        """
        Insert heartbeat into database
        """
        heartbeat = time.time()
        if first:
            self._cur.execute("INSERT INTO heartbeat (pid, TimeStamp) VALUES (%s, %s)",
                              (os.getpid(), heartbeat))
        else:
            self._cur.execute("UPDATE heartbeat SET Timestamp=%s WHERE pid=%s", (heartbeat, str(os.getpid())))
        self._conn.commit()

    def insert_files_names(self, file_names):
        """
        Inserts file names into database

        Args:
            file_names: a list of file names from the request.
        Returns: None
        """
        for fname in file_names:
            try:
                if fname['corrupted'] == True:
                    raise CorruptFileException
                self._cur.execute("INSERT INTO files(fileName) VALUES ('{0}')".format(fname['file_name']))
                self._conn.commit()
            except CorruptFileException:
                continue

    def get_connection_stats(self):
        """
        Returns the statistics for the database connection

        Args: None

        Returns: A JSON string consisting of connection statistics.
        """
        return json.dumps(self._conn.get_dsn_parameters())

    def get_database_info(self):
        """
        Returns the data stored in the database, indexed by table.

        Args: None

        Returns: A JSON string where keys are table names and values are lists
        of lists.
        This corresponds to the list of records in that table.
        """
        tables = {}
        self._cur.execute(
            "SELECT table_name FROM information_schema.tables \
             WHERE table_schema = 'public'"
        )  # returns an iterable collection of public tables in the database
        for table in self._cur.fetchall():
            cur2 = self._conn.cursor()
            cur2.execute(
                sql.SQL("SELECT * FROM {} ;").format(sql.Identifier(table[0]))
            )  # note sql module used for safe dynamic SQL queries
            tables[table[0]] = cur2.fetchall()
        return json.dumps(tables)

    def clear_data(self):
        """
        Clears the data stored in the database.

        Args: None
        Returns: None
        """
        self._cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE \
            table_schema = 'public'"
        )  # returns an iterable collection of public tables in the database
        for table in self._cur.fetchall():
            cur2 = self._conn.cursor()
            cur2.execute(
                sql.SQL("DELETE FROM {} ;").format(sql.Identifier(table[0]))
            )  # note sql module used for safe dynamic SQL queries
        self._conn.commit()
