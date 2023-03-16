import requests as rq
import sqlite3
from tkinter import messagebox
from datetime import datetime
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash

warehouse = "testwarehouse.db"

def create_database():
    conn = sqlite3.connect(warehouse,
                           detect_types=sqlite3.PARSE_DECLTYPES |
                                        sqlite3.PARSE_COLNAMES)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        loc_id INTEGER PRIMARY KEY,
        location TEXT NOT NULL UNIQUE,
        loc_zone TEXT NOT NULL,
        loc_utn INTEGER,
        item TEXT DEFAULT '',
        alt_item_one TEXT DEFAULT '', 
        alt_item_two TEXT DEFAULT '',
        item_stock INTEGER DEFAULT 0,
        alt_item_one_stock INTEGER DEFAULT 0,
        alt_item_two_stock INTEGER DEFAULT 0,
        loc_history TEXT DEFAULT '',
        FOREIGN KEY (item) REFERENCES items (item),
        FOREIGN KEY (alt_item_one) REFERENCES items (item),
        FOREIGN KEY (alt_item_two) REFERENCES items (item))""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS items (
        item REFERENCES locations (item),
        item_num TEXT,
        item_type TEXT,
        item_brand TEXT,
        location TEXT, 
        loc_id INTEGER,
        alt_location_one TEXT DEFAULT '', 
        alt_location_two TEXT DEFAULT '',
        weight INTEGER,
        onhand INTEGER DEFAULT 0, 
        pallet_qty INTEGER,
        item_history TEXT DEFAULT '',
        FOREIGN KEY (location) REFERENCES locations (location),
        FOREIGN KEY (alt_location_one) REFERENCES locations (location),
        FOREIGN KEY (alt_location_two) REFERENCES locations (location))""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT,
        userpass TEXT,
        email TEXT,
        user_id INTEGER,
        name_full TEXT,
        name_nick TEXT,
        branch_perms TEXT,
        status TEXT)""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        date TIMESTAMP,
        user TEXT,
        type TEXT,
        item TEXT,
        location TEXT,
        log TEXT,
        log_id INTEGER)""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS orderlog (
        date TIMESTAMP,
        user TEXT,
        order_num TEXT,
        order_items TEXT,
        order_notes TEXT)""")

    conn.commit()
    conn.close() 
    

def pack_database():
    r = rq.get('https://api.sheety.co/1df786a24857eae9f8e9c6fdd9a4e227/warehouse/sheet1').json()['sheet1']

    conn = sqlite3.connect(warehouse)
    c = conn.cursor()
    c.execute("SELECT * FROM locations")
    loc_list = c.fetchall()
    c.execute("SELECT * FROM items")
    item_list = c.fetchall()
    c.execute("SELECT * FROM users")
    user_list = c.fetchall()
    print(user_list)
    conn.commit()
    conn.close()
    if len(loc_list) != 0 and len(item_list) != 0:
        print("DID NOT PACK DATABASE")
        return
    
    ### CREATE STARTER USER ###
    if len(user_list) == 0:
        new_pass = generate_password_hash('boss1234')
        new_user = ('testboss', new_pass, 'testboss@twclimate.com', 100, 'Test Boss', 'TST', '024', 'master')
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute('INSERT INTO users (username, userpass, email, user_id, name_full, name_nick, branch_perms, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', new_user)
        conn.commit()
        conn.close()

    ### FILL DATABASE ###
    item_list = []
    location_list = []
    for item in r:
        print(item)
        if item['itemName'] != 'n/a':
            if item['itemName'] not in item_list:
                item_to_add = (item['itemName'], item['itemNumber'], item['location'], item['loc#'], item['type'], item['brand'], item['weight'], item['fullPallet'], item['location']) 
                try:
                    conn = sqlite3.connect(warehouse)
                    c = conn.cursor()
                    c.execute('INSERT INTO items (item, item_num, location, loc_id, item_type, item_brand, weight, pallet_qty, item_history) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', item_to_add)
                    item_list.append(item['itemName'])
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print(e)
            elif item_list.count(item['itemName']) == 1:
                try:
                    conn = sqlite3.connect(warehouse)
                    c = conn.cursor()
                    # UPDATE ITEM_HISTORY
                    c.execute("SELECT item_history FROM items WHERE item = ?", (item['itemName'],))
                    temp_history = c.fetchone()[0]
                    new_history = temp_history + f" {item['location']}"
                    # UPDATE ITEM
                    c.execute('UPDATE items SET alt_location_one=?, item_history=? WHERE item=?', (item['location'], new_history, item['itemName']))
                    item_list.append(item['itemName'])
                    conn.commit()
                    conn.close()

                except Exception as e:
                    print(e)
            elif item_list.count(item['itemName']) == 2:
                try:
                    conn = sqlite3.connect(warehouse)
                    c = conn.cursor()                    
                    c.execute("SELECT item_history FROM items WHERE item = ?", (item['itemName'],))
                    temp_history = c.fetchone()[0]
                    new_history = temp_history + f" {item['location']}"
                    c.execute('UPDATE items SET alt_location_two=? WHERE item=?', (item['location'], item['itemName']))
                    item_list.append(item['itemName'])
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print(e)
            else:
                pass

        if item['location'] not in location_list:
            try:
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                location_to_add = (item['loc#'], item['location'], item['zone'], item['itemName'], f"{item['itemName']}")
                if item['itemName'] == 'n/a':
                    location_to_add = (item['loc#'], item['location'], item['zone'], '', '')
                c.execute('INSERT INTO locations (loc_id, location, loc_zone, item, loc_history) VALUES (?, ?, ?, ?, ?)', location_to_add)
                location_list.append(item['location'])
                conn.commit()
                conn.close()
            except Exception as e:
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                location_to_add = (item['loc#'], item['location'], item['zone'])
                c.execute('INSERT INTO locations (loc_id, location, loc_zone) VALUES (?, ?, ?)', location_to_add)
                location_list.append(item['location'])
                conn.commit()
                conn.close()
        else:
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            c.execute('SELECT alt_item_one FROM locations WHERE location=?', (item['location'],))
            if c.fetchone()[0] == '':
                c.execute("SELECT loc_history FROM locations WHERE location = ?", (item['location'],))
                temp_history = c.fetchone()[0]
                new_history = temp_history + f" {item['location']}"
                add_alt_one = (item['itemName'], item['itemName'], item['location'])
                c.execute('UPDATE locations SET alt_item_one=?, loc_history=? WHERE location=?', add_alt_one)
            else:
                c.execute("SELECT loc_history FROM locations WHERE location = ?", (item['location'],))
                temp_history = c.fetchone()[0]
                new_history = temp_history + f" {item['location']}"
                add_alt_two = (item['itemName'], item['itemName'], item['location'])
                c.execute('UPDATE locations SET alt_item_two=?, loc_history=? WHERE location=?', add_alt_two)
            conn.commit()
            conn.close()


def reset_database(note, order):
    conn = sqlite3.connect(warehouse)
    c = conn.cursor()
    c.execute("DELETE FROM items")
    c.execute("DELETE FROM locations")
    if note == 1:
        c.execute("DELETE FROM notes")
    if order == 1:    
        c.execute("DELETE FROM orderlog")
    conn.commit()
    conn.close()   
    pack_database()
    return


def check_credentials(mode, uname='', upass='', ubranch=''):
    if mode == 'login':
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("SELECT * from users WHERE username = ?", (uname,))
        check_user = c.fetchone()
        conn.commit()
        conn.close()
        # CHECK USERNAME
        if check_user == None:
            messagebox.showerror(title="Error", message="Username not found")
            return False
        # CHECK PASSWORD
        if not check_password_hash(check_user[1], upass):
            messagebox.showerror(title="Error", message="Incorrect Password")
            return False
        # CHECK BRANCH PERMISSIONS
        branch_perms = check_user[6]
        if ubranch != branch_perms:
            messagebox.showerror(title="Error", message="User not allowed at this branch")
            return False
        # RETURN USER INFO
        return check_user

    if mode == 'pass':
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("SELECT userpass from users WHERE username = ?", (uname,))
        check_pass = c.fetchone()[0]
        conn.commit()
        conn.close()
        if not check_password_hash(check_pass, upass):
            return False
        return True

    # new_pass = generate_password_hash('boss1234')
    # new_user = ('testboss', new_pass, 'testboss@twclimate.com', 100, 'Test Boss', 'TST', '024', 'master')

### NOTES FOR EDIT, ADD, REMOVE USERS ###
def edit_user_database(user_info, mode='', cur_user_info='', master_info=''):
    if mode == 'e':
        if cur_user_info == '':
            messagebox.showerror(title='Error', message='Error updating user database')
            return
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        ## CHECK EXISTING VALUES
        # USERNAME
        if user_info[0] != cur_user_info[0]:
            c.execute("SELECT * from users WHERE username = ?", (user_info[0],))
            check_user = c.fetchone()
            if check_user != None:
                messagebox.showerror(title="Error", message="Username already exists")
                conn.commit()
                conn.close()
                return
        # EMAIL
        if user_info[1] != cur_user_info[1]:
            c.execute("SELECT * from users WHERE email = ?", (user_info[1],))
            check_user = c.fetchone()
            if check_user != None:
                messagebox.showerror(title="Error", message="Email already exists")
                conn.commit()
                conn.close()
                return
        # USER_ID
        if user_info[2] != cur_user_info[2]:
            c.execute("SELECT * from users WHERE user_id = ?", (user_info[2],))
            check_user = c.fetchone()
            if check_user != None:
                messagebox.showerror(title="Error", message="UserID already exists")
                conn.commit()
                conn.close()
                return
        # FULL_NAME
        if user_info[3] != cur_user_info[3]:
            c.execute("SELECT * from users WHERE name_full = ?", (user_info[3],))
            check_user = c.fetchone()
            if check_user != None:
                messagebox.showerror(title="Error", message="Username already exists")
                conn.commit()
                conn.close()
                return
        # NICK_NAME
        if user_info[4] != cur_user_info[4]:
            c.execute("SELECT * from users WHERE name_nick = ?", (user_info[4],))
            check_user = c.fetchone()
            if check_user != None:
                messagebox.showerror(title="Error", message="Nickname already exists")
                conn.commit()
                conn.close()
                return
        ### COMMIT CHANGES TO DB ###
        new_user = (user_info[0], user_info[1], user_info[2], user_info[3], user_info[4], user_info[5], user_info[6], cur_user_info[0])
        c.execute('UPDATE users SET username = ?, email = ?, user_id = ?, name_full = ?, name_nick = ?, branch_perms = ?, status = ? WHERE username = ?', new_user)
        print('User added to database')    
        conn.commit()
        conn.close()
        ### ADD EDIT NOTE TO DB ###
        add_note(note_type='user', user=master_info, mode='edit', new_info=new_user[:7], cur_info=cur_user_info)
        return

    if mode == 'a':
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        ## CHECK EXISTING VALUES
        # USERNAME
        c.execute("SELECT * from users WHERE username = ?", (user_info[0],))
        check_user = c.fetchone()
        if check_user != None:
            messagebox.showerror(title="Error", message="Username already exists")
            conn.commit()
            conn.close()
            return
        # EMAIL
        c.execute("SELECT * from users WHERE email = ?", (user_info[2],))
        check_user = c.fetchone()
        if check_user != None:
            messagebox.showerror(title="Error", message="Email already exists")
            conn.commit()
            conn.close()
            return
        # USER_ID
        c.execute("SELECT * from users WHERE user_id = ?", (user_info[3],))
        check_user = c.fetchone()
        if check_user != None:
            messagebox.showerror(title="Error", message="UserID already exists")
            conn.commit()
            conn.close()
            return
        # FULL_NAME
        c.execute("SELECT * from users WHERE name_full = ?", (user_info[4],))
        check_user = c.fetchone()
        if check_user != None:
            messagebox.showerror(title="Error", message="Username already exists")
            conn.commit()
            conn.close()
            return
        # NICK_NAME
        c.execute("SELECT * from users WHERE name_nick = ?", (user_info[5],))
        check_user = c.fetchone()
        if check_user != None:
            messagebox.showerror(title="Error", message="Nickname already exists")
            conn.commit()
            conn.close()
            return
        ### ADD NEW USER TO DB ###
        pass_hash = generate_password_hash(user_info[1])
        new_user = (user_info[0], pass_hash, user_info[2], user_info[3], user_info[4], user_info[5], user_info[6], user_info[7])
        c.execute('INSERT INTO users (username, userpass, email, user_id, name_full, name_nick, branch_perms, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', new_user)
        print('User added to database')
        conn.commit()
        conn.close()
        ### ADD NOTE TO DB ###
        new_user_info = (user_info[0], user_info[2], user_info[3], user_info[4], user_info[5], user_info[6], user_info[7])
        add_note(note_type='user', user=master_info, mode='add', new_info=new_user_info)
        return   

    if mode == 'r':
        ### REMOVE USER FROM DB ###
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE user_id = ?", (user_info,))
        del_uname = c.fetchall()[0]
        c.execute("DELETE FROM users WHERE user_id = ?", (user_info,))
        conn.commit()
        conn.close()
        ### ADD NOTE TO DB ###
        add_note(note_type='user', user=master_info, mode='del', del_info=del_uname)
        return    


def get_user_info(q, uid=''):
    if q == 'a':
        user_list = []
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("SELECT username, email, user_id, name_full, name_nick, branch_perms, status FROM users")
        users = c.fetchall()
        conn.commit()
        conn.close()
        return users

    if q == 's':
        if uid != '':
            user_list = []
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            c.execute("SELECT username, email, user_id, name_full, name_nick, branch_perms, status FROM users WHERE user_id = ?", (uid,))
            user = c.fetchone()
            conn.commit()
            conn.close()            
            return user
        return


def warehouse_inquiry(tag=0, type=0, search=0, **kwargs):
    itag = tag
    itype = type
    isearch = search
    
    if itag == 'type':
        type_list = []
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute('SELECT DISTINCT item_type FROM items')
        temp_list = c.fetchall()
        conn.commit()
        conn.close()
        type_list = [row[0] for row in temp_list]
        return type_list        

    if itag == 'brand':
        brand_list = []
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute('SELECT DISTINCT item_brand FROM items')
        temp_list = c.fetchall()
        conn.commit()
        conn.close()
        brand_list = [row[0] for row in temp_list]
        return brand_list
        
    if itag == 'zone':
        zone_list = []
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute('SELECT DISTINCT loc_zone FROM locations')
        temp_list = c.fetchall()
        conn.commit()
        conn.close()
        for zone in range(len(temp_list)):
            zone_list += temp_list[zone]
        return zone_list
    
    if itag == 'loc':
        if kwargs['mode'] == 'add_loc_pop':
            if itype == 'r':
                loc_list = []
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                c.execute('SELECT location, item, alt_item_one, alt_item_two FROM locations ORDER BY loc_id')
                temp_list = c.fetchall()
                conn.commit()
                conn.close()
                for loc in range(len(temp_list)):
                    loc_list += temp_list[loc]
                return loc_list        

            loc_list = []
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            c.execute('SELECT location FROM locations ORDER BY loc_id')
            temp_list = c.fetchall()
            conn.commit()
            conn.close()
            for loc in range(len(temp_list)):
                loc_list += temp_list[loc]
            return loc_list        
        else:
            e = isearch
            if e == "":
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                c.execute("SELECT * from locations ORDER BY loc_id")
                locations = c.fetchall()
                conn.commit()
                conn.close()
                return locations
            elif e == "empty":
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                c.execute("SELECT * from locations WHERE item = '' ORDER BY loc_id")
                locations = c.fetchall()
                conn.commit()
                conn.close()
                return locations        
            else:
                e = f"%{e}%"
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                c.execute("SELECT * from locations WHERE item LIKE ? or alt_item_one LIKE ? or alt_item_two LIKE ? or location LIKE ? ORDER BY loc_id", (e, e, e, e))
                locations = c.fetchall()
                conn.commit()
                conn.close()
                return locations 

    if tag == 'loc_id':
        if kwargs['mode'] == 's':
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            c.execute("SELECT loc_id FROM locations WHERE location = ?", (kwargs['location'],))
            location_ids = c.fetchone()[0]
            conn.commit()
            conn.close()
            return location_ids
        
        if kwargs['mode'] == 'a':
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            c.execute("SELECT loc_id FROM locations WHERE location = ?", (kwargs['location'],))
            start_id = c.fetchone()[0]
            c.execute("SELECT loc_id, location, loc_zone FROM locations WHERE loc_id >= ?", (start_id,))
            location_ids = c.fetchall()
            conn.commit()
            conn.close()
            return location_ids

        if kwargs['mode'] == 'r':
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            c.execute("SELECT loc_id FROM locations WHERE location = ?", (kwargs['location'],))
            start_id = c.fetchone()[0]
            c.execute("SELECT loc_id, location FROM locations WHERE loc_id >= ?", (start_id,))
            location_ids = c.fetchall()
            conn.commit()
            conn.close()
            return location_ids
            pass

    if tag == 'loc_info':
        location = kwargs['location']
        item = kwargs['item']
        ### IF ITEM IS GIVEN ###
        if item != '':
                    conn = sqlite3.connect(warehouse)
                    c = conn.cursor()
                    c.execute("SELECT loc_id, location, item, alt_item_one, alt_item_two, item_stock, alt_item_one_stock, alt_item_two_stock FROM locations WHERE item = ? OR alt_item_one = ? OR alt_item_two =?", (item, item, item))
                    location_info = c.fetchall()
                    conn.commit()
                    conn.close()
                    return location_info

        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("SELECT * FROM locations WHERE location = ?", (location,))
        location_info = c.fetchone()
        conn.commit()
        conn.close()
        return location_info

        

    if itag == 'cc':
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute('SELECT * FROM locations WHERE item != ?', ('',))
        location_list = c.fetchall()
        conn.commit()
        conn.close()
        return location_list

    if itag == 'item_inv':
        if isearch == "":
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            c.execute("SELECT item, item_num, item_type, item_brand, location, alt_location_one, alt_location_two, onhand, weight, pallet_qty FROM items ORDER BY loc_id")
            item_list = c.fetchall()
            conn.commit()
            conn.close()
            for x in range(len(item_list)):
                try:
                    conn = sqlite3.connect(warehouse)
                    c = conn.cursor()
                    c.execute("SELECT loc_zone FROM locations WHERE location=?", (item_list[x][4],))
                    to_add = (c.fetchone()[0],)
                    item_list[x] += to_add
                    conn.commit()
                    conn.close()
                except Exception as e:
                    to_add = ("",)
                    item_list[x] += to_add
                    # print(f'{e}')
            return item_list
        else:
            isearch = f"%{isearch}%"
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            c.execute(f"SELECT item, item_num, item_type, item_brand, location, alt_location_one, alt_location_two, onhand, weight, pallet_qty FROM items WHERE item LIKE ? OR location LIKE ? OR item_num LIKE ? OR item_type LIKE ? ORDER BY loc_id", (isearch, isearch, isearch, isearch))
            item_list = c.fetchall()
            conn.commit()
            conn.close()
            for x in range(len(item_list)):
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                try:
                    c.execute("SELECT loc_zone FROM locations WHERE location=?", (item_list[x][4],))
                    to_add = (c.fetchone()[0],)
                except Exception as e:
                    # print(e)
                    to_add = ('',)
                item_list[x] += to_add
                conn.commit()
                conn.close()
            return item_list

    if itag == 'item':
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE item = ?", (isearch,))
        item_info = c.fetchone()
        conn.commit()
        conn.close()
        return item_info

    if itag == 'weight':
        quantity = int(kwargs['quantity'])
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("SELECT weight, pallet_qty FROM items WHERE item =?", (kwargs['selection'],))
        stuff = c.fetchone()
        conn.commit()
        conn.close()
        try:
            weight = stuff[0] * quantity
            pallet = round(quantity / stuff[1], 2)
            return (weight, pallet)            
        except Exception as e:
            messagebox.showerror(title='Error', message=f'{e}')
            return

    if itype != 0:
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        list = c.execute("SELECT item FROM items WHERE item_type=? ORDER BY item_brand", (itype,))
        new_list = list.fetchall()
        return_list = ()
        for item in new_list:
            if item[0] != 'n/a' and item[0] not in return_list:
                return_list += (item[0],)
        conn.close()
        return return_list

    if itag != 0:
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        list = c.execute("SELECT item FROM items WHERE item_brand=? ORDER BY item", (itag,))
        new_list = list.fetchall()
        return_list = ()
        for item in new_list:
            if item[0] != 'n/a' and item[0] not in return_list:
                return_list += (item[0],)
        conn.close()
        return return_list

    if isearch != 0:
        if isearch == "":
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            list = c.execute("SELECT item FROM items ORDER BY item")
            new_list = list.fetchall()
            return_list = ()
            for item in new_list:
                if item[0] != 'n/a' and item[0] not in return_list:
                    return_list += (item[0],)
            conn.close()
            return return_list
        else:
            e = f"%{isearch}%"
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            list = c.execute(f"SELECT item FROM items WHERE item LIKE ? ORDER BY item", (e,))
            new_list = list.fetchall()
            return_list = ()
            for item in new_list:
                if item[0] != 'n/a' and item[0] not in return_list:
                    return_list += (item[0],)
            conn.close()
            return return_list

    if itag == 0 and itype == 0 and isearch == 0:
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        list = c.execute("SELECT item FROM items ORDER BY item_brand")
        new_list = list.fetchall()
        return_list = ()
        for item in new_list:
            if item[0] != 'n/a' and item[0] not in return_list:
                return_list += (item[0],)
        conn.close()
        return return_list


### VERIFY NOTES WORK
#  item_entry, item_num_entry, item_type_entry, item_brand_entry, item_loc_entry, item_zone_entry, item_alt_loc_entry, 
# item_alt_loc_entry_two, item_onhand_entry, item_weight_entry, item_pallet_entry,
def update_item(window, new_info, current_vals, master_info):
    try:
        item_name = new_info[0].get()
        # location_edit_details = ()
        item_num = new_info[1].get()
        item_type = new_info[2].get().upper()
        item_brand = new_info[3].get().upper()
        item_location = new_info[4].get().upper()
        item_loc_zone = new_info[5].get()
        item_alt_location = new_info[6].get().upper()
        item_alt_location_two = new_info[7].get().upper()
        item_on_hand = new_info[8].get()
        item_weight = new_info[9].get()
        item_full_pallet = new_info[10].get()
        current_values = current_vals
        print(f'current values: \n{current_values}')
    except Exception as e:
        messagebox.showwarning(title="Error", message=f"{e}")
        return
    # today = date.today()


    ### CHECK ENTRY VALIDITY
    ## CHECK LOCATION VALIDITY
    # MAIN LOCATION
    if item_location != "" and item_location != "n/a":
        try:
            location_id = warehouse_inquiry(tag='loc_id', mode='s', location=item_location)
            # location_id = get_location_id(location=item_location)
            new_main_location_info = warehouse_inquiry(tag='loc_info', location=item_location, item='')
        except Exception as e:
            messagebox.showwarning(title="Error", message=f"Invalid Location: {item_location}")
            print(e)
            window.destroy()
            return

    # ALT LOCATION ONE
            # alt_location_one_info = warehouse_inquiry(tag='loc_info', location=item_alt_location, item='')
            # print(alt_location_one_info)
    if item_alt_location != "" and item_alt_location != "n/a":
        try:
            alt_location_one_info = warehouse_inquiry(tag='loc_info', location=item_alt_location, item='')
            if alt_location_one_info == None:
                messagebox.showwarning(title="Error", message=f"Invalid Location: {item_alt_location}")
                return    
        except Exception as e:
            messagebox.showwarning(title="Error", message=f"Invalid Location: {item_alt_location}")
            window.destroy()
            return
    else:
        alt_location_one_info = None
    # ALT LOCATION TWO
    if item_alt_location_two != "" and item_alt_location_two != "n/a":
        try:
            alt_location_two_info = warehouse_inquiry(tag='loc_info', location=item_alt_location_two, item='')
            if alt_location_two_info == None:
                messagebox.showwarning(title="Error", message=f"Invalid Location: {item_alt_location_two}")            
                return
        except Exception as e:
            messagebox.showwarning(title="Error", message=f"Invalid Location: {item_alt_location_two}")
            window.destroy()
            return
    else:
        alt_location_two_info = None

    ## CHECK QTY/WEIGHT/PALLET INFO FOR VALIDITY
    numerical_val_check = [item_on_hand, item_weight, item_full_pallet]
    for value in numerical_val_check:
        try:
            value = int(value)
        except Exception as e:
            messagebox.showwarning(title="Error", message=f"Invalid Qauntity: {value}")
            window.destroy()
            return
        if value < 0:
            messagebox.showwarning(title="Error", message=f"Invalid Qauntity: {value}")
            window.destroy()
            return        
    item_weight = int(item_weight)
    item_on_hand = int(item_on_hand)
    item_full_pallet = int(item_full_pallet)

    ## CHECK TYPE VALIDITY
    # type_list = ["OUTDOOR", "INDOOR", "LINE", "PART"]
    type_list = warehouse_inquiry(tag='type')     
    if item_type not in type_list:
        messagebox.showwarning(title="Error", message=f"Invalid type: {item_type}\nMust be one of \n{type_list}")
        window.destroy()
        return

    ## CHECK BRAND VALIDITY
    # brand_list = ["MULTI", "MULTIU", "3VIR", "VIR", "VIRU", "FLEXX", "LIVV", "BRS", "MBRS", "FLR", "CAS", "DUCT", "CONS", "LIVS", "LIVV", "UMAT", "SAP", "LS", "OTHER"]
    brand_list = warehouse_inquiry(tag='brand')
    if item_brand not in brand_list:
        messagebox.showwarning(title="Error", message=f"Invalid brand: {item_brand}")
        window.destroy()
        return        

    ## CHECK FOR NO CHANGE
    new_item_info = (item_name, item_num, item_type, item_brand, item_location, location_id, item_alt_location, item_alt_location_two, item_weight, item_on_hand, item_full_pallet)
    current_item_info = warehouse_inquiry(tag='item', search=item_name)
    current_alt_location_one = current_item_info[6]
    current_alt_location_two = current_item_info[7]
    # print(f"Item Edit Details - \n{type(new_item_info)} \n{new_item_info} \nItem Current Info - \n{type(current_item_info)} \n{current_item_info[:-2]}")
    if new_item_info == current_item_info[:-2]:
        messagebox.showwarning(title="Error", message=f"No Changes Needed")
        window.destroy()
        return
    # return
    new_locations = [item_location, item_alt_location, item_alt_location_two]
    old_locations = [current_values[4], current_values[6], current_values[7]]
    # print(f'new locations \n{new_locations} \n----\nold locations \n{old_locations}')

    ### UPDATE ITEMS TABLE    
    if item_alt_location == item_location:
        item_alt_location = ''
    if item_alt_location_two == item_location:
        item_alt_location_two = ''

    try:
        item_edit_details = (item_num, item_type, item_brand, item_location, location_id, item_alt_location, item_alt_location_two, item_on_hand, item_weight, item_full_pallet, item_name)
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("""UPDATE items SET item_num = ?, 
                                    item_type = ?,
                                    item_brand = ?,
                                    location = ?,
                                    loc_id = ?,
                                    alt_location_one = ?,
                                    alt_location_two = ?,
                                    onhand = ?,
                                    weight = ?,
                                    pallet_qty = ? WHERE item = ?""", item_edit_details)
        conn.commit()
        conn.close()
        add_note(note_type='item', user=master_info, mode='edit', old_info=current_item_info)
    except Exception as e:
        print(e)
        return
    # UPDATE NEW LOCATIONS
    for x in range(len(new_locations)):
        if new_locations[x] != '' and new_locations[x] != 'n/a' and new_locations[x] not in old_locations:
            print('doing something')
            print(f'adding item to location {new_locations[x]}')
            #get info for location x, insert item into location
            temp_location_info = warehouse_inquiry(tag='loc_info', location=new_locations[x], item='')
            if temp_location_info[4] == '':
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                c.execute("UPDATE locations SET item = ? where location = ?", (item_name, new_locations[x]))
                conn.commit()
                conn.close()
            elif temp_location_info[5] == '':
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                c.execute("UPDATE locations SET alt_item_one = ? where location = ?", (item_name, new_locations[x]))
                conn.commit()
                conn.close()
            elif temp_location_info[6] == '':
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                c.execute("UPDATE locations SET alt_item_two = ? where location = ?", (item_name, new_locations[x]))
                conn.commit()
                conn.close()
            else:
                messagebox.showwarning(title="Warning", message=f"New location full, did not update Locations Table.")
            add_note(note_type='loc', user=master_info, mode='edit', old_info=temp_location_info)
        # if new_locations[x] == '' or new_locations[x] == 'n/a':
        #     continue
        #     # print('no location to add to')
        # elif new_locations[x] in old_locations:
        #     continue
        #     # print(f'item already in location {new_locations[x]}')
        # else:
        #     print(f'adding item to location {new_locations[x]}')
        #     #get info for location x, insert item into location
        #     temp_location_info = warehouse_inquiry(tag='loc_info', location=new_locations[x], item='')
        #     if temp_location_info[4] == '':
        #         conn = sqlite3.connect(warehouse)
        #         c = conn.cursor()
        #         c.execute("UPDATE locations SET item = ? where location = ?", (item_name, new_locations[x]))
        #         conn.commit()
        #         conn.close()
        #     elif temp_location_info[5] == '':
        #         conn = sqlite3.connect(warehouse)
        #         c = conn.cursor()
        #         c.execute("UPDATE locations SET alt_item_one = ? where location = ?", (item_name, new_locations[x]))
        #         conn.commit()
        #         conn.close()
        #     elif temp_location_info[6] == '':
        #         conn = sqlite3.connect(warehouse)
        #         c = conn.cursor()
        #         c.execute("UPDATE locations SET alt_item_two = ? where location = ?", (item_name, new_locations[x]))
        #         conn.commit()
        #         conn.close()
        #     else:
        #         messagebox.showwarning(title="Warning", message=f"New location full, did not update Locations Table.")
        #     add_note(note_type='loc', user=master_info, mode='edit', old_info=temp_location_info)

    # UPDATE OLD LOCATIONS
    for x in range(len(old_locations)):
        if old_locations[x] != '' and old_locations[x] not in new_locations:
            temp_location_info = warehouse_inquiry(tag='loc_info', location=old_locations[x], item='')
            if temp_location_info[4] == item_name:
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                c.execute("""UPDATE locations SET item = ?,
                                                item_stock = ?,
                                                alt_item_one = ?,
                                                alt_item_one_stock = ?,
                                                alt_item_two = ?,
                                                alt_item_two_stock = ? WHERE location = ?""", (temp_location_info[5],
                                                                                               temp_location_info[8],
                                                                                               temp_location_info[6],
                                                                                               temp_location_info[9],
                                                                                               '',
                                                                                               0,
                                                                                               old_locations[x]))
                conn.commit()
                conn.close()
            elif temp_location_info[5] == item_name:
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                c.execute("""UPDATE locations SET alt_item_one = ?,
                                                alt_item_one_stock = ?,
                                                alt_item_two = ?,
                                                alt_item_two_stock = ? WHERE location = ?""", (temp_location_info[6],
                                                                                               temp_location_info[9],
                                                                                               '',
                                                                                               0,
                                                                                               old_locations[x]))
                conn.commit()
                conn.close()      
            elif temp_location_info[6] == item_name:
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                c.execute("""UPDATE locations SET alt_item_two = ?, alt_item_two_stock = ? WHERE location = ?""", ('', 0, old_locations[x]))
                conn.commit()
                conn.close()
            add_note(note_type='loc', user=master_info, mode='edit', old_info=temp_location_info)      

    window.destroy()
    return   
    

### ADD NOTES FOR ADD ITEM AND UPDATE LOCATIONS
def add_item_to_database(box, item, inum, itype, ibrand, iloc, iweight, ipallet, master_info):
    try:    
        new_item = item.get().upper()
        new_item_num = inum.get().upper()
        new_item_type = itype.get().upper()
        new_item_brand = ibrand.get().upper()
        new_item_location = iloc.get().upper()
        new_item_weight = iweight.get()
        new_item_full_pallet = ipallet.get()
    except Exception as e:
        messagebox.showwarning(title="Error", message=f"{e}")
        return
    
    item_list = warehouse_inquiry()
    if new_item in item_list:
        messagebox.showwarning(title="Error", message=f"Item Already in Database")
        return

    if new_item == '':
        messagebox.showwarning(title="Error", message=f"No Item Entered")
        return    

    if new_item_num == '':
        messagebox.showwarning(title="Error", message=f"No Item Number Entered")
        return

    new_item_loc_id = 500

    types = warehouse_inquiry(tag='type')
    brands = warehouse_inquiry(tag='brand')

    if new_item_type not in types:
        type_check = messagebox.askyesno(title="Warning", message=f"Item Type not in Database.  Confirm {new_item_type}")
        if not type_check:
            return

    if new_item_brand not in brands:
        brand_check = messagebox.askyesno(title="Warning", message=f"Item Brand not in Database.  Confirm {new_item_brand}")
        if not brand_check:
            return

    try:
        new_item_weight = int(new_item_weight)
        new_item_full_pallet = int(new_item_full_pallet)
    except Exception as e:
        messagebox.showwarning(title="Error", message=f"{e}")
        return
    
    if new_item_weight <= 0 or new_item_full_pallet <= 0:
        messagebox.showwarning(title="Error", message=f"Weight and Full Pallet must be Positive Integers")
        return

    ### UPDATE DATABASE TABLES


    ## LOCATIONS UPDATE
    if new_item_location != '':
        location_info = warehouse_inquiry(tag='loc_info', location=new_item_location, item='')
        print(location_info)
        if location_info == None:
            messagebox.showwarning(title="Error", message=f"Invalid Location")
            return
        if location_info[4] == '' or location_info[4] == 'n/a':
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            c.execute("UPDATE locations SET item = ? WHERE location = ?", (new_item, new_item_location))
            conn.commit()
            conn.close()
        elif location_info[5] == '' or location_info[5] == 'n/a':
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            c.execute("UPDATE locations SET alt_item_one = ? WHERE location = ?", (new_item, new_item_location))
            conn.commit()
            conn.close()
        elif location_info[6] == '' or location_info[6] == 'n/a':
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            c.execute("UPDATE locations SET alt_item_two = ? WHERE location = ?", (new_item, new_item_location))
            conn.commit()
            conn.close()
        else:
            messagebox.showwarning(title="Error", message=f"Location Full.  Did not update Locations Table")
        add_note(note_type='loc', user=master_info, mode='edit', old_info=location_info)
        new_item_loc_id = location_info[0] 
    
    ## UPDATE ITEMS TABLE
    new_item_info = (new_item, new_item_num, new_item_location, new_item_loc_id, new_item_type, new_item_brand, new_item_weight, new_item_full_pallet)
    conn = sqlite3.connect(warehouse)
    c = conn.cursor()
    c.execute('INSERT INTO items (item, item_num, location, loc_id, item_type, item_brand, weight, pallet_qty) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', new_item_info)
    conn.commit()
    conn.close()
    add_note(note_type='item', user=master_info, mode='add', item=new_item_info)

    print(f'{new_item} added to database')
    box.destroy()


### NEED TO PROPERLY ADD NOTES FOR EACH LOCATION EDIT
def update_location_database(master_info='', box='', location_info='', primary_vars='', mode='', edit_list='', **kwargs):
    if mode == 'cc':
        print(f'updating {location_info}')
        new_info = (primary_vars[0], primary_vars[1], primary_vars[2], location_info)
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("UPDATE locations SET item_stock = ?, alt_item_one_stock = ?, alt_item_two_stock = ? WHERE location = ?", new_info)
        conn.commit()
        conn.close()
        print(f'finished updating {location_info}')
        add_note(note_type='loc', user=master_info, mode='edit', old_info=location_info)
        return
    
    if mode == 'edit':
        loc_box = box
        loc = location_info[0].get()
        loc_zone = location_info[1].get()
        new_utn = location_info[2].get()
        new_item = location_info[3].get().upper()
        new_item_qty = location_info[4].get()
        new_item_primary = primary_vars[0].get()
        new_alt_item_one = location_info[5].get().upper()
        new_alt_item_one_qty = location_info[6].get()
        new_alt_item_one_primary = primary_vars[1].get()
        new_alt_item_two = location_info[7].get().upper()
        new_alt_item_two_qty = location_info[8].get()
        new_alt_item_two_primary = primary_vars[2].get()
        # today = date.today()
        
        if new_alt_item_one == new_item:
            new_alt_item_one = ''
            new_alt_item_one_qty = 0
        if new_alt_item_two == new_item:
            new_alt_item_two = ''
            new_alt_item_two_qty = 0
        

        ### CHECK INVENTORY FOR NEW ITEM VALIDITY
        item_list = warehouse_inquiry()
        new_item_list = [new_item, new_alt_item_one, new_alt_item_two]
        item_primary_check = [new_item_primary, new_alt_item_one_primary, new_alt_item_two_primary]
        for item in new_item_list:
            if item not in item_list and item != "" and item != "n/a":
                messagebox.showwarning(title="Error", message=f"Invalid Item: {item}")
                return

        ### CHECK QTY VALS FOR VALIDITY
        qauntity_val_check = [new_item_qty, new_alt_item_one_qty, new_alt_item_two_qty]
        for qty in qauntity_val_check:
            try:
                qty = int(qty)
            except Exception as e:
                messagebox.showwarning(title="Error", message="Invalid Qauntity")
                return
            if qty < 0:
                messagebox.showwarning(title="Error", message="Invalid Qauntity")
                return

        current_location_info = warehouse_inquiry(tag='loc_info', location=loc, item='')
        current_items = [current_location_info[4], current_location_info[5], current_location_info[6]]
        current_location_item_info = warehouse_inquiry(tag='item', search=current_location_info[4])
        print(f'item info--- \n{current_location_item_info}')

        if current_items == new_item_list:
            print('Same Items')
        
        ### CHECK IF NO CHANGE
        check_one = current_location_info[3:10]
        check_two = (new_utn, new_item, new_alt_item_one, new_alt_item_two, int(new_item_qty), int(new_alt_item_one_qty), int(new_alt_item_two_qty))
        if check_one == check_two:
            print("no change")
            return
        
        ### UPDATE LOCATIONS TABLE
        location_update_details = (new_utn, new_item, new_alt_item_one, new_alt_item_two, new_item_qty, new_alt_item_one_qty, new_alt_item_two_qty, loc)
        
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("""UPDATE locations SET loc_utn = ?, 
                                        item = ?,
                                        alt_item_one = ?,
                                        alt_item_two = ?,
                                        item_stock = ?,
                                        alt_item_one_stock = ?,
                                        alt_item_two_stock = ? WHERE location = ?""", location_update_details)
        # add_note(note_type='loc', user=master_info, mode='edit', old_info=current_location_info)
        ### UPDATE ITEMS TABLE
        # if current_items != new_item_list:
        ### UPDATING NEW ITEMS
        for item in range(len(new_item_list)):
            if new_item_list[item] != "" and new_item_list[item] != "n/a" and new_item_list[item] not in current_items:
                # IF LOCATION IS PRIMARY
                temp_item_info = warehouse_inquiry(tag='item', search=new_item_list[item])
                if item_primary_check[item] == 1:
                    if temp_item_info[4] != loc:
                        # item_notes = new_location_item_info[12] + f"""{today} LOCATION CHANGE 
                        # primary {new_location_item_info[4]} to {loc}
                        # alt loc {new_location_item_info[6]} to {new_location_item_info[4]}
                        # alt loc 2 {new_location_item_info[7]} to {new_location_item_info[6]} - """
                        new_primary_vals = (loc, current_location_info[0], temp_item_info[4], temp_item_info[6], new_item_list[item])
                        c.execute("""UPDATE items SET location = ?, loc_id = ?, alt_location_one = ?, alt_location_two = ?, WHERE item = ?""", new_primary_vals)
                # IF LOCATION IS NOT PRIMARY
                else:
                    print(temp_item_info)
                    # IF NO MAIN LOCATION
                    if temp_item_info[4] == '' or temp_item_info[4] == 'n/a' and temp_item_info[4] != loc:
                        c.execute("UPDATE items SET location = ?, loc_id = ? where item = ?", (loc, current_location_info[0], new_item_list[item]))
                    # IF NO ALT LOCATION ONE
                    elif temp_item_info[6] == '' or temp_item_info[6] == 'n/a' and temp_item_info[6] != loc:
                        c.execute("UPDATE items SET alt_location_one = ? where item = ?", (loc, new_item_list[item]))
                    # IF NO ALT LOCATION TWO
                    elif temp_item_info[7] == '' or temp_item_info[7] == 'n/a' and temp_item_info[7] != loc:
                        c.execute("UPDATE items SET alt_location_two = ? where item = ?", (loc, new_item_list[item]))
                    # IF ITEM LOCATIONS ARE FULL
                    else:
                        messagebox.showwarning(title="Error", message="Item Data full, did not update Item Database")

        ### UPDATING OLD ITEMS
        for item in current_items:
            if item != '' and item != 'n/a' and item not in new_item_list:
                temp_item_info = warehouse_inquiry(tag='item', search=item)
                if not temp_item_info:
                    continue
                if temp_item_info[4] == loc:
                    if temp_item_info[6] != '' and temp_item_info[6] != 'n/a':
                        new_loc_id = warehouse_inquiry(tag='loc_id', mode='s', location=temp_item_info[6])
                        # new_loc_id = get_location_id(temp_item_info[6])
                        c.execute("UPDATE items SET location = ?, loc_id = ?, alt_location_one = ?, alt_location_two = ? WHERE item = ?", (temp_item_info[6], new_loc_id, temp_item_info[7], '', item))
                    elif temp_item_info[7] != '' and temp_item_info[7] != 'n/a':
                        new_loc_id = warehouse_inquiry(tag='loc_id', mode='s', location=temp_item_info[7])
                        # new_loc_id = get_location_id(temp_item_info[7])
                        c.execute("UPDATE items SET location = ?, loc_id = ?, alt_location_two = ? WHERE item = ?", (temp_item_info[7], new_loc_id, '', item))
                    else:
                        c.execute("UPDATE items SET location = ?, loc_id = ?, alt_location_one = ?, alt_location_two = ? WHERE item = ?", ('', '', '', '', item))
                elif temp_item_info[6] == loc:
                    if temp_item_info[7] != '' and temp_item_info[7] != 'n/a':
                        c.execute("UPDATE items SET alt_location_one = ?, alt_location_two = ? WHERE item = ?", (temp_item_info[7], '', item))
                    else:
                        c.execute("UPDATE items SET alt_location_one = ?, alt_location_two = ? WHERE item = ?", ('', '', item))
                elif temp_item_info[7] == loc:
                    c.execute("UPDATE items SET alt_location_two = ? WHERE item = ?", ('', item))
                else:
                    messagebox.showwarning(title="Error", message="Data Error, did not update Items Database")
        conn.commit()
        conn.close()                    
        add_note(note_type='loc', user=master_info, mode='edit', old_info=current_location_info)
        loc_box.destroy()
        return

    if mode == 'add':
        new_location = location_info[0]
        new_zone = location_info[1]
        new_utn = location_info[2]
        list_pos = location_info[3]
        
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        if list_pos == 'last':
            loc_edit_list = edit_list
            new_loc_id = loc_edit_list[0][0] + 1
            add_location = (new_loc_id, new_location, new_utn, new_zone)
            c.execute("INSERT INTO locations (loc_id, location, loc_utn, loc_zone) VALUES (?, ?, ?, ?)", add_location)
        else:
            loc_edit_list = edit_list[1:]
            rev_loc_edit_list = loc_edit_list[::-1]
            new_loc_id = loc_edit_list[0][0]
            add_location = (new_loc_id, new_location, new_utn, new_zone, new_item)
            # SHIFT LOCATION ID's
            for loc in rev_loc_edit_list:
                new_id = loc[0] + 1
                move_location = loc[1]
                c.execute("UPDATE locations SET loc_id = ? WHERE location = ?", (new_id, move_location))
            # ADD NEW LOCATION
            add_location = (new_loc_id, new_location, new_utn, new_zone)
            c.execute("INSERT INTO locations (loc_id, location, loc_utn, loc_zone) VALUES (?, ?, ?, ?)", add_location)
        add_note(note_type='loc', user=master_info, mode='add', location_info=add_location)

        conn.commit()
        conn.close()

    if mode == 'remove':
        to_remove = location_info[0]
        temp_loc_info = warehouse_inquiry(tag='loc_info', location=to_remove[1], item='')
        items = [primary_vars[1], primary_vars[2], primary_vars[3]]
        to_edit = location_info[1:]
        list_pos = kwargs['list_pos']

        # DELETE LOCATION
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("DELETE FROM locations WHERE location = ?", (to_remove[1],))
        conn.commit()
        conn.close()

        add_note(note_type='loc', user=master_info, mode='del', location=to_remove[1])
        # SHIT LOCATION ID's
        if list_pos != 'last':
            conn = sqlite3.connect(warehouse)
            c = conn.cursor()
            for loc in to_edit:
                new_id = loc[0] - 1
                c.execute("UPDATE locations SET loc_id = ? WHERE location = ?", (new_id, loc[1]))    
            conn.commit()
            conn.close()    

        # REMOVE LOCATION FROM ITEMS
        # REPEAT FOR EACH ITEM IN LOCATION
        for item in items:
            if item != '' and item != 'n/a':
                conn = sqlite3.connect(warehouse)
                c = conn.cursor()
                item_info = warehouse_inquiry(tag='item', search=item)
                print(f'item info {item_info}')
                # IF DELETED LOCATION IS PRIMARY LOCATION
                if item_info[4] == to_remove[1]:
                    if item_info[6] != '' and item_info[6] != 'n/a':
                        new_id = warehouse_inquiry(tag='loc_id', mode='s', location=item_info[6])
                        # new_id = get_location_id(item_info[6])
                        c.execute("UPDATE items SET location = ?, alt_location_one = ?, alt_location_two = ?, loc_id = ? WHERE item = ?", (item_info[6], item_info[7], '', new_id, item))
                    elif item_info[7] != '' and item_info[7] != 'n/a':
                        new_id = warehouse_inquiry(tag='loc_id', mode='s', location=item_info[7])
                        # new_id = get_location_id(item_info[7])
                        c.execute("UPDATE items SET location = ?, alt_location_one = ?, alt_location_two = ?, loc_id = ? WHERE item = ?", (item_info[7], '', '', new_id, item))                   
                    # IF NO LOCATIONS, SET LOC_ID TO 500
                    else:
                        new_id = 500
                        c.execute("UPDATE items SET location = ?, alt_location_one = ?, alt_location_two = ?, loc_id = ? WHERE item = ?", ('', '', '', new_id, item))                   
                # IF DELETED LOCATION IS ALT_LOCATION_ONE
                elif item_info[6] == to_remove[1]:
                    c.execute("UPDATE items SET alt_location_one = ?, alt_location_two = ? WHERE item = ?", (item_info[7], '', item))
                # IF DELETED LOCATION IS ALT_LOCATION_TWO
                elif item_info[7] == to_remove[1]:
                    c.execute("UPDATE items SET alt_location_two = ? WHERE item = ?", ('', item))
                else:
                    messagebox.showwarning(title='Warning', message=f'Location not listed in Items Database for {item}.  Items Database not updated.')
                    conn.commit()
                    conn.close()
                    return
                conn.commit()
                conn.close()
                add_note(note_type='item', user=master_info, mode='edit', old_info=item_info)
        return


