import os

folder_path = lambda showID: f"{os.getcwd()}\Databases\{showID}"

hash_path = lambda showID: f"{os.getcwd()}\Databases\{showID}\{showID}-hashes.db"
hash_encrypt_path = lambda showID: f"{os.getcwd()}\Databases\{showID}\encrypt-{showID}-hashes.db"

order_path = lambda showID: f"{os.getcwd()}\Databases\{showID}\{showID}-orders.db"
order_encrypt_path = lambda showID: f"{os.getcwd()}\Databases\{showID}\encrypt-{showID}-orders.db"

details_path = lambda showID: f"{os.getcwd()}\Databases\{showID}\show_details.json"
shows_path = f"{os.getcwd()}\Databases\shows.json"

KEY = b'Ya7EtDm2aMrFFSs4d5bYr5wZQBYAc3YvTEcF3GcuHmQ='
admin_username = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
admin_password = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"