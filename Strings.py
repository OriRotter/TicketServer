import os

folder_path = lambda showID: f"{os.getcwd()}\Databases\{showID}"

hash_path = lambda showID: f"{os.getcwd()}\Databases\{showID}\{showID}-hashes.db"
hash_encrypt_path = lambda showID: f"{os.getcwd()}\Databases\{showID}\encrypt-{showID}-hashes.db"

order_path = lambda showID: f"{os.getcwd()}\Databases\{showID}\{showID}-orders.db"
order_encrypt_path = lambda showID: f"{os.getcwd()}\Databases\{showID}\encrypt-{showID}-orders.db"

KEY = b'Ya7EtDm2aMrFFSs4d5bYr5wZQBYAc3YvTEcF3GcuHmQ='
admin_username = "admin"
admin_password = "admin"