
class DbHelper:
    def __init__(self, connection, cursor):
        self.cursor = cursor 
        self.connection = connection

    def create_vertical_fragment(self, dbsrc, dbtarget, tablename, attributes):
        '''
        All argument is str type is expected with the exception of attributes which are of type
        iter(iter(d)) where d = (Field, Type, Null, Key)
        '''
        self.cursor.execute(f'DROP DATABASE IF EXISTS {dbtarget}') 
        self.cursor.execute(f'CREATE DATABASE {dbtarget}') 
        metadata = ', '.join(map(lambda d: str(d[0]) + ' ' + str(d[1]), attributes)) 
        self.cursor.execute(f'CREATE TABLE {tablename} ({metadata})') 
        selectquery = f"SELECT {', '.join(map(labda d: str(d[0])))} FROM {tablename}"
        self.cursor.execute(f'INSERT INTO {dbtarget}.{tablename} {selectquery}') 
        self.connection.commit() # call commit after inserting

    def relation_attributes(self, relation_name):
        """
        Arguments:
            relation_name {str}
        
        Returns:
            tuple(tuple()) -- returns a tuple of tuples such that every element is (Field, Type, Null, Key, Default, Extra)
        """
        self.cursor.execute(f'DESC {relation_name}')
        return self.cursor.fetchall() 

    def count_rows(self, predicate, relation_name):
        query = f"SELECT COUNT(*) FROM {relation_name} WHERE {str(predicate)} "
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall() # tuple of tuples
            return result[0][0]
        except:
            return -1

    def select_all(self, relation_name, predicate=False):
        query = f"SELECT * FROM {relation_name} " + (
            f" WHERE {predicate}" if predicate else "" )
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_attributes(self, relation): # relation: str
        self.cursor.execute( "DESC {}".format(relation) )
        return self.cursor.fetchall()

    def create_fragment_minterm(self, db_src, minterm_predicate, relation, site):
        attributes = self.get_attributes(relation)
        self.cursor.execute(f'DROP DATABASE IF EXISTS {site}') # DROP DATABASE [IF EXISTS] db_name
        self.cursor.execute(f'CREATE DATABASE IF NOT EXISTS {site}')
        self.cursor.execute(f'USE {site}')
        self.cursor.execute(f'DROP TABLE IF EXISTS {relation}')
        print(attributes)
        metadata = ', '.join(map(lambda d: str(d[0]) + ' ' + str(d[1]), attributes)) # d = (Field, Type, Null, Key), avoid keys, avoid problems with horizontal fragmentation
        print(metadata)
        query = 'CREATE TABLE {} ( {} )'.format(relation, metadata)
        self.cursor.execute(query)
        query = f'INSERT INTO {site}.{relation} SELECT * FROM {db_src}.{relation} WHERE {minterm_predicate}'
        self.cursor.execute(query)
        self.connection.commit() # call commit after inserting
        print(query)
        self.cursor.execute(f'USE {db_src}')