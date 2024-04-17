from Strings import *
from cryptography.fernet import Fernet

def encrypt_db(show_id, KEY=KEY):
    try:
        hashDB = hash_path(show_id)
        hashDB_encrypt = hash_encrypt_path(show_id)
        orderDB = order_path(show_id)
        orderDB_encrypt = order_encrypt_path(show_id)
        f = Fernet(KEY)
        with open(hashDB, "rb") as file:
            file_data = file.read()
        os.remove(hashDB)
        encrypted_data = f.encrypt(file_data)
        with open(hashDB_encrypt, "wb") as file:
            file.write(encrypted_data)

        with open(orderDB, "rb") as file:
            file_data = file.read()
        os.remove(orderDB)
        encrypted_data = f.encrypt(file_data)
        with open(orderDB_encrypt, "wb") as file:
            file.write(encrypted_data)
    except:
        return


def decrypt_db(show_id, KEY=KEY):
    try:
        hashDB = hash_path(show_id)
        hashDB_encrypt = hash_encrypt_path(show_id)
        orderDB = order_path(show_id)
        orderDB_encrypt = order_encrypt_path(show_id)
        f = Fernet(KEY)
        with open(hashDB_encrypt, "rb") as file:
            encrypted_data = file.read()
        os.remove(hashDB_encrypt)
        decrypted_data = f.decrypt(encrypted_data)
        with open(hashDB, "wb") as file:
            file.write(decrypted_data)

        with open(orderDB_encrypt, "rb") as file:
            encrypted_data = file.read()
        os.remove(orderDB_encrypt)

        decrypted_data = f.decrypt(encrypted_data)
        with open(orderDB, "wb") as file:
            file.write(decrypted_data)
    except:
        return

encrypt_db(1)