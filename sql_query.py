import sqlite3

if __name__ == "__main__":

    path = 'test.sqlite3'

    # connect to the locally populated database
    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    # Select the row with the highest value as well as its block number between 2024-01-01 00:00:00(1704067200) and 2024-01-01 00:30:00(1704069000)
    query = "SELECT max(value), block_number FROM transactions WHERE timestamp BETWEEN (1704067200) AND (1704069000);"
    cursor.execute(query)
    ans = cursor.fetchall()

    print("The max etherium transfered in 1 block between the allotted time is", ans[0][0], "in the block", str(ans[0][1]) + '.')