###
def update_quantities(xitem='', master_info=''):
    if xitem == '':
        print('updating all items')
        item_list = warehouse_inquiry()
    else:
        print('updating single item')
        item_list = warehouse_inquiry(search=xitem)
    for item in item_list:
        new_onhand = 0
        item_name = item
        old_info = warehouse_inquiry(tag='item', search=item_name)
        item_loc_info_list = warehouse_inquiry(tag='loc_info', location='', item=item_name)
        if len(item_loc_info_list) == 1:
            item_loc_info = item_loc_info_list[0]
            if item_loc_info[2] == item_name:
                new_onhand += item_loc_info[5]
            if item_loc_info[3] == item_name:
                new_onhand += item_loc_info[6]
            if item_loc_info[4] == item_name:
                new_onhand += item_loc_info[7]
        if len(item_loc_info_list) > 1:
            for item_loc_info in item_loc_info_list:
                if item_loc_info[2] == item_name:
                    new_onhand += item_loc_info[5]
                if item_loc_info[3] == item_name:
                    new_onhand += item_loc_info[6]
                if item_loc_info[4] == item_name:
                    new_onhand += item_loc_info[7]
        conn = sqlite3.connect(warehouse)
        c = conn.cursor()
        c.execute("UPDATE items SET onhand = ? WHERE item = ?", (new_onhand, item_name))
        conn.commit()
        conn.close()
        add_note(note_type='item', user=master_info, mode='edit', old_info=old_info)
    print('update complete')


