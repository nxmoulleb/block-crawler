import argparse
import requests
import json
import sqlite3
from urllib.parse import urlparse
import psycopg2
import web3

def get_connection_from_path(path):
    """
    Gets a connection to the database based on the path. 

    Args:
        path (String): The path to the database. The path can either be a local sqlite3 db or a postgreSQL URI.
    
    Returns:
        connection: The connection object which goes to the db.
    """
    
    if(path.startswith('postgresql://')):
        try:
            result = urlparse("path")
            username = result.username
            password = result.password
            database = result.path[1:]
            hostname = result.hostname
            port = result.port
            connection = psycopg2.connect(
                database = database,
                user = username,
                password = password,
                host = hostname,
                port = port
            )
            print("Connected to postgreSQL db")
            return connection
        except Exception as e:
            print(f"Error while connecting to postgreSQL db: {e}")
    else:
        try:
            connection = sqlite3.connect(path)
            print("Connected to sqlite3 db")
            return connection
        except sqlite3.Error as e:
            print(f"Error while connecting to sqlite3 db: {e}")

def print_sql_table(path, table_name):
    """
    Prints the formatted table based on the path and table name.

    Args:
        path (String): The path to the database. 
        table_name (String): The name of the table to be printed.
    """
   
    try:
        # Get connection from path
        connection = get_connection_from_path(path)
        cursor = connection.cursor()

        # Select all rows from the specified table
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)

        # Get the column names from the result
        column_names = [description[0] for description in cursor.description]

        # Print the column names
        print(" | ".join(column_names))
        print("-" * (len(column_names) * 4))

        # Print each row's data
        for row in cursor.fetchall():
            print(" | ".join(str(value) for value in row))

    except sqlite3.Error as e:
        print(f"Error: {e}")

    finally:
        # Close the database connection
        connection.close()

def create_table(path):
    """
    Create a table if it does not exist using the path.

    Args:
        path (String): The path to the database.
    """

    # Get connection from path
    connection = get_connection_from_path(path)

    # Create table schema
    create_table_sql = """ CREATE TABLE IF NOT EXISTS transactions (
                            block_number INTEGER PRIMARY KEY,
                            transaction_number INTEGER,
                            timestamp INTEGER,
                            value FLOAT
                        ); """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
        connection.commit()
        print("Table created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
    finally:
        connection.close()

def add_record_to_table(connection, timestamp, transaction_number, block_number, value):
    """
    Adds a record to table.

    Args:
        connection (): A connection to a database.
        timestamp (int): The time of the transaction.
        transaction_number (int): The number of transactions in this block. 
        block_number (int): The number of this block.
        value (float): The total value in eth of all the transactions in this block.
    """

    try:
        sql = 'INSERT INTO transactions(timestamp, transaction_number, block_number, value) VALUES(?,?,?,?)'
        cursor = connection.cursor()
        cursor.execute(sql, (timestamp, transaction_number, block_number, value))
        connection.commit()
        print("Record inserted successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting record: {e}")

def get_eth_block(endpoint, path, start, end):
    """
    Gets the etherium block.

    Args:
        endpoint (String): The endpoint which we are requesting for etherium data.
        path (String): The path to the database which we will populate.
        start (int): The starting block we are getting.
        end (end): The last etherium block that we are getting.
    """
    
    connection = get_connection_from_path(path)
    for id in range(start, end):
        try:
            # Request the endpoint by block number. Uses the requests library to format the request. Uses id to keep track of which block is which.
            payload = {"method":"eth_getBlockByNumber","params":[hex(id),True],"id":id,"jsonrpc":"2.0"}
            headers = {'content-type': 'application/json'}
            r = requests.post(endpoint, data=json.dumps(payload), headers=headers)
            resultsJson = r.json()
            
            if(resultsJson['result']):
                transactions = resultsJson['result']['transactions']
                 
                 # Get the total value of all transactions in the block and convert it from WEI to ETH
                total_value = 0
                for transaction in transactions:
                    value_in_wei = int(transaction['value'], 0)
                    # convert the value from WEI to ETH so it fits in the SQL table
                    value_in_ether = value_in_wei/1000000000000000000
                    total_value += value_in_ether
                     
                # Add the important information from the block to the table
                add_record_to_table(connection,  
                                    int(resultsJson['result']['timestamp'], 0), # timestamp of the block
                                    len(transactions), # The amount of transactions. Some of these may have a value of 0
                                    resultsJson['id'], # The id is the block number, because of the id we set in our request.
                                    total_value)
        except Exception as e:
            print(id, "broken:", e)
    connection.close()

if __name__ == "__main__":
    # Add arguments to the program using argparse
    parser = argparse.ArgumentParser(description="A block crawler")
    parser.add_argument('endpoint', help="A JSON-RPC endpoint to call an Ethereum client")
    parser.add_argument('path', help="The path of the SQLite file to write to or a connection URI")
    parser.add_argument('startEnd', help="A block range, formatted as \"{start}-{end}\"")

    args = parser.parse_args()

    endpoint = args.endpoint
    path = args.path
    startEnd = args.startEnd

    # Create table if it doesnt exist
    create_table(path)

    # Make sure that start-end is correctly formatted
    try:
        start = int(startEnd.split('-')[0])
        end = int(startEnd.split('-')[1])
        get_eth_block(endpoint, path, start, end)
        print_sql_table(path, 'transactions')
    except:
        print("Improperly formatted start-end. It should be formatted as follows: \'{start}-{end}\', where {start} and {end} are integers")

    