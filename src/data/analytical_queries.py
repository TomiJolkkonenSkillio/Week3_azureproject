import psycopg2
import numpy as np
import pandas as pd
from config import config
from datetime import datetime

'''
    basic_counts_sums() # tot no. of orders, tot sales, products w. low stock
    grouping_aggregations() # tot. sales per product category, avr. order value, monthly breakdown of no. of orders and tot. sales
    joins_multitablequeries() # list of orders, each order shows cust. name and tot. order value, top 5 customers tot. spending, supplier list w. details
    nestedqueries_subqueries() # non-ordered products, customer over x€ spent per order, orders w. biggest quantity
    advanced_analyticalqueries() # daily orders trend, peak order days, avr. delivery time per month, % of tot. sales filtered by top 10% of product sales.
'''



def basic_counts_sums():
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor()

        # Total number of orders
        cursor.execute("SELECT COUNT(*) FROM Orders;")
        total_orders = cursor.fetchone()[0]
        print(f"Tot no. of orders: {total_orders}")

        # Total sales
        cursor.execute("SELECT SUM(price_at_purchase * quantity) FROM Order_items;")
        total_sales = cursor.fetchone()[0]
        print(f"Tot sales: {total_sales}")

        # Products with low stock under 10)
        cursor.execute("SELECT name, stock_quantity FROM Products WHERE stock_quantity < 10;")
        low_stock_products = cursor.fetchall()
        print("Products with low stock:")
        for product in low_stock_products:
            print(product)

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()


def grouping_aggregations():
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor()

        # Total sales per product category
        cursor.execute(
            """
            SELECT category, SUM(price_at_purchase * quantity) AS total_sales
            FROM Products
            JOIN Order_items ON Products.id = Order_items.product_id
            GROUP BY category;
            """
        )
        category_sales = cursor.fetchall()
        print("Tot sales per category:")
        for row in category_sales:
            print(row)

        # Average order value
        cursor.execute(
            """
            SELECT AVG(total_value) FROM (
                SELECT order_id, SUM(price_at_purchase * quantity) AS total_value
                FROM Order_items
                GROUP BY order_id
            ) AS OrderValues;
            """
        )
        average_order_value = cursor.fetchone()[0]
        print(f"Avr order €: {round(average_order_value, 2)}")

        # Monthly statistics of no. of orders and tot sales
        cursor.execute(
            """
            SELECT DATE_TRUNC('month', order_date) AS month, 
                   COUNT(*) AS total_orders,
                   SUM(price_at_purchase * quantity) AS total_sales
            FROM Orders
            JOIN Order_items ON Orders.id = Order_items.order_id
            GROUP BY month
            ORDER BY month;
            """
        )
        monthly_breakdown = cursor.fetchmany(10)
        print("Monthly statistics:")
        for row in monthly_breakdown:
            print(f"Date: {row[0].date()}, no. of orders: {row[1]}, total sales: {row[2]}")

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()


def joins_multitablequeries():
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor()

        # Orders with cust name and tot order €
        cursor.execute(
            """
            SELECT Orders.id, Customers.name AS customer_name, SUM(price_at_purchase * quantity) AS total_order_value
            FROM Orders
            JOIN Customers ON Orders.customer_id = Customers.id
            JOIN Order_items ON Orders.id = Order_items.order_id
            GROUP BY Orders.id, Customers.name;
            """
        )
        orders_list = cursor.fetchmany(10)
        print("List of orders with customer names and total values:")
        for row in orders_list:
            print(row)

        # Top 5 customers by tot spending
        cursor.execute(
            """
            SELECT Customers.name, SUM(price_at_purchase * quantity) AS total_spent
            FROM Customers
            JOIN Orders ON Customers.id = Orders.customer_id
            JOIN Order_items ON Orders.id = Order_items.order_id
            GROUP BY Customers.name
            ORDER BY total_spent DESC
            LIMIT 5;
            """
        )
        top_customers = cursor.fetchall()
        print("Top 5 customers by total spending:")
        for row in top_customers:
            print(row)

        # Supplier list with details
        cursor.execute("SELECT * FROM Suppliers;")
        suppliers = cursor.fetchmany(10)
        print("Supplier list:")
        for supplier in suppliers:
            print(supplier)

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()


def nestedqueries_subqueries():
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor()

        # Non-ordered products
        cursor.execute(
            """
            SELECT name FROM Products
            WHERE id NOT IN (SELECT DISTINCT product_id FROM Order_items);
            """
        )
        non_ordered_products = cursor.fetchmany(10)
        print("Products with zero orders:")
        for product in non_ordered_products:
            print(product)

        # Customers who spent more than X per order (e.g., 100)
        cursor.execute(
            """
            SELECT DISTINCT Customers.name
            FROM Customers
            JOIN Orders ON Customers.id = Orders.customer_id
            JOIN (
                SELECT order_id, SUM(price_at_purchase * quantity) AS total_value
                FROM Order_items
                GROUP BY order_id
            ) AS OrderValues ON Orders.id = OrderValues.order_id
            WHERE total_value > 100;
            """
        )
        high_spending_customers = cursor.fetchmany(10)
        print("Customers with over 100 € per order:")
        for customer in high_spending_customers:
            print(customer)

        # Orders with the biggest quantities
        cursor.execute(
            """
            SELECT Orders.id, SUM(quantity) AS total_quantity
            FROM Orders
            JOIN Order_items ON Orders.id = Order_items.order_id
            GROUP BY Orders.id
            ORDER BY total_quantity DESC
            LIMIT 1;
            """
        )
        largest_order = cursor.fetchone()
        print(f"Biggest order quantity: {largest_order}")

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()


def advanced_analyticalqueries():
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor()

        # Daily orders trend
        cursor.execute(
            """
            SELECT order_date, COUNT(*) AS total_orders
            FROM Orders
            GROUP BY order_date
            ORDER BY order_date;
            """
        )
        daily_trend = cursor.fetchmany(10)
        print("Trending daily orders:")
        for row in daily_trend:
            print(f"Date: {row[0]}, no. of orders: {row[1]}")

        # Peak order days
        cursor.execute(
            """
            SELECT order_date, COUNT(*) AS total_orders
            FROM Orders
            GROUP BY order_date
            ORDER BY total_orders DESC
            LIMIT 5;
            """
        )
        peak_days = cursor.fetchall()
        print("Peak order days:")
        for day in peak_days:
            print(f"Date: {row[0]}, quantity: {row[1]}")

        # Average delivery time per month
        cursor.execute(
            """
            SELECT DATE_TRUNC('month', shipped_date) AS month, 
                   AVG(delivery_date - shipped_date) AS avg_delivery_time
            FROM Shipments
            GROUP BY month
            ORDER BY month;
            """
        )
        avg_delivery_time = cursor.fetchmany(10)
        print("Avr delivery time per month:")
        for row in avg_delivery_time:
            print(f"Date: {row[0].date()}, avg delivery time: {round(row[1], 2)}")

        # Percentage of total sales by top 10% of product sales
        cursor.execute(
            """
            WITH ProductSales AS (
                SELECT
                    product_id,
                    SUM(price_at_purchase * quantity) AS total_sales
                FROM Order_items
                GROUP BY product_id
            ),
            RankedSales AS (
                SELECT
                    product_id,
                    total_sales,
                    ROW_NUMBER() OVER (ORDER BY total_sales DESC) AS rank,
                    COUNT(*) OVER () AS total_products
                FROM ProductSales
            ),
            Top10PercentSales AS (
                SELECT
                    total_sales
                FROM RankedSales
                WHERE rank <= total_products / 10
            )
            SELECT
                SUM(total_sales) * 100.0 / (
                    SELECT SUM(total_sales) FROM ProductSales
                ) AS top_10_percent_sales
            FROM Top10PercentSales;
            """
        )
        top_10_percent_sales = cursor.fetchone()[0]
        print(f"% of tot sales by top 10%% products: {round(top_10_percent_sales, 2)}%")

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()


def analyze():
    basic_counts_sums()
    grouping_aggregations()
    joins_multitablequeries()
    nestedqueries_subqueries()
    advanced_analyticalqueries()

def main():
    analyze()


if __name__ == "__main__":
    main()