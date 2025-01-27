import psycopg2
from config import config
from database_population import randomize_data
from analytical_queries import *
from datetime import datetime


def database_design():
    con = None
    try:
        con = psycopg2.connect(**config())  
        cursor = con.cursor()

        # the database query
        SQL = '''

        -- Create table Suppliers
        CREATE TABLE IF NOT EXISTS Suppliers (
            id SERIAL PRIMARY KEY,
            name varchar(255) NOT NULL,
            contact_info varchar(255), -- ?
            country varchar(255)
        );

         INSERT INTO Suppliers (id, name, contact_info, country)
        VALUES
            ('1', 'jack', 'asdf', 'finland'),
            ('2', 'john', 'etry', 'finland'),
            ('3', 'merv', '5hest', 'finland')
        ;

        '''
        cursor.execute(SQL)
        con.commit()

        # Close cursor
        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

def main():
    database_design()
    #randomize_data(150, 170, 350, 400, 300, 250)
    #analyze()

if __name__ == "__main__":
    main()