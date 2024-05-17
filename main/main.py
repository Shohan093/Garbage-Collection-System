import numpy as np
import hashlib
import os

# User class
class User:
    def __init__(self, name, address, username, password_hash, salt):
        self.name = name
        self.address = address
        self.username = username
        self.password_hash = password_hash
        self.salt = salt
        self.total_bill = 0

    def receive_warning(self, message):
        print(f"Warning for {self.name}: {message}")

    def check_total_bill(self):
        print(f"Total bill for {self.name}: {self.total_bill} tk")

# UserManager class for handling user registration and login
class UserManager:
    def __init__(self):
        self.users = {}

    # securing password
    def hash_password(self, password, salt):
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest()

    def register_user(self, name, address, username, password):
        if username in self.users:
            print("Username already exists. Please choose a different username.")
        else:
            salt = os.urandom(16).hex()  # Generate a new salt for this user
            password_hash = self.hash_password(password, salt)
            self.users[username] = User(name, address, username, password_hash, salt)
            print(f"User {name} registered successfully.")

    def login_user(self, username, password):
        if username in self.users:
            user = self.users[username]
            if user.password_hash == self.hash_password(password, user.salt):
                print(f"User {username} logged in successfully.")
                return user
            else:
                print("Invalid password.")
        else:
            print("Invalid username.")
        return None

# BillingInfo class
class BillingInfo:
    def __init__(self):
        self.biodegradable_cost = 0
        self.recyclable_cost = 2
        self.non_recyclable_cost = 5
        self.billing_catalog = {}

    # update bill
    def update_bill(self, user, garbage_type):
        if user not in self.billing_catalog:
            self.billing_catalog[user.username] = 0
        if garbage_type == 'biodegradable':
            self.billing_catalog[user.username] += self.biodegradable_cost
        elif garbage_type == 'recyclable':
            self.billing_catalog[user.username] += self.recyclable_cost
        elif garbage_type == 'non_recyclable':
            self.billing_catalog[user.username] += self.non_recyclable_cost

        # update billing catalog
        user.total_bill = self.billing_catalog[user.username]

# SourceBin class
class SourceBin:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.current_load = 0

    # receive garbage
    def receive_garbage(self, user, billing_info):
        if self.current_load < self.capacity:
            self.current_load += 1
        else:
            self.send_warning("Reduce garbage production", user)

    # send to GMP-Bin
    def send_to_gmp_bin(self, gmp_bin, user, billing_info):
        if self.current_load > 0:
            gmp_bin.receive_garbage(user, billing_info)
            self.current_load -= 1

    def send_warning(self, message, user):
        user.receive_warning(message)

# GMPBin class
class GMPBin:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.current_load = 0

    # receive garbage
    def receive_garbage(self, user, billing_info):
        if self.current_load < self.capacity:
            self.current_load += 1
        else:
            self.send_warning("Warning from GMP-bin", user)

    # send to b-bin
    def send_to_bbins(self, b_bin, nb_bin, garbage_type, user, billing_info):
        if garbage_type == 'biodegradable':
            b_bin.receive_garbage(user, billing_info)
        else:
            nb_bin.receive_garbage(garbage_type, user, billing_info)
        billing_info.update_bill(user, garbage_type)

    def send_warning(self, message, user):
        user.receive_warning(message)

# BBin class
class BBin:
    def receive_garbage(self, user, billing_info):
        print("BBin received biodegradable garbage")
        billing_info.update_bill(user, 'biodegradable')

# NBBin class
class NBBin:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.current_load = 0

    # receive garbage
    def receive_garbage(self, garbage_type, user, billing_info):
        if self.current_load < self.capacity:
            self.current_load += 1
            if garbage_type == 'recyclable':
                RBin().receive_garbage(user, billing_info)
            elif garbage_type == 'non_recyclable':
                NRBin().receive_garbage(user, billing_info)
        else:
            self.send_warning("Warning from NB-bin", user)

    def send_warning(self, message, user):
        user.receive_warning(message)

# RBin class
class RBin:
    def receive_garbage(self, user, billing_info):
        print("RBin received recyclable garbage")
        billing_info.update_bill(user, 'recyclable')

# NRBin class
class NRBin:
    def receive_garbage(self, user, billing_info):
        print("NRBin received non-recyclable garbage")
        billing_info.update_bill(user, 'non_recyclable')

# example usage
user_manager = UserManager()
user_manager.register_user("Anisujjaman", "Sylhet", "anis06", "random000")
user_manager.register_user("Shohan", "Rajshahi", "shohan93", "random101")

# user login
logged_in_user = user_manager.login_user("shohan93", "random101")

if logged_in_user:
    billing_info = BillingInfo()

    source_bin = SourceBin()
    gmp_bin = GMPBin()
    b_bin = BBin()
    nb_bin = NBBin()

    # garbage collection process
    source_bin.receive_garbage(logged_in_user, billing_info)
    source_bin.send_to_gmp_bin(gmp_bin, logged_in_user, billing_info)
    gmp_bin.send_to_bbins(b_bin, nb_bin, 'biodegradable', logged_in_user, billing_info)
    gmp_bin.send_to_bbins(b_bin, nb_bin, 'recyclable', logged_in_user, billing_info)
    gmp_bin.send_to_bbins(b_bin, nb_bin, 'non_recyclable', logged_in_user, billing_info)

    # Check the total bill for the user
    logged_in_user.check_total_bill()
