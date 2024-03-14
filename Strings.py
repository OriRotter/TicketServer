import os

folder_path = lambda showID: f"{os.getcwd()}\Databases\{showID}"

hash_path = lambda showID: f"{os.getcwd()}\Databases\{showID}\{showID}-hashes.db"

order_path = lambda showID: f"{os.getcwd()}\Databases\{showID}\{showID}-orders.db"


