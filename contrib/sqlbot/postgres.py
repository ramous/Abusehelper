#
# PostgreSQL implementation rely on python-pygresql
#
import pgdb


class PostgresConnector():
    '''
        Implement a wrapper for SQL queries on Postgres using DB-API compliant interface pgdb.
        For more information, look http://www.pygresql.org/pgdb.html
        
        Notice: no schema knowledge is contained in this class!
    '''
    connection = None
 
    def __init__(self, dbsrv, dbname, dbusr, dbpwd):
        '''
            Create a new instance of PostgresConnector and establish connection
    
            Parameters are:
            dbsrv  = address of postgres server
            dbname = name of the database to use
            dbusr  = user to use for connection
            dbpwd  = password of the user
        '''
        self.connection = pgdb.connect(dbsrv + ":" + dbname + ":" + dbusr + ":" + dbpwd)

    def close(self):
        '''
            Close connection to DB
        '''
        self.connection.close()

    def executeAndCommit(self, query, *values):
        '''
            Execute the query given in parameter and commit transaction
        '''
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()

    def executeAndReturnResult(self, query, *values):
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        try:    
            result = cursor.fetchall()
            return result
        except:
            return None

    def getConnection(self):
        '''
            Return reference to internal DB pointer
        '''
        return self.connection

