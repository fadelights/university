# database driver allowing connections to PostgreSQl from Python
import psycopg2

# main ETL framework
import pygrametl
from pygrametl.datasources import SQLSource
from pygrametl.tables import FactTable, TypeOneSlowlyChangingDimension

# connect to database
db_conn = psycopg2.connect(dbname='library')  # replace with your own connection info

# connect to data warehouse
warehouse_conn = psycopg2.connect(dbname='warehouse')  # replace with your own connection info
dw_conn_wrap = pygrametl.ConnectionWrapper(connection=warehouse_conn)

# acquire our source data from relevant tables
books_source = SQLSource(connection=db_conn, query="SELECT * FROM book_data", initsql=open('init.sql', 'r').read())
users_source = SQLSource(connection=db_conn, query="SELECT * FROM users")
borrows_source = SQLSource(connection=db_conn, query="SELECT * FROM borrow_data")

# create fact table and dimensions
books_dim = TypeOneSlowlyChangingDimension(
    name='books',
    key='isbn',
    attributes=['title',
                'edition',
                'descr',
                'genres',
                'authors',
                'translators',
                'pub_date',
                'publisher',
                'language',
                'original'],
    lookupatts=['title']
)

users_dim = TypeOneSlowlyChangingDimension(
    name='users',
    key='user_id',
    attributes=['name',
                'birth_date',
                'join_date',
                'phone_no',
                'address'],
    lookupatts=['name'],
)

borrows_fact = FactTable(
    name='borrows',
    keyrefs=['user_id', 'isbn'],
    measures=['remain_count']
)

## ETL flow ##

# automatic insertion/updates

for row in borrows_source:
    borrows_fact.ensure(row)

for row in books_source:
    books_dim.scdensure(row)

for row in users_source:
    users_dim.scdensure(row)

# close connections
dw_conn_wrap.commit()
dw_conn_wrap.close()

# functions to check for deleted rows
dw_conn = psycopg2.connect(dbname='warehouse')
dw_curs = dw_conn.cursor()

db_conn = psycopg2.connect(dbname='library')
db_curs = db_conn.cursor()
db_curs.execute(open('init.sql', 'r').read())

def check_borrows():
    """Check whether or not the `borrows` table
    has deleted rows in the original database
    and delete accordingly"""

    # acquire DB data
    db_query =\
        """
        select * from borrow_data
        """
    db_curs.execute(db_query)
    db_results = db_curs.fetchall()

    # acquire DW data
    dw_query =\
        """
        select user_id, isbn, remain_count from borrows
        """
    dw_curs.execute(dw_query)
    dw_results = dw_curs.fetchall()

    # compare results
    for row in dw_results:
        # in case row was deleted
        if row not in db_results:
            del_query =\
                """
                delete from borrows
                where user_id = %s
                    and
                      isbn = %s
                    and
                      remain_count = %s
                """
            dw_curs.execute(del_query, (row[0], row[1], row[2]))
    

def check_books():
    """Check whether or not the `books` table
    has deleted rows in the original database
    and delete accordingly"""

    # acquire DB data
    db_query =\
        """
        select * from book_data
        """
    db_curs.execute(db_query)
    db_results = db_curs.fetchall()

    # acquire DW data
    dw_query =\
        """
        select * from books
        """
    dw_curs.execute(dw_query)
    dw_results = dw_curs.fetchall()
    
    # elimiate timestamp columns
    dw_results = [row[:-1] for row in dw_results]

    # compare results
    for row in dw_results:
        # in case row was deleted
        if row not in db_results:
            del_query =\
                """
                delete from books
                where isbn = %s
                """
            dw_curs.execute(del_query, (row[0],))


def check_users():
    """Check whether or not the `users` table
    has deleted rows in the original database
    and delete accordingly"""

    # acquire DB data
    db_query =\
        """
        select * from users
        """
    db_curs.execute(db_query)
    db_results = db_curs.fetchall()

    # acquire DW data
    dw_query =\
        """
        select * from users
        """
    dw_curs.execute(dw_query)
    dw_results = dw_curs.fetchall()

    # elimiate timestamp columns
    dw_results = [row[:-1] for row in dw_results]

    # compare results
    for row in dw_results:
        # in case row was deleted
        if row not in db_results:
            del_query =\
                """
                delete from users
                where user_id = %s
                """
            dw_curs.execute(del_query, (row[0],))


check_borrows()
check_books()
check_users()

# commit and close connections
dw_conn.commit()
dw_conn.close()
db_conn.close()
