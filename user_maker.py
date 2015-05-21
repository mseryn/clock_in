#!/usr/bin/python
# This is a temporary user-adding solution

import os, sqlite3, hashlib

admin_pass = 'antimatGrav2015'

def user_walkthrough():
    username = input('Username : ')
    os.system('stty -echo')
    password = input('Password : ')
    password_check = input('\nPassword re-type : ')
    os.system('stty echo')
    if password != password_check:
        print('The passwords did not match.')
        quit()
    print('Passwords matched.')
    admin = input('Please enter 1 if the user is an admin or 0 if not : ')
    if admin == '1':
        os.system('stty -echo')
        check = input('Please enter the admin password for this system: ')
        os.system('stty echo')
        if check != admin_pass:
            print('\nInvalid admin password.')
            quit()
    admin_boo = int(admin)

    h_password = hash_pw(username, password)

    make_user(username, h_password, admin_boo)

def make_user(in_username, in_password, in_password_check, in_admin_boo):
    db = sqlite3.connect('db.db')
    c = db.cursor()
    boo = int(in_admin_boo)

    if in_password != in_password_check:
        print('The passwords did not match.')
        quit()

    c.execute("insert into users (username, password, admin) values (?,?,?)", (in_username, in_password, boo))
    db.commit()

def hash_pw(username, password):
    return hashlib.md5(username.encode('utf-8') + password.encode('utf-8')).hexdigest()

if __name__ == "__main__":
    user_walkthrough()