def add_note(note_type, user, mode='', **kwargs):
    today = datetime.now()
    note_user = user[5]
    conn = sqlite3.connect(warehouse,
                           detect_types=sqlite3.PARSE_DECLTYPES |
                                        sqlite3.PARSE_COLNAMES)
    c = conn.cursor()
    
    xint = randint(10000, 99999)
    
    c.execute("SELECT DISTINCT log_id FROM notes")
    log_ids = c.fetchall()
    if len(log_ids) != 0:
        if xint in log_ids[0]:
            while xint in log_ids[0]:
                xint = randint(10000, 99999)

    ### RESET WAREHOUSE ###
    if note_type == 'war_reset':
        message = 'Warehouse Inventory Reset'
        new_log = (today, note_user, note_type, 'all', 'all', message, xint)
        c.execute("INSERT INTO notes (date, user, type, item, location, log, log_id) VALUES (?, ?, ?, ?, ?, ?, ?)", new_log)
        conn.commit()
        conn.close()
        return

    ### SAVE NEW ORDER ###       -DONE-
    if note_type == 'order_create':
        order_box = kwargs['box']
        order_num = kwargs['order_num']
        if order_num == '':
            messagebox.showerror(title='Error', message='Order Number is required to Save Order')
            order_box.destroy()
            return
        item_notes = kwargs['item_notes']
        notes = kwargs['notes']
        ### UPDATE ORDERLOG DB ###
        new_log = (today, note_user, order_num, item_notes, notes)
        c.execute("INSERT INTO orderlog (date, user, order_num, order_items, order_notes) VALUES (?, ?, ?, ?, ?)", new_log)
        ### UPDATE NOTES DB PER ITEM ###
        item_list = kwargs["item_list"]
        for item in item_list:
            message = f"x{item[1]} added to {order_num}"
            new_note = (today, note_user, 'order', item[0], message, xint)
            c.execute("INSERT INTO notes (date, user, type, item, log, log_id) VALUES (?, ?, ?, ?, ?, ?)", new_note)
        conn.commit()
        conn.close()
        order_box.destroy()
        print('databases updated successfully')
        return
    
    ### UPDATING USER INFO ###   -DONE- 
    if note_type == 'user':
        ### EDIT CURRENT INFO ###
        if mode == 'edit':
            old_info = kwargs['cur_info']
            new_info = kwargs['new_info']
            if old_info == new_info:
                print('no changes')
                return
            new_data = []
            change_col = ['username', 'email', 'user_id', 'name_full', 'name_nick', 'branch', 'status']
            # c.execute("INSERT INTO notes (date, user, type, log, log_id) VALUES (?, ?, ?, ?, ?)", new_note)
            for x in range(len(old_info)):
                if old_info[x] != new_info[x]:
                    new_message = f'{change_col[x]} CHANGE FROM {old_info[x]} TO {new_info[x]}'
                    new_note = (today, note_user, note_type, new_message, xint)
                    new_data.append(new_note)
            c.executemany("INSERT INTO notes (date, user, type, log, log_id) VALUES (?, ?, ?, ?, ?)", new_data)
            conn.commit()
            conn.close()
            print('note added')
            return
        
        ### ADD NEW UDER ###
        if mode == 'add':
            new_user_info = kwargs['new_info']
            new_data = [(today, note_user, note_type, f"ADD USER", xint),
                        (today, note_user, note_type, f"USERNAME {new_user_info[0]}", xint),
                        (today, note_user, note_type, f"EMAIL {new_user_info[1]}", xint),
                        (today, note_user, note_type, f"USERID {new_user_info[2]}", xint),
                        (today, note_user, note_type, f"FULLNAME {new_user_info[3]}", xint),
                        (today, note_user, note_type, f"NICKNAME {new_user_info[4]}", xint),
                        (today, note_user, note_type, f"BRANCH {new_user_info[5]}", xint),
                        (today, note_user, note_type, f"STATUS {new_user_info[6]}", xint)]
            c.executemany("INSERT INTO notes (date, user, type, log, log_id) VALUES (?, ?, ?, ?, ?)", new_data)
            conn.commit()
            conn.close()
            print('note added')
            return
        
        ### DELETE USER ###
        if mode == 'del':
            del_info = kwargs['del_info']
            new_message = f"""USERNAME {del_info[0]} REMOVED FROM DATABASE"""
            new_note = (today, note_user, note_type, new_message, xint)
            c.execute("INSERT INTO notes (date, user,  type, log, log_id) VALUES (?, ?, ?, ?, ?)", new_note)
            conn.commit()
            conn.close()
            print('note added')
            return

    ### UPDATE ITEM CHANGES ###
    if note_type == 'item':
        ### EDIT EXISTING ITEM ###
        if mode == 'edit':
            old_info = kwargs['old_info'][:-1]
            new_info = warehouse_inquiry(tag='item', search=old_info[0])[:-1]
            if old_info == new_info:
                print('no changes')
                conn.commit()
                conn.close()
                return
            change_col = ['item', 'item_num', 'item_type', 'item_brand', 'location', 'loc_id', 'alt_location_one', 'alt_location_two', 'weight', 'onhand', 'pallet_qty']
            new_data = []
            # new_message = f'EDIT ITEM {old_info[0]}'
            # new_note = (today, note_user, note_type, old_info[0], new_message, xint)
            # c.execute("INSERT INTO notes (date, user, type, item, log, log_id) VALUES (?, ?, ?, ?, ?, ?)", new_note)
            for x in range(len(old_info)):
                if old_info[x] != new_info[x]:
                    new_message = f'{change_col[x]} CHANGED FROM {old_info[x]} TO {new_info[x]}'
                    new_note = (today, note_user, note_type, old_info[0], new_message, xint)
                    new_data.append(new_note)                    
                    # c.execute("INSERT INTO notes (date, user, type, item, log, log_id) VALUES (?, ?, ?, ?, ?, ?)", new_note)                    
            c.executemany("INSERT INTO notes (date, user, type, item, log, log_id) VALUES (?, ?, ?, ?, ?, ?)", new_data)
            # new_note = (today, note_user, note_type, old_info[0], new_message)                    
            # c.execute("INSERT INTO notes (date, user, type, item, log) VALUES (?, ?, ?, ?, ?)", new_note)
            conn.commit()
            conn.close()
            print('note added')
            return
        ### ADD NEW ITEM ###
        if mode == 'add':
            item = kwargs['item']
            new_data = [(today, note_user, note_type, item[0], f'ADD ITEM {item[0]}', xint),
                        (today, note_user, note_type, item[0], f'item number {item[1]}', xint),
                        (today, note_user, note_type, item[0], f'location {item[2]}', xint),
                        (today, note_user, note_type, item[0], f'type {item[4]}', xint),
                        (today, note_user, note_type, item[0], f'brand {item[5]}', xint),
                        (today, note_user, note_type, item[0], f'weight {item[6]}', xint),
                        (today, note_user, note_type, item[0], f'full pallet {item[7]}', xint)]
            c.executemany("INSERT INTO notes (date, user, type, item, log, log_id) VALUES (?, ?, ?, ?, ?, ?)", new_data)
            conn.commit()
            conn.close()
            print('note added')
            return
        ### REMOVE ITEM ###
        if mode == 'del':
            item = kwargs['item']
            new_message = f"""{item} REMOVED FROM DATABASE"""
            new_note = (today, user, note_type, item, new_message, xint)
            c.execute("INSERT INTO notes (date, user,  type, item, log, log_id) VALUES (?, ?, ?, ?, ?, ?)", new_note)
            conn.commit()
            conn.close()
            print('note added')
            return

    ### UPDATE LOCATION CHANGES ###
    if note_type == 'loc':
        ### EDIT EXISTING LOCATION ###
        if mode == 'edit':
            old_info = kwargs['old_info'][:-1]
            new_info = warehouse_inquiry(tag='loc_info', location=old_info[1], item='')[:-1]
            print(f'old - {old_info}')
            print(f'new - {new_info}')
            change_col = ['loc_id', 'location', 'loc_zone', 'loc_utn', 'item', 'alt_item_one', 'alt_item_two', 'item_stock', 'alt_item_one_stock', 'alt_item_two_stock']
            # new_message = f'LOCATION EDIT {old_info[1]}'
            change_count = 0
            new_data = []
            # new_note = (today, note_user, note_type, old_info[1], new_message, xint)
            # c.execute("INSERT INTO notes (date, user, type, location, log, log_id) VALUES (?, ?, ?, ?, ?, ?)", new_note)
            for x in range(len(old_info)):
                if old_info[x] != new_info[x]:
                    new_message = f'{change_col[x]} CHANGED FROM {old_info[x]} TO {new_info[x]}'
                    new_note = (today, note_user, note_type, old_info[1], new_message, xint)
                    new_data.append(new_note)
                    # c.execute("INSERT INTO notes (date, user, type, location, log, log_id) VALUES (?, ?, ?, ?, ?, ?)", new_note)
                    change_count += 1
                    if x > 3 and x < 7 and old_info[x] not in new_info:
                        # UPDATE LOC_HISTORY
                        c.execute("SELECT loc_history FROM locations WHERE location = ?", (old_info[1],))
                        temp_loc_message = c.fetchone()[0]
                        if temp_loc_message == '' or temp_loc_message == 'n/a':
                            new_loc_history = f'{new_info[x]}'
                            c.execute("UPDATE locations SET loc_history = ? WHERE location = ?", (new_loc_history, old_info[1]))
                        else:
                            temp_loc_list = temp_loc_message.split(' ')
                            update_history = False
                            if old_info[x] not in temp_loc_list:
                                new_loc_history = temp_loc_message + f' {new_info[x]}'
                                update_history = True
                            temp_loc_list = temp_loc_message.split(' ')
                            if new_info[x] not in temp_loc_list:
                                new_loc_history = temp_loc_message + f' {new_info[x]}'
                                update_history = True
                            if update_history:
                                c.execute("UPDATE locations SET loc_history = ? WHERE location = ?", (new_loc_history, old_info[1]))
                        # UPDATE ITEM_HISTORY
                        c.execute("SELECT item_history FROM items WHERE item = ?", (new_info[x],))
                        print('trouble maybe')
                        print(old_info)
                        print(x)
                        print(old_info[x])
                        try:
                            old_item_history = c.fetchone()[0]
                        except Exception as e:
                            old_item_history = ''
                        #     print(e)
                        # print(f'TEMP TEMP TEMP {temp_temp_temp}')
                        # temp_item_message = temp_temp_temp[0]
                        # print(temp_item_message)
                        # # temp_item_message = c.fetchone()[0]
                        if old_item_history == '':
                            new_item_history = f'{old_info[1]}'
                            c.execute("UPDATE items SET item_history = ? WHERE item = ?", (new_item_history, old_info[x]))
                        else:
                            temp_item_list = old_item_history.split(' ')
                            if old_info[1] not in temp_item_list:
                                new_item_history = old_item_history + f' {old_info[1]}'
                                c.execute("UPDATE items SET item_history = ? WHERE item = ?", (new_item_history, old_info[x]))
            c.executemany("INSERT INTO notes (date, user, type, location, log, log_id) VALUES (?, ?, ?, ?, ?, ?)", new_data)
            conn.commit()
            conn.close()
            print('note added')
            return
        ### ADD LOCATION
        if mode == 'add':
            new_location = kwargs['location_info']
            new_data = [(today, note_user, note_type, new_location[1], f'LOCATION ADD {new_location[1]}', xint),
                        (today, note_user, note_type, new_location[1], f'loc_id {new_location[0]}', xint),
                        (today, note_user, note_type, new_location[1], f'loc_utn {new_location[2]}', xint),
                        (today, note_user, note_type, new_location[1], f'loc_zone {new_location[3]}', xint)]
            c.executemany("INSERT INTO notes (date, user, type, location, log, log_id) VALUES (?, ?, ?, ?, ?, ?)", new_data)
            conn.commit()
            conn.close()
            print('note added')
            return
        ### REMOVE LOCATION ###
        if mode == 'del':
            location = kwargs['location']
            new_message = f"LOCATION REMOVE {location}"
            new_note = (today, note_user, note_type, location, new_message, xint)
            c.execute("INSERT INTO notes (date, user, type, location, log, log_id) VALUES (?, ?, ?, ?, ?, ?)", new_note)
            conn.commit()
            conn.close()
            print('note added')
            return
    conn.commit()
    conn.close()
    return  
    

