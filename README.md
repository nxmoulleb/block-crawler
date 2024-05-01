Relayer Technical 
===============================
## Overview
The python file `block_crawler.py` contains the code to create a table, populate it with data about etherium transactions, and prints the resulting table. The program was tested with a local SQLite3 database but supports postgreSQL URI.

`sql_query.py` finds the block with the maximum amount of etherium traded from the time 2024-01-01 00:00:00 to 2024-01-01 00:30:00 (1704067200 to 1704069000 in epoch unix form).

## `block_crawler.py`

The `block_crawler.py` starts by parsing the args in the main if statement. From there, we loop through all the blocks from start to end and get the etherium data. Some of the calls to the endpoint return null values, which we need to be repared for. All null records are ignored. For this problem the data we care about is the timestamp, block number, total value, and number of transactions. These fields are extracted from the data. The value of etherium is stored in WEI, which is converted to ETH and then stored in the DB. 

Below you will find the usage statement for the program.

```
usage: block_crawler.py [-h] endpoint path startEnd

Populates a database with data about etherium transactions between block number {start} and {end}

positional arguments:
  endpoint    A JSON-RPC endpoint to call an Ethereum client
  path        The path to the database. Can be a local SQLite3 file or or a postgreSQL connection URI
  startEnd    A block range, formatted as "{start}-{end}"

options:
  -h, --help  show this help message and exit
```
## `sql_quer.py`
This was creates as a helper to execute the following SQL command on a local sqlite3 database. 

The path varaible can be edited to look at a different local sqlite3 database. If the database is postgreSQL, the following SQL command can be used to find the answer. 

`SELECT max(value), block_number FROM transactions WHERE timestamp BETWEEN (1704067200) AND (1704069000);`