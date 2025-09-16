# create_user.py
import bcrypt
import getpass

# 1. Get the password securely from the terminal
password = getpass.getpass("Enter the password to hash: ")

# 2. Encode the password to bytes
password_bytes = password.encode('utf-8')

# 3. Generate a salt and hash the password
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password_bytes, salt)

# 4. Print the hash so you can copy it
# The result will be bytes, so we decode it to a string to print it
print("\n---")
print("Copy this entire line into your MOCK_USERS dictionary:")
print(f'"{hashed_password.decode()}"')
print("---")