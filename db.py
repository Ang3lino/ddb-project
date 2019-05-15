
class DbHelper:
    def __init__(self, connection, cursor):
        self.cursor = cursor 
        self.connection = connection

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

    def create_fragment_minterm(self, attributes, db_src, minterm_predicate, relation, site):
        self.cursor.execute(f'DROP DATABASE IF NOT EXISTS {site}')
        self.cursor.execute(f'CREATE DATABASE IF NOT EXISTS {site}')
        self.cursor.execute(f'USE {site}')
        self.cursor.execute(f'DROP TABLE IF EXISTS {relation}')
        metadata = ', '.join(map(lambda d: d[0] + ' ' + d[1], attributes)) # d = (Field, Type, Null, Key), avoid keys, avoid problems with horizontal fragmentation
        query = 'CREATE TABLE {} ( {} )'.format(relation, metadata)
        self.cursor.execute(query)
        query = f'INSERT INTO {site}.{relation} SELECT * FROM {db_src}.{relation} WHERE {minterm_predicate}'
        self.cursor.execute(query)
        self.connection.commit() # call commit after inserting
        print(query)
        self.cursor.execute(f'USE {db_src}')