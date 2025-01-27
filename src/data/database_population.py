import psycopg2
import numpy as np
import pandas as pd
from config import config
import random
from faker import Faker

'''
    randomize_data() # randomized data for realistic distribution
    data_consistency() # data consistency (e.g. order_date should be earlier than delivery_date)
    populate_100() # populate with at least 100 entries in the Orders, Order-Items, Customers tables

'''

fake = Faker()

def randomize_data(num_suppliers, num_customers, num_products, num_orders, num_order_items, num_shipments):
    con = psycopg2.connect(**config())
    cursor = con.cursor()

    # Suppliers
    for i in range(num_suppliers):
        name = fake.company()
        contact_info = fake.phone_number()
        country = fake.country()
    
        suppliers_sql = 'INSERT INTO Suppliers (name, contact_info, country) VALUES (%s, %s, %s);'
        suppliers_data = name, contact_info, country
        cursor.execute(suppliers_sql, suppliers_data)
        con.commit()

    # Customers
    for i in range(num_customers):
        name = fake.name()
        location = fake.address().replace("\n", ", ")
        email = fake.email()

        cust_sql = 'INSERT INTO Customers (name, location, email) VALUES (%s, %s, %s);'
        cust_data = name, location, email
        cursor.execute(cust_sql, cust_data)
        con.commit()

    # Products
    for i in range(num_products):
        name = fake.word()
        category = random.choice(['Clothes', 'Hardware', 'Cleaning supplies', 'Bags', 'Hats', 'Shoes'])
        price = round(random.uniform(10.0, 500.0), 2)
        supplier_id = random.randint(1, num_suppliers)
        stock_quantity = random.randint(1, 1000)

        prod_sql = 'INSERT INTO Products (name, category, price, supplier_id, stock_quantity) VALUES (%s, %s, %s, %s, %s);'
        prod_data = name, category, price, supplier_id, stock_quantity
        cursor.execute(prod_sql, prod_data)
        con.commit()

    # Orders
    order_dates = []
    for i in range(num_orders):
        customer_id = random.randint(1, num_customers)
        order_date = fake.date_between(start_date='-5y', end_date='today')
        order_status = random.choice(['ordered', 'fulfilled', 'delivered'])

        orders_sql = 'INSERT INTO Orders (customer_id, order_date, order_status) VALUES (%s, %s, %s);'
        orders_data = customer_id, order_date, order_status
        cursor.execute(orders_sql, orders_data)
        con.commit()

        order_dates.append(order_date)

    # Order_items
    for i in range(num_order_items):
        order_id = random.randint(1, num_orders)
        product_id = random.randint(1, num_products)
        quantity = random.randint(1, 10)
        price_at_purchase = round(random.uniform(10.0, 500.0), 2)

        ord_items_sql = 'INSERT INTO Order_items (order_id, product_id, quantity, price_at_purchase) VALUES (%s, %s, %s, %s);'
        ord_items_data = order_id, product_id, quantity, price_at_purchase
        cursor.execute(ord_items_sql, ord_items_data)
        con.commit()

    # Shipments
    for i in range(num_shipments):
        order_id = random.randint(1, num_orders)
        order_date = order_dates[order_id - 1] # Get the order_date for this order from the list
        shipped_date = fake.date_between(start_date=order_date)
        delivery_date = fake.date_between(start_date=shipped_date)
        shipping_cost = round(random.uniform(5.0, 50.0), 2)

        ship_sql = 'INSERT INTO Shipments (order_id, shipped_date, delivery_date, shipping_cost) VALUES (%s, %s, %s, %s);'
        ship_data = order_id, shipped_date, delivery_date, shipping_cost
        cursor.execute(ship_sql, ship_data)
        con.commit()

    cursor.close()
    con.close()