# dependency
from mongoengine import *


class DB:
    """
    A Class representing a MongoDB based database.
    @param  host    str         the host name
    @paran  port    str(int)    the port number
    @param  name    str         the DB name
    """

    def __init__(self, host, port, name):
        self.__host = host
        self.__port = port
        self.__name = name

    def get_DB_url(self):
        """
        A method that returns URL of the DB.
        @return     url     str     the url of the DB
        """
        return f"mongodb://{self.__host}:{self.__port}"

    def get_DB_name(self):
        """
        A method that returns name of the DB.
        @return     name    str     the name of the DB
        """
        return self.__name