def note_inquiry(note_type, mode='', **kwargs):
    if note_type == 'all':
        if mode == 'all':
            conn = sqlite3.connect(warehouse,
                                detect_types=sqlite3.PARSE_DECLTYPES |
                                                sqlite3.PARSE_COLNAMES)
            c = conn.cursor()
            c.execute("SELECT * FROM notes")
            temp_list = c.fetchall()
            change_log = temp_list[::-1]
            conn.commit()
            conn.close()
            return change_log 
        
        if mode == 'search':
            temp_search = kwargs['search']
            if temp_search == 'no order':
                conn = sqlite3.connect(warehouse,
                                       detect_types=sqlite3.PARSE_DECLTYPES |
                                                    sqlite3.PARSE_COLNAMES)
                c = conn.cursor()
                c.execute("SELECT * FROM notes WHERE type != ?", ('order',))
                temp_list = c.fetchall()
                change_log = temp_list[::-1]
                conn.commit()
                conn.close()
                return change_log     
            
            if temp_search == 'no item':
                conn = sqlite3.connect(warehouse,
                                       detect_types=sqlite3.PARSE_DECLTYPES |
                                                    sqlite3.PARSE_COLNAMES)
                c = conn.cursor()
                c.execute("SELECT * FROM notes WHERE type != ?", ('item',))
                temp_list = c.fetchall()
                change_log = temp_list[::-1]
                conn.commit()
                conn.close()
                return change_log     

            if temp_search == 'no location' or temp_search == 'no loc':
                conn = sqlite3.connect(warehouse,
                                       detect_types=sqlite3.PARSE_DECLTYPES |
                                                    sqlite3.PARSE_COLNAMES)
                c = conn.cursor()
                c.execute("SELECT * FROM notes WHERE type != ?", ('loc',))
                temp_list = c.fetchall()
                change_log = temp_list[::-1]
                conn.commit()
                conn.close()
                return change_log     
                        
                
            search = f"%{temp_search}%"
            conn = sqlite3.connect(warehouse,
                                   detect_types=sqlite3.PARSE_DECLTYPES |
                                                sqlite3.PARSE_COLNAMES)
            c = conn.cursor()
            c.execute("SELECT * FROM notes WHERE user LIKE ? OR type LIKE ? OR item LIKE ? OR location LIKE ? OR log_id LIKE ?", (search, search, search, search, search))
            temp_list = c.fetchall()
            change_log = temp_list[::-1]
            conn.commit()
            conn.close()
            return change_log            
        
    
    if note_type == 'order':
        if mode == '':
            conn = sqlite3.connect(warehouse,
                                detect_types=sqlite3.PARSE_DECLTYPES |
                                                sqlite3.PARSE_COLNAMES)
            c = conn.cursor()
            c.execute("SELECT * FROM orderlog")
            temp_list = c.fetchall()
            order_log = temp_list[::-1]
            conn.commit()
            conn.close()
            return order_log

        if mode == 'order_nums':
            return_list = []
            conn = sqlite3.connect(warehouse,
                                detect_types=sqlite3.PARSE_DECLTYPES |
                                                sqlite3.PARSE_COLNAMES)
            c = conn.cursor()
            c.execute("SELECT order_num FROM orderlog")
            temp_list = c.fetchall()
            order_log = temp_list[::-1]
            conn.commit()
            conn.close()
            for order in order_log:
                return_list += order
            return return_list            

        if mode == 'order_details':
            order_num = kwargs['order']
            conn = sqlite3.connect(warehouse,
                                detect_types=sqlite3.PARSE_DECLTYPES |
                                                sqlite3.PARSE_COLNAMES)
            c = conn.cursor()
            c.execute("SELECT * FROM orderlog WHERE order_num = ?", (order_num,))
            temp_list = c.fetchall()[0]
            conn.commit()
            conn.close()
            return temp_list
        

    if note_type == 'loc':
        if mode == 'all':
            conn = sqlite3.connect(warehouse,
                                   detect_types=sqlite3.PARSE_DECLTYPES |
                                   sqlite3.PARSE_COLNAMES)
            c = conn.cursor()
            c.execute("SELECT * FROM notes WHERE type = ?", (note_type,))
            temp_list = c.fetchall()
            item_log = temp_list[::-1]        
            conn.commit()
            conn.close()
            return temp_list

    if note_type == 'item':
        if mode == 'all':
            conn = sqlite3.connect(warehouse,
                                   detect_types=sqlite3.PARSE_DECLTYPES |
                                   sqlite3.PARSE_COLNAMES)
            c = conn.cursor()
            c.execute("SELECT * FROM notes WHERE type = ?", (note_type,))
            temp_list = c.fetchall()
            item_log = temp_list[::-1]        
            conn.commit()
            conn.close()
            return temp_list
        
        if mode == 'history':
            item = kwargs['item']
            conn = sqlite3.connect(warehouse,
                                   detect_types=sqlite3.PARSE_DECLTYPES |
                                   sqlite3.PARSE_COLNAMES)
            c = conn.cursor()
            c.execute("SELECT * FROM notes WHERE item = ?", (item,))
            temp_list = c.fetchall()
            item_log = temp_list[::-1]        
            conn.commit()
            conn.close()
            return temp_list
        
        if mode == 'locations':
            item = kwargs['item']
            conn = sqlite3.connect(warehouse,
                                   detect_types=sqlite3.PARSE_DECLTYPES |
                                   sqlite3.PARSE_COLNAMES)
            c = conn.cursor()
            c.execute("SELECT item_history FROM items WHERE item = ?", (item,))
            temp_list = c.fetchone()[0]
            item_log = temp_list.split('\n')       
            conn.commit()
            conn.close()
            return item_log
    pass

    


create_database()
pack_database()
#       TO DO LIST
###  NOTE_INQUIRY FUNCTION
###  finish cycle count function/implementation
###  add update qty function, implement where needed
###  finish add location function
###  finish remove location function
###  implement remove item or deprecate item function
###  
###
###
###
###
###
###