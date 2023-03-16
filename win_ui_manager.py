from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import string
import pprint
import math
from data_manager import check_credentials, warehouse_inquiry, update_item, update_location_database, add_item_to_database, update_quantities, edit_user_database, get_user_info, add_note, note_inquiry, reset_database
pp = pprint.PrettyPrinter(indent=4)


class WinWarehouse:

    def __init__(self):
        self.root = Tk()
        self.root.title('Warehouse Manager')
        self.root.geometry('1024x768')
        self.root.minsize(1024, 768)
        self.root.resizable(False, False)
        self.startup()
        self.user_info = ''
        self.root.mainloop()

    def startup(self):
        login_frame_top = Frame(self.root)
        login_frame_top.pack()

        app_name = Label(login_frame_top, text='Warehouse Inventory Manager', anchor='center')
        app_name.config(font=("Georgia Bold", 35))
        app_name.grid(row=0, column=0, columnspan=15, padx=80, pady=(100, 270))

        login_frame_middle = Frame(self.root)
        login_frame_middle.pack()
    
        uname_label = Label(login_frame_middle, text='Username:')
        uname_label.grid(row=0, column=0, pady=(0,10), padx=(0, 10), sticky=E)

        uname = Entry(login_frame_middle, width=38)
        uname.grid(row=0, column=1, pady=(0, 5))
        uname.insert(0, 'testboss')

        pw_label = Label(login_frame_middle, text='Password:')
        pw_label.grid(row=1, column=0, pady=(0, 10), padx=(0, 10), sticky=E)

        upass = Entry(login_frame_middle, show='*', width=38)
        upass.grid(row=1, column=1, pady=(0, 5))
        upass.insert(0, 'boss1234')

        br_label = Label(login_frame_middle, text='Branch #:')
        br_label.grid(row=2, column=0, pady=(0, 10), padx=(0, 10), sticky=E)

        br_get = Entry(login_frame_middle, width=38)
        br_get.grid(row=2, column=1, pady=(0, 5))
        br_get.insert(0, '024')

        login_frame_bottom = Frame(self.root)
        login_frame_bottom.pack()

        login_btn = Button(login_frame_bottom, text='Login', command=lambda: self.log_in(user_in=uname, user_pass=upass, user_branch=br_get, frames=(login_frame_top, login_frame_middle, login_frame_bottom)), width=41)
        login_btn.pack(padx=(8,0), pady=(10,0))

    def log_in(self, user_in, user_pass, user_branch, frames):
        username = user_in.get()
        password = user_pass.get()
        branch = user_branch.get()
        login_frames = frames
        user_login = check_credentials(mode='login', uname=username, upass=password, ubranch=branch)
        if user_login:
            self.user_info = user_login
            self.clear_screen(login_frames)
            self.create_menu_screen()

    def clear_screen(self, *args):
        try:
            for frame in args:
                frame.destroy()
        except AttributeError:
            for frames in args:
                for frame in frames:
                    frame.destroy()

    def back_to_menu_screen(self, *args):
        for arg in args:
            self.clear_screen(arg)
        self.create_menu_screen()
        
    def create_menu_screen(self):
        # TOP FRAME WITH LABEL
        main_frame_top = Frame(self.root)
        main_frame_top.grid(row=0, column=0, columnspan=3, stick=NSEW)

        app_name = Label(main_frame_top, text='Warehouse Inventory Manager', anchor='center')
        app_name.config(font=("Georgia Bold", 30))
        app_name.grid(row=0, column=0, padx=(185,0), pady=(60, 90), stick=N)
        
        # LEFT FRAME WITH ITEM NOTES
        main_frame_left = Frame(self.root, height=555, width=328)
        main_frame_left.grid(row=1, column=0, padx=(10,5))
        main_frame_left.grid_propagate(False)

        item_inv_btn = Button(main_frame_left, text='Item Inventory', command=lambda: self.generate_item_inventory_screen(kill_frames=(main_frame_top, main_frame_left, main_frame_center, main_frame_right)), width=44)
        item_inv_btn.grid(row=0, column=0, padx=(3,0), pady=(0, 20))
        
        item_notes = warehouse_inquiry()
        item_list_var = Variable(value=item_notes)
        item_notes_box = Listbox(main_frame_left, listvariable=item_list_var, height=29, width=53, selectmode=SINGLE)
        item_notes_box.grid(row=1, column=0, padx=(3,0))

        back_btn = Button(main_frame_left, text='Log Out', command=lambda: self.logout(kill_frame=(main_frame_top, main_frame_left, main_frame_center, main_frame_right)), width=17)
        back_btn.grid(row=2, column=0, stick=W, padx=(2,0), pady=(15,0))
        
        # CENTER FRAME WITH LOCATION NOTES
        main_frame_center = Frame(self.root, height=555, width=328)
        main_frame_center.grid(row=1, column=1, padx=5)
        main_frame_center.grid_propagate(False)

        loc_inv_btn = Button(main_frame_center, text='Location Inventory', command=lambda: self.generate_location_inventory_screen(kill_frames=(main_frame_top, main_frame_left, main_frame_center, main_frame_right)), width=44)
        loc_inv_btn.grid(row=0, column=0, pady=(0, 20), padx=(3,0), stick=N)
               
        loc_notes = warehouse_inquiry(tag='loc', search='', mode='add_loc_pop')
        loc_list_var = Variable(value=loc_notes)
        loc_notes_box = Listbox(main_frame_center, listvariable=loc_list_var, height=29, width=53, selectmode=SINGLE)
        loc_notes_box.grid(row=1, column=0, padx=(3,0))
        
        exec_func_btn = Button(main_frame_center, text='Executive Functions', width=17, command=lambda: self.executive_popup(frames=kill_frames))
        exec_func_btn.grid(row=2, column=0, sticky=N, pady=(15,0))

        # RIGHT FRAME WITH ORDER NOTES
        main_frame_right = Frame(self.root, height=555, width=328)
        main_frame_right.grid(row=1, column=2, padx=5)
        main_frame_right.grid_propagate(False)

        order_btn = Button(main_frame_right, text='Generate Order', command=lambda: self.generate_order_screen(kill_frame=(main_frame_top, main_frame_left, main_frame_center, main_frame_right)), width=44)
        order_btn.grid(row=0, column=0, pady=(0, 20), padx=(3,0))

        order_log = note_inquiry(note_type='order')
        try:
            note_one = order_log[0]
            fill_tree = True
        except:
            fill_tree = False

        order_notes_tree = ttk.Treeview(main_frame_right, height=22)
        order_notes_tree['columns'] = ("details", "user")

        order_notes_tree.column("#0", anchor=W, width=98, stretch=NO)
        order_notes_tree.column("details", anchor=N, width=165, stretch=TRUE)
        order_notes_tree.column("user", anchor=N, width=55, stretch=TRUE)

        order_notes_tree.heading("#0", text="Order #", anchor=N)
        order_notes_tree.heading("details", text="Details", anchor=N)
        order_notes_tree.heading("user", text="User", anchor=N)

        
        if fill_tree:
            count = 0
            # print(order_log)
            for order in order_log:
                temp_date = str(order[0]).split(' ')[0]
                temp_details = order[4].split('\n')
                pcs = temp_details[0].split(':')[1].strip()
                lbs = temp_details[1].split(':')[1].strip()
                plt = temp_details[2].split(':')[1].strip()
                detail_note = f'{pcs} pcs - {lbs} lbs - {plt} plt'
                order_notes_tree.insert(parent='', index='end', iid=count, text=order[2], values=(detail_note, order[1]))
                parent_num = str(count)
                count += 1
                temp_items = order[3].split('\n')[:-1]
                parent_count = 0
                for item in temp_items:
                    temp_split = item.split(' ')
                    temp_item = temp_split[0].strip()
                    temp_qty = temp_split[1].strip()
                    order_notes_tree.insert(parent=parent_num, index=parent_count, iid=count, text=temp_date, values=(temp_item, temp_qty))
                    count += 1
                    parent_count += 1

        order_notes_tree.grid(row=1, column=0, stick=E, padx=(3,0))

        user_list_button = Button(main_frame_right, text='User List', command=lambda: self.view_user_list(), width=17)
        user_list_button.grid(row=2, column=0, stick=E, padx=(0,1), pady=(15,0))

        kill_frames=(main_frame_top, main_frame_left, main_frame_center, main_frame_right)


    def executive_popup(self, frames):
        if self.user_info[-1] != 'master':
            messagebox.showerror(title='Error', message='User does not have permission for this function')
            return
        
        if self.user_info[-1] == 'master':
            exec_box = Toplevel(self.root)
            exec_box.geometry('280x200+500+400')
            exec_box.title("Executive Functions")
        
            clog_btn = Button(exec_box, text='Change Log', width=20, command=lambda: self.show_changelog(box=exec_box))
            clog_btn.pack(pady=(40,10))
            
            reset_warehouse_btn = Button(exec_box, text='Reset Warehouse', width=20, command=lambda: self.reset_warehouse_pop(box=exec_box, kill_frames=frames))
            reset_warehouse_btn.pack(pady=10)    
                        
    def reset_warehouse_pop(self, box, kill_frames):
        if not messagebox.askokcancel(title='WARNING!', message='Warning! This action cannot be undone.  Are you sure you wish to completely reset to warehouse inventory?'):
            return
        
        box.destroy()
        
        check_pw_box = Toplevel(self.root)
        check_pw_box.geometry('300x200')
        check_pw_box.title('Confirm Password')
        
        check_pw_label = Label(check_pw_box, text='Please confirm user password')
        check_pw_label.pack(pady=(20,5))
        
        check_pw_entry = Entry(check_pw_box, width=25, show='*')
        check_pw_entry.pack(pady=(5,5))
               
        note_check_var = IntVar()
        note_check = Checkbutton(check_pw_box, text='Reset Note Log:', variable=note_check_var)
        note_check.pack(anchor=W, padx=(90,0))
        
        order_check_var = IntVar()
        order_check = Checkbutton(check_pw_box, text='Reset Order Log:', variable=order_check_var)
        order_check.pack(anchor=W, padx=(90,0), pady=(0,15))
        
        check_pw_btn = Button(check_pw_box, text='Submit', width=21, command=lambda: self.reset_warehouse_func(box=check_pw_box, entry=check_pw_entry, note_var=note_check_var, order_var=order_check_var, frames=kill_frames))
        check_pw_btn.pack(pady=10)

    def reset_warehouse_func(self, box, entry, note_var, order_var, frames):
        userpass = entry.get()
        
        pw_check = check_credentials(mode='pass', uname=self.user_info[0], upass=userpass)
        if not pw_check:
            messagebox.showerror(title="Error", message="Incorrect Password")
            return
        if pw_check:
            note_reset = note_var.get()
            order_reset = order_var.get()
            reset_database(note=note_reset, order=order_reset)
            add_note(note_type='war_reset', user=self.user_info)
            box.destroy()
            self.logout(kill_frame=frames)
            messagebox.showinfo(title='Warehouse', message='Database has been reset')
            return
        pass

    def show_changelog(self, box):
        box.destroy()
        
        change_box = Toplevel(self.root)
        change_box.geometry('980x600')
        change_box.title("Change Log")        
        
        change_box.winfo_width()
        change_box.winfo_height()
        
        change_frame_top = Frame(change_box)
        change_frame_top.grid(row=0, column=0, padx=10, pady=10, stick=W)
        
        change_search_btn = Button(change_frame_top, text='Search', width=12, command=lambda: self.search_log(box=change_box, tree=change_log_tree, entry=change_entry))
        change_search_btn.grid(row=0, column=0, padx=(0,5), stick=W)
        
        change_entry = Entry(change_frame_top, width=55)
        change_entry.grid(row=0, column=1)
        
        change_frame_bottom = Frame(change_box)
        change_frame_bottom.grid(row=1, column=0, padx=10)
        
        change_log = note_inquiry(note_type='all', mode='all')

        change_log_tree = ttk.Treeview(change_frame_bottom, height=25)
        change_log_tree['columns'] = ("date", "user", "type", "item", "loc", "log", "id")

        change_log_tree.column("#0", width=0, stretch=NO)
        change_log_tree.column("date", anchor=N, width=110)
        change_log_tree.column("user", anchor=N, width=50)
        change_log_tree.column("type", anchor=N, width=85)
        change_log_tree.column("item", anchor=N, width=200)
        change_log_tree.column("loc", anchor=N, width=100)
        change_log_tree.column("log", anchor=W, width=330)
        change_log_tree.column("id", anchor=N, width=80)
        
        change_log_tree.heading("#0", text="")
        change_log_tree.heading("date", text="Date", anchor=N)
        change_log_tree.heading("user", text="User", anchor=N)
        change_log_tree.heading("type", text="Type", anchor=N)
        change_log_tree.heading("item", text="Item", anchor=N)
        change_log_tree.heading("loc", text="Location", anchor=N)
        change_log_tree.heading("log", text="Log", anchor=N)
        change_log_tree.heading("id", text="ID", anchor=N)
        change_log_tree.grid(row=0, column=0, columnspan=3)
        
        temp_value = ['tempdate', 'rjr', 'type', 'item', 'location', 'this is the message log', 'id']
        if len(change_log) == 0:
            change_log_tree.insert('', 'end', iid='', text='', values=temp_value)
        else:
            for index, row in enumerate(change_log):
                temp_date = str(row[0]).split(' ')[0]
                temp_value = [temp_date, row[1], row[2], row[3], row[4], row[5], row[6]]
                change_log_tree.insert('', 'end', iid=index, text='', values=temp_value)  

    def search_log(self, box, tree, entry):
        for item in tree.get_children():
            tree.delete(item)
        e = entry.get()
        if e == '':
            print('empty')
            new_notes = note_inquiry(note_type='all', mode='all')
        if e != '':
            new_notes = note_inquiry(note_type='all', mode='search', search=e)        
        for index, row in enumerate(new_notes):
            temp_date = str(row[0]).split(' ')[0]
            temp_value = [temp_date, row[1], row[2], row[3], row[4], row[5], row[6]]
            tree.insert('', 'end', iid=index, text='', values=temp_value)

    def view_user_list(self, box=''):
        if self.user_info[7] != 'master':
            return
        
        if box != '':
            box.destroy()

        user_list_box = Toplevel(self.root)
        user_list_box.geometry('610x260')
        user_list_box.title("Users")
        
        user_list_frame = Frame(user_list_box)
        user_list_frame.pack()

        
        user_tree = ttk.Treeview(user_list_frame, height=9)
        user_tree['columns'] = ("full_name", "nick_name", "user_id", "email", "branch_perms", "status")

        user_tree.column("#0", width=0, stretch=NO)
        user_tree.column("full_name", anchor=W, width=130, stretch=TRUE)
        user_tree.column("nick_name", anchor=N, width=80, stretch=TRUE)
        user_tree.column("user_id", anchor=N, width=60)
        user_tree.column("email", anchor=W, width=160)
        user_tree.column("branch_perms", anchor=N, width=75)
        user_tree.column("status", anchor=N, width=70, stretch=TRUE)

        user_tree.heading("#0", text="")
        user_tree.heading("full_name", text="Full Name", anchor=W)
        user_tree.heading("nick_name", text="Nick Name", anchor=N)
        user_tree.heading("user_id", text="User ID", anchor=N)
        user_tree.heading("email", text="Email", anchor=N)
        user_tree.heading("branch_perms", text="Branch", anchor=N)
        user_tree.heading("status", text="Status", anchor=N)

        count = 0
        users = get_user_info(q='a')
        for user in users:
            user_tree.insert(parent='', index='end', iid=count, values=(user[3], user[4], user[2], user[1], user[5], user[6]))
            count += 1
        user_tree.grid(row=0, column=0, columnspan=3, padx=5, pady=(10,0))

        add_user_btn = Button(user_list_frame, text='Add User', command=lambda: self.add_user_menu(box=user_list_box), width=12)
        add_user_btn.grid(row=1, column=0, padx=(4,0), pady=(10,0), stick=W)

        edit_user_btn = Button(user_list_frame, text='Edit User', command=lambda: self.edit_user_menu(master_box=user_list_box, tree=user_tree), width=12)
        edit_user_btn.grid(row=1, column=1, pady=(10,0), stick=N)

        delete_user_btn = Button(user_list_frame, text='Delete User', command=lambda: self.remove_user(master_box=user_list_box, tree=user_tree), width=12)
        delete_user_btn.grid(row=1, column=2, padx=(0,4), pady=(10,0), stick=E)        

    def add_user_menu(self, box):
        add_user_box = Toplevel(box)
        add_user_box.geometry('330x460')
        add_user_frame = Frame(add_user_box)
        add_user_frame.grid(row=0, column=0, padx=(15,10))

        # Status
        user_status_check_var = IntVar()
        user_status_check = Checkbutton(add_user_frame, text="Master", variable=user_status_check_var)
        user_status_check.grid(row=0, column=1, pady=(10,10), stick=E)

        # Full Name
        full_name_label = Label(add_user_frame, text="Full Name: ")
        full_name_label.grid(row=1, column=0, pady=(0,20), stick=E)

        full_name_entry = Entry(add_user_frame, width=30)
        full_name_entry.grid(row=1, column=1, pady=(0,20))

        # User Name
        user_name_label = Label(add_user_frame, text='User Name: ')
        user_name_label.grid(row=2, column=0, pady=(0,20), stick=E)

        user_name_entry = Entry(add_user_frame, width=30)
        user_name_entry.grid(row=2, column=1, pady=(0,20))

        # User Pass
        user_pass_label = Label(add_user_frame, text='Password: ')
        user_pass_label.grid(row=3, column=0, pady=(0,20), stick=E)

        user_pass_entry = Entry(add_user_frame, show='*', width=30)
        user_pass_entry.grid(row=3, column=1, pady=(0,20))

        user_pass_label_two = Label(add_user_frame, text='Confirm Password: ')
        user_pass_label_two.grid(row=4, column=0, pady=(0,20), stick=E)

        user_pass_entry_two = Entry(add_user_frame, show='*', width=30)
        user_pass_entry_two.grid(row=4, column=1, pady=(0,20))
        
        # Email
        user_email_label = Label(add_user_frame, text='Email: ')
        user_email_label.grid(row=5, column=0, pady=(0,20), stick=E)

        user_email_entry = Entry(add_user_frame, width=30)
        user_email_entry.grid(row=5, column=1, pady=(0,20))

        # User ID
        user_id_label = Label(add_user_frame, text='User ID #: ')
        user_id_label.grid(row=6, column=0, pady=(0,20), stick=E)

        user_id_entry = Entry(add_user_frame, width=30)
        user_id_entry.grid(row=6, column=1, pady=(0,20))

        # Nick Name
        user_nick_label = Label(add_user_frame, text="User Nick Name: ")
        user_nick_label.grid(row=7, column=0, pady=(0,20), stick=E)

        user_nick_entry = Entry(add_user_frame, width=30)
        user_nick_entry.grid(row=7, column=1, pady=(0,20))
    
        # Branch Perms
        user_branch_label = Label(add_user_frame, text='Branch #: ')
        user_branch_label.grid(row=8, column=0, pady=(0,45), stick=E)

        user_branch_entry = Entry(add_user_frame, width=30)
        user_branch_entry.grid(row=8, column=1, pady=(0,45))

        # Add Button
        add_button = Button(add_user_frame, text='Add User', width=40, command=lambda: self.add_new_user(master_box=box, temp_box=add_user_box, fname=full_name_entry, uname=user_name_entry, pword=user_pass_entry, cpword=user_pass_entry_two, email=user_email_entry, uid=user_id_entry, nname=user_nick_entry, branch=user_branch_entry, stat=user_status_check_var))
        add_button.grid(row=9, column=0, columnspan=2, stick=E)

    ### NOTE ###
    def add_new_user(self, master_box, temp_box, fname, uname, pword, cpword, email, uid, nname, branch, stat):
        full_name = fname.get().title()
        user_name = uname.get().lower()
        password = pword.get()
        con_password = cpword.get()
        new_email = email.get()
        new_id = uid.get()
        nick_name = nname.get().upper()
        branch_perm = branch.get()
        status = stat.get()

        # CHECK FOR EMPTY FIELDS
        check_list = [full_name, user_name, password, con_password, new_email, new_id, nick_name, branch_perm]
        for check in check_list:
            if check == '':
                messagebox.showwarning(title='Warning', message="All fields are required.")
                return
        
        # CHECK FOR MATCHING PASSWORDS
        if password != con_password:
            messagebox.showwarning(title='Warning', message="Password fields must match")
            return
        
        # CHECK FOR VALID USER_ID
        try:
            user_id = int(new_id)
            if len(str(user_id)) != 3:
                messagebox.showwarning(title='Warning', message="'User ID' must be a positive 3-digit number and cannot start with 0")
                return
        except ValueError:
            messagebox.showwarning(title='Warning', message="'User ID' must be a positive 3-digit number and cannot start with 0")
            return

        # CHECK FOR VALID NICK_NAME
        num_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for x in nick_name:
            if x in num_list:
                messagebox.showwarning(title='Warning', message="'User Nick Name' must be 3 letters")
                return
        if len(nick_name) != 3:
            messagebox.showwarning(title='Warning', message="'User Nick Name' must be 3 letters")
            return

        # CHECK FOR VALID BRANCH_PERMS
        if len(branch_perm) != 3:
            messagebox.showwarning(title='Warning', message="'Branch #' must be a 3-digit number")
            return
        for x in branch_perm:
            if x not in num_list:
                messagebox.showwarning(title='Warning', message="'Branch #' must be a 3-digit number")
                return

        # CHECK 'STATUS'
        if status == 1:
            user_status = 'master'
        else:
            user_status = ''
        
        if not messagebox.askyesno(title='Add User', message=f'Are you sure all of the information you added is correct?'):
            return

        new_user_info = (user_name, password, new_email, user_id, full_name, nick_name, branch_perm, user_status)
        edit_user_database(user_info=new_user_info, mode='a', master_info=self.user_info)
        temp_box.destroy()
        self.view_user_list(box=master_box)
        return

    def remove_user(self, master_box, tree):
        user_tree = tree
        tree_select = user_tree.selection()
        select_vals = user_tree.item(tree_select)['values']

        if select_vals == "":
            return
        
        if not messagebox.askyesno(title='Delete User', message=f'Are you sure you want to remove this user from the database?'):
            return

        remove_id = select_vals[2]
        edit_user_database(user_info=remove_id, mode='r', master_info=self.user_info)
        self.view_user_list(box=master_box)
        return

    def edit_user_menu(self, master_box, tree):
        # GET TREE VALUES
        user_tree = tree
        tree_select = user_tree.selection()
        select_vals = user_tree.item(tree_select)['values']
        # CHECK FOR IF NO SELECTION
        if select_vals == "":
            return
        # OPEN NEW TOPLEVEL WINDOW AND FRAME
        box = master_box
        edit_user_box = Toplevel(master_box)
        edit_user_box.geometry('330x380')
        
        edit_user_frame = Frame(edit_user_box)
        edit_user_frame.grid(row=0, column=0, padx=(15,10))
        # GET USER INFO
        user_db_info = get_user_info(q='s', uid=select_vals[2])
        # Status
        user_status_check_var = IntVar()
        user_status_check = Checkbutton(edit_user_frame, text="Master", variable=user_status_check_var)
        user_status_check.grid(row=0, column=1, pady=(10,10), stick=E)
        if user_db_info[6] == 'master':
            user_status_check.select()
        # Full Name
        full_name_label = Label(edit_user_frame, text="Full Name: ")
        full_name_label.grid(row=1, column=0, pady=(0,20), stick=E)
        full_name_entry = Entry(edit_user_frame, width=30)
        full_name_entry.grid(row=1, column=1, pady=(0,20))
        full_name_entry.insert(0, user_db_info[3])
        # User Name
        user_name_label = Label(edit_user_frame, text='User Name: ')
        user_name_label.grid(row=2, column=0, pady=(0,20), stick=E)
        user_name_entry = Entry(edit_user_frame, width=30)
        user_name_entry.grid(row=2, column=1, pady=(0,20))
        user_name_entry.insert(0, user_db_info[0])        
        # Email
        user_email_label = Label(edit_user_frame, text='Email: ')
        user_email_label.grid(row=3, column=0, pady=(0,20), stick=E)
        user_email_entry = Entry(edit_user_frame, width=30)
        user_email_entry.grid(row=3, column=1, pady=(0,20))
        user_email_entry.insert(0, user_db_info[1])
        # User ID
        user_id_label = Label(edit_user_frame, text='User ID #: ')
        user_id_label.grid(row=4, column=0, pady=(0,20), stick=E)
        user_id_entry = Entry(edit_user_frame, width=30)
        user_id_entry.grid(row=4, column=1, pady=(0,20))
        user_id_entry.insert(0, user_db_info[2])
        # Nick Name
        user_nick_label = Label(edit_user_frame, text="User Nick Name: ")
        user_nick_label.grid(row=5, column=0, pady=(0,20), stick=E)
        user_nick_entry = Entry(edit_user_frame, width=30)
        user_nick_entry.grid(row=5, column=1, pady=(0,20))
        user_nick_entry.insert(0, user_db_info[4])
        # Branch Perms
        user_branch_label = Label(edit_user_frame, text='Branch #: ')
        user_branch_label.grid(row=6, column=0, pady=(0,45), stick=E)
        user_branch_entry = Entry(edit_user_frame, width=30)
        user_branch_entry.grid(row=6, column=1, pady=(0,45))
        user_branch_entry.insert(0, user_db_info[5])
        # Add Button
        new_user_info = (full_name_entry, user_name_entry, user_email_entry, user_id_entry, user_nick_entry, user_branch_entry, user_status_check_var)
        edit_button = Button(edit_user_frame, text='Submit Changes', width=38, command=lambda: self.edit_user(master_box=box, temp_box=edit_user_box, new_info=new_user_info, cur_info=user_db_info))
        edit_button.grid(row=7, column=0, columnspan=2, stick=E)

    ### NOTE ###
    def edit_user(self, master_box, temp_box, new_info, cur_info):
        # GET ENTRY DATA
        full_name = new_info[0].get().title()
        user_name = new_info[1].get().lower()
        new_email = new_info[2].get()
        new_id = new_info[3].get()
        nick_name = new_info[4].get().upper()
        branch_perm = new_info[5].get()
        status = new_info[6].get()
        # SET USER STATUS
        if status == 1:
            user_status = 'master'
        else:
            user_status = ''
        # CHECK FOR EMPTY FIELDS
        temp_check_list = (user_name, new_email, new_id, full_name, nick_name, branch_perm)
        for check in temp_check_list:
            if check == '':
                messagebox.showwarning(title='Warning', message="All fields are required.")
                return
        # CHECK FOR VALID USER_ID
        try:
            user_id = int(new_id)
            if len(str(user_id)) != 3:
                messagebox.showwarning(title='Warning', message="'User ID' must be a positive 3-digit number and cannot start with 0")
                return
        except ValueError:
            messagebox.showwarning(title='Warning', message="'User ID' must be a positive 3-digit number and cannot start with 0")
            return
        # CHECK FOR VALID NICK_NAME
        num_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for x in nick_name:
            if x in num_list:
                messagebox.showwarning(title='Warning', message="'User Nick Name' must be 3 letters")
                return
        if len(nick_name) != 3:
            messagebox.showwarning(title='Warning', message="'User Nick Name' must be 3 letters")
            return
        # CHECK FOR VALID BRANCH_PERMS
        if len(branch_perm) != 3:
            messagebox.showwarning(title='Warning', message="'Branch #' must be a 3-digit number")
            return
        for x in branch_perm:
            if x not in num_list:
                messagebox.showwarning(title='Warning', message="'Branch #' must be a 3-digit number")
                return
        # CHECK FOR NO CHANGE
        check_list = (user_name, new_email, user_id, full_name, nick_name, branch_perm, user_status)
        if check_list == cur_info:
            messagebox.showwarning(title='Warning', message="No Changes Detected")
            return
        # CONFIRM CHANGES
        if not messagebox.askyesno(title='Add User', message=f'Are you sure you want to make these changes?'):
            return
        # SEND NEW INFO TO DATA MANAGER
        new_user_info = (user_name, new_email, user_id, full_name, nick_name, branch_perm, user_status)
        edit_user_database(user_info=new_user_info, mode='e', cur_user_info=cur_info, master_info=self.user_info)
        # DESTROY TEMP BOX / REFRESH USER LIST BOX
        temp_box.destroy()
        self.view_user_list(box=master_box)

    def logout(self, kill_frame):
        self.clear_screen(kill_frame)
        self.user_info = ''
        self.startup()


## ITEM INVENTORY SCREEN FUNCTIONS

    def generate_item_inventory_screen(self, entry='', kill_frames=''):
        self.clear_screen(kill_frames)

        e = entry
        
        item_inv_screen_frame_top = Frame(self.root)
        item_inv_screen_frame_top.grid(row=0, column=0, stick=W)

        search_btn = Button(item_inv_screen_frame_top, text='Search', width=15, command=lambda: self.item_inv_search(search_entry, frames=(item_inv_screen_frame_top, item_inv_screen_frame_center, item_inv_screen_frame_right)))
        search_btn.grid(row=0, column=0, stick=W, pady=10, padx=(12,0))

        search_entry = Entry(item_inv_screen_frame_top, width=122)
        search_entry.grid(row=0, column=1, stick=W, pady=10, padx=(5,0))

        item_inv_screen_frame_center = Frame(self.root)
        item_inv_screen_frame_center.grid(row=1, column=0, stick=W)

        items = warehouse_inquiry(tag='item_inv', type=0, search=e)
        inv_tree = ttk.Treeview(item_inv_screen_frame_center, height=32)
        inv_tree['columns'] = ("item", "item_number", "item_type", "item_brand", "location",
                      "location_type", "alt_location_one", "alt_location_two",
                      "on_hand", "weight", "full_pallet")

        inv_tree.column("#0", width=0, stretch=NO)
        inv_tree.column("item", anchor=W, width=135, stretch=TRUE)
        inv_tree.column("item_number", anchor=W, width=65, stretch=TRUE)
        inv_tree.column("item_type", anchor=W, width=80)
        inv_tree.column("item_brand", anchor=W, width=75)
        inv_tree.column("location", anchor=W, width=80)
        inv_tree.column("location_type", anchor=W, width=55, stretch=TRUE)
        inv_tree.column("alt_location_one", anchor=W, width=80)
        inv_tree.column("alt_location_two", anchor=W, width=80)  
        inv_tree.column("on_hand", anchor=W, width=75)
        inv_tree.column("weight", anchor=W, width=55)
        inv_tree.column("full_pallet", anchor=W, width=75)

        inv_tree.heading("#0", text="")
        inv_tree.heading("item", text="Item", anchor=W)
        inv_tree.heading("item_number", text="Item #", anchor=W)
        inv_tree.heading("item_type", text="Item Type", anchor=W)
        inv_tree.heading("item_brand", text="Brand", anchor=W)
        inv_tree.heading("location", text="Location", anchor=W)
        inv_tree.heading("location_type", text="Zone", anchor=W)
        inv_tree.heading("alt_location_one", text="Alt 1", anchor=W)
        inv_tree.heading("alt_location_two", text="Alt 2", anchor=W)
        inv_tree.heading("on_hand", text="On Hand", anchor=W)
        inv_tree.heading("weight", text="Weight", anchor=W)
        inv_tree.heading("full_pallet", text="Full Pallet", anchor=W)

        count = 0
        for item in items:
            inv_tree.insert(parent='', index='end', iid=count, values=(item[0], item[1], item[2], item[3], item[4], item[10], item[5], item[6], item[7], item[8], item[9]))
            count += 1
        inv_tree.grid(row=0, column=0, padx=(10,3))
        
        view_scrollbar = ttk.Scrollbar(item_inv_screen_frame_center, orient=VERTICAL, command=inv_tree.yview)
        inv_tree['yscrollcommand'] = view_scrollbar.set
        view_scrollbar.grid(row=0, column=1, stick='ns')

        item_inv_screen_frame_right = Frame(self.root)
        item_inv_screen_frame_right.grid(row=1, column=1, stick=NS, padx=(3,0))

        back_btn = Button(item_inv_screen_frame_center, text="Back", width=15, command=lambda: self.back_to_menu_screen(item_inv_screen_frame_top, item_inv_screen_frame_center, item_inv_screen_frame_right))
        back_btn.grid(row=1, column=0, stick=W, pady=(10,0), padx=10)

        add_item_btn = Button(item_inv_screen_frame_right, text="Add Item", command=self.add_item, width=17)
        add_item_btn.grid(row=0, column=0, stick=W)
        
        edit_item = Button(item_inv_screen_frame_right, text="Edit Item", comman=lambda: self.edit_item(tree=inv_tree), width=17)
        edit_item.grid(row=1, column=0, stick=W, pady=(20,20))

        item_history_btn = Button(item_inv_screen_frame_right, text='Item History', command=lambda: self.item_history_menu(tree=inv_tree), width=17)
        item_history_btn.grid(row=2, column=0, stick=W)
        
        receive_item_btn = Button(item_inv_screen_frame_right, text='Receive Items', width=17)
        receive_item_btn.grid(row=3, column=0, pady=(522,0), stick=W)

    ### NOTE ###
    def edit_item(self, tree):
        inv_tree = tree
        tree_select = inv_tree.selection()
        select_vals = inv_tree.item(tree_select)['values']

        if select_vals == "":
            return

        edit_box = Toplevel(self.root)
        edit_box.geometry('300x530')
        edit_box.title("Item Editor")

        item_label = Label(edit_box, text="Item: ")
        item_label.grid(row=0, column=0, padx=5, pady=(20, 0), stick=E)

        item_entry = Entry(edit_box, width=25)
        item_entry.grid(row=0, column=1, columnspan=2, stick=W, pady=(20,0))
        item_entry.insert(0, select_vals[0])
        item_entry.config(state=DISABLED)

        item_num_label = Label(edit_box, text="Item Number: ")
        item_num_label.grid(row=1, column=0, padx=5, pady=(20, 0), stick=E)

        item_num_entry = Entry(edit_box, width=25)
        item_num_entry.grid(row=1, column=1, columnspan=2, stick=W, pady=(20,0))
        item_num_entry.insert(0, str(select_vals[1]))
        item_num_entry.config(state=DISABLED)

        item_type_label = Label(edit_box, text="Item Type: ")
        item_type_label.grid(row=2, column=0, padx=5, pady=(20, 0), stick=E)

        item_type_entry = Entry(edit_box, width=25)
        item_type_entry.grid(row=2, column=1, columnspan=2, stick=W, pady=(20,0))
        item_type_entry.insert(0, select_vals[2])

        item_brand_label = Label(edit_box, text="Item Brand: ")
        item_brand_label.grid(row=3, column=0, padx=5, pady=(20, 0), stick=E)

        item_brand_entry = Entry(edit_box, width=25)
        item_brand_entry.grid(row=3, column=1, columnspan=2, stick=W, pady=(20,0))
        item_brand_entry.insert(0, select_vals[3])

        item_loc_label = Label(edit_box, text="Item Location: ")
        item_loc_label.grid(row=4, column=0, padx=5, pady=(20, 0), stick=E)

        item_loc_entry = Entry(edit_box, width=25)
        item_loc_entry.grid(row=4, column=1, columnspan=2, stick=W, pady=(20,0))
        item_loc_entry.insert(0, select_vals[4])

        item_zone_label = Label(edit_box, text="Item Zone: ")
        item_zone_label.grid(row=5, column=0, pady=(20, 0), stick=E)

        item_zone_entry = Entry(edit_box, width=25)
        item_zone_entry.grid(row=5, column=1, columnspan=2, stick=W, pady=(20,0))
        item_zone_entry.insert(0, select_vals[5])
        item_zone_entry.config(state=DISABLED)

        item_alt_loc_label = Label(edit_box, text="Item Alt Location: ")
        item_alt_loc_label.grid(row=6, column=0, padx=5, pady=(20, 0), stick=E)

        item_alt_loc_entry = Entry(edit_box, width=25)
        item_alt_loc_entry.grid(row=6, column=1, columnspan=2, stick=W, pady=(20,0))
        item_alt_loc_entry.insert(0, select_vals[6])

        item_alt_loc_label_two = Label(edit_box, text="Item Alt Location 2: ")
        item_alt_loc_label_two.grid(row=7, column=0, padx=5, pady=(20, 0), stick=E)

        item_alt_loc_entry_two = Entry(edit_box, width=25)
        item_alt_loc_entry_two.grid(row=7, column=1, columnspan=2, stick=W, pady=(20,0))
        item_alt_loc_entry_two.insert(0, select_vals[7])

        item_onhand_label = Label(edit_box, text="On Hand Qty: ")
        item_onhand_label.grid(row=8, column=0, padx=5, pady=(20, 0), stick=E)

        item_onhand_entry = Entry(edit_box, width=25)
        item_onhand_entry.grid(row=8, column=1, columnspan=2, stick=W, pady=(20,0))
        item_onhand_entry.insert(0, select_vals[8])

        item_weight_label = Label(edit_box, text="Item Weight: ")
        item_weight_label.grid(row=9, column=0, padx=5, pady=(20, 0), stick=E)

        item_weight_entry = Entry(edit_box, width=25)
        item_weight_entry.grid(row=9, column=1, columnspan=2, stick=W, pady=(20,0))
        item_weight_entry.insert(0, select_vals[9])

        item_pallet_label = Label(edit_box, text="Full Pallet: ")
        item_pallet_label.grid(row=10, column=0, padx=5, pady=(20, 0), stick=E)

        item_pallet_entry = Entry(edit_box, width=25)
        item_pallet_entry.grid(row=10, column=1, columnspan=2, stick=W, pady=(20,0))
        item_pallet_entry.insert(0, select_vals[10])
        
        new_item_info = (item_entry, item_num_entry, item_type_entry, item_brand_entry, item_loc_entry, item_zone_entry, item_alt_loc_entry, item_alt_loc_entry_two, item_onhand_entry, item_weight_entry, item_pallet_entry)
        item_update_btn = Button(edit_box, text="Update Item", width=37, command=lambda: update_item(edit_box, new_info=new_item_info, current_vals=select_vals, master_info=self.user_info))
        item_update_btn.grid(row=11, column=0, columnspan=2, stick=E, padx=(13, 0), pady=(20,))

    def show_empties(self, empty_loc):
        empties = empty_loc
        empty_win = Toplevel(self.root)
        empty_win.geometry('200x280')
        empty_win.title("Empty Locations")

        
        empty_list_var = Variable(value=empties)
        empty_box = Listbox(empty_win, listvariable=empty_list_var, height=15, width=20, selectmode=SINGLE)
        empty_box.grid(row=0, column=0, padx=(30, 0), pady=10)
        scrollbar = ttk.Scrollbar(empty_win, orient=VERTICAL, command=empty_box.yview)
        empty_box['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=1, stick='ns', pady=10)

    def item_inv_search(self, entry, frames):
        inv_frames = frames
        search_var = entry.get()
        
        self.generate_item_inventory_screen(entry=search_var, kill_frames=inv_frames)

    ### NOTE ###
    def add_item(self):
        add_box = Toplevel(self.root)
        add_box.title("Add Item")
        add_box.geometry('300x400')
        
        item_label = Label(add_box, text="Item: ")
        item_label.grid(row=0, column=0, padx=5, pady=(20, 0), stick=E)

        item_entry = Entry(add_box, width=25)
        item_entry.grid(row=0, column=1, columnspan=2, stick=W, pady=(20,0))

        item_num_label = Label(add_box, text="Item Number: ")
        item_num_label.grid(row=1, column=0, padx=5, pady=(20, 0), stick=E)

        item_num_entry = Entry(add_box, width=25)
        item_num_entry.grid(row=1, column=1, columnspan=2, stick=W, pady=(20,0))

        item_type_label = Label(add_box, text="Item Type: ")
        item_type_label.grid(row=2, column=0, padx=5, pady=(20, 0), stick=E)

        item_type_entry = Entry(add_box, width=25)
        item_type_entry.grid(row=2, column=1, columnspan=2, stick=W, pady=(20,0))

        item_brand_label = Label(add_box, text="Item Brand: ")
        item_brand_label.grid(row=3, column=0, padx=5, pady=(20, 0), stick=E)

        item_brand_entry = Entry(add_box, width=25)
        item_brand_entry.grid(row=3, column=1, columnspan=2, stick=W, pady=(20,0))

        item_loc_label = Label(add_box, text="Item Location: ")
        item_loc_label.grid(row=4, column=0, padx=5, pady=(20, 0), stick=E)

        item_loc_entry = Entry(add_box, width=25)
        item_loc_entry.grid(row=4, column=1, columnspan=2, stick=W, pady=(20,0))

        item_weight_label = Label(add_box, text="Item Weight: ")
        item_weight_label.grid(row=5, column=0, padx=5, pady=(20, 0), stick=E)

        item_weight_entry = Entry(add_box, width=25)
        item_weight_entry.grid(row=5, column=1, columnspan=2, stick=W, pady=(20,0))

        item_pallet_label = Label(add_box, text="Full Pallet: ")
        item_pallet_label.grid(row=6, column=0, padx=5, pady=(20, 0), stick=E)

        item_pallet_entry = Entry(add_box, width=25)
        item_pallet_entry.grid(row=6, column=1, columnspan=2, stick=W, pady=(20,0))

        item_add_btn = Button(add_box, text="Add Item", width=35, command=lambda: add_item_to_database(box=add_box, item=item_entry, inum=item_num_entry, itype=item_type_entry, ibrand=item_brand_entry, iloc=item_loc_entry, iweight=item_weight_entry, ipallet=item_pallet_entry, master_info=self.user_info))
        item_add_btn.grid(row=7, column=0, columnspan=2, stick=E, padx=(18, 0), pady=(45,))        

    def item_history_menu(self, tree):
        inv_tree = tree
        tree_select = inv_tree.selection()
        select_vals = inv_tree.item(tree_select)['values']
        print(select_vals)
        if select_vals == "":
            return
        
        history_box = Toplevel(self.root)
        history_box.geometry('600x380')
        history_box.title("Item History")        
        
        left_frame = Frame(history_box)
        left_frame.grid(row=0, column=0, padx=(15,0), pady=15, stick=N)

        right_frame = Frame(history_box)
        right_frame.grid(row=0, column=1, padx=5, pady=15)

        item_locations_label = Label(left_frame, text='Location History:')
        item_locations_label.grid(row=0, column=0, stick=E, pady=(10, 156))

        item_history_label = Label(left_frame, text='Item History:')
        item_history_label.grid(row=1, column=0, stick=E)

        ### LOCATION HISTORY BOX
        item_locations_box = Listbox(right_frame, width=75, height=9)
        item_locations_box.grid(row=0, column=0, pady=(10, 30))
        item_locations = note_inquiry(note_type='item', mode='locations', item=select_vals[0])
        loc_count = 0
        for loc in item_locations:
            item_locations_box.insert(loc_count, loc)
            loc_count += 1

        ### ITEM HISTORY BOX
        ########  CHANGE TO TREEVIEW
        ########  CHANGE NOTES TO INSERT ROW FOR EACH INDIVIDUAL CHANGE
        ########  ADD EACH ROW TO TREEVIEW, CAN POSSIBLY CHANGE MENU SCREEN AFTEr
        item_history_box = Listbox(right_frame, width=75, height=9)
        item_history_box.grid(row=1, column=0)
        item_history = note_inquiry(note_type='item', mode='history', item=select_vals[0])
        edit_count = 0
        for edit in item_history[::-1]:
            temp_date = str(edit[0]).split(' ')[0]
            new_message = f"{temp_date} - {edit[1]} - {edit[5]}"
            item_history_box.insert(edit_count, new_message)
            edit_count += 1
        print(item_history)
## LOCATION INVENTORY SCREEN FUNCTIONS

    def generate_location_inventory_screen(self, entry='', kill_frames=''):
        self.clear_screen(kill_frames)

        e = entry
        
        location_inv_screen_frame_top = Frame(self.root)
        location_inv_screen_frame_top.grid(row=0, column=0, padx=(10, 0), stick=W)

        search_btn = Button(location_inv_screen_frame_top, text='Search', width=15, command=lambda: self.location_inv_search(entry=search_entry, frames=(location_inv_screen_frame_top, location_inv_screen_frame_center, location_inv_screen_frame_right)))
        search_btn.grid(row=0, column=0, pady=10)

        search_entry = Entry(location_inv_screen_frame_top, width=122)
        search_entry.grid(row=0, column=1, pady=10, padx=(5,0))

        location_inv_screen_frame_center = Frame(self.root)
        location_inv_screen_frame_center.grid(row=1, column=0, padx=(10, 0))

        locations = warehouse_inquiry(tag='loc', search=e, mode='')
        inv_tree = ttk.Treeview(location_inv_screen_frame_center, height=32)
        inv_tree['columns'] = ("location", "location_zone", "location_utn", "item", "item_qty", "alt_item_one", "alt_item_one_qty", "alt_item_two", "alt_item_two_qty")

        inv_tree.column("#0", width=0, stretch=NO)
        inv_tree.column("location", anchor=W, width=75)
        inv_tree.column("location_zone", anchor=W, width=70)
        inv_tree.column("location_utn", anchor=W, width=80)
        inv_tree.column("item", anchor=W, width=150)
        inv_tree.column("item_qty", anchor=W, width=60)
        inv_tree.column("alt_item_one", anchor=W, width=150)
        inv_tree.column("alt_item_one_qty", anchor=W, width=60)  
        inv_tree.column("alt_item_two", anchor=W, width=150)
        inv_tree.column("alt_item_two_qty", anchor=W, width=60)

        inv_tree.heading("#0", text="")
        inv_tree.heading("location", text="Location", anchor=N)
        inv_tree.heading("location_zone", text="Zone", anchor=N)
        inv_tree.heading("location_utn", text="UTN", anchor=N)
        inv_tree.heading("item", text="Item", anchor=N)
        inv_tree.heading("item_qty", text="Qty", anchor=N)
        inv_tree.heading("alt_item_one", text="Item #2", anchor=N)
        inv_tree.heading("alt_item_one_qty", text="Qty", anchor=N)
        inv_tree.heading("alt_item_two", text="Item #3", anchor=N)
        inv_tree.heading("alt_item_two_qty", text="Qty", anchor=N)
        

        count = 0
        for location in locations:
            inv_tree.insert(parent='', index='end', iid=count, values=(location[1], location[2], location[3], location[4], location[7], location[5], location[8], location[6], location[9]))
            count += 1
        inv_tree.grid(row=0, column=0)
        

        view_scrollbar = ttk.Scrollbar(location_inv_screen_frame_center, orient=VERTICAL, command=inv_tree.yview)
        inv_tree['yscrollcommand'] = view_scrollbar.set
        view_scrollbar.grid(row=0, column=1, stick='ns')

        location_inv_screen_frame_right = Frame(self.root)
        location_inv_screen_frame_right.grid(row=1, column=1, padx=(5, 0), stick=NS)

        # add - edit - history - remove - 

        add_loc_btn = Button(location_inv_screen_frame_right, text='Add Location', command=self.add_location_popup, width=17)
        add_loc_btn.grid(row=0, column=0, stick=W, pady=(0,20))

        edit_location_btn = Button(location_inv_screen_frame_right, text="Edit Location", command=lambda: self.edit_location(tree=inv_tree), width=17)
        edit_location_btn.grid(row=1, column=0, stick=W, pady=(0,20))

        location_history_btn = Button(location_inv_screen_frame_right, text='Location History', width=17)
        location_history_btn.grid(row=2, column=0, stick=W, pady=(0,20))
        # def remove_location(self, tree):
        remove_location_btn = Button(location_inv_screen_frame_right, text='Remove location', width=17, command=lambda: self.remove_location(tree=inv_tree))
        remove_location_btn.grid(row=3, column=0, stick=W, pady=(0,20))

        inventory_list = warehouse_inquiry('cc')
        cc_btn = Button(location_inv_screen_frame_right, text='Cycle Count', width=17, command=lambda: self.start_cycle_count(inventory=inventory_list, cc_count=50))
        cc_btn.grid(row=4, column=0, stick=W, pady=(455,0))

        back_btn = Button(location_inv_screen_frame_center, text="Back", width=17, command=lambda: self.back_to_menu_screen(location_inv_screen_frame_top, location_inv_screen_frame_center, location_inv_screen_frame_right))
        back_btn.grid(row=1, column=0, columnspan=2, stick=W, pady=10)
    
    def inventory_functions_menu(self):
        cc_menu_box = Toplevel(self.root)
        cc_menu_box.geometry("300x300")
        cc_menu_box.title("Inventory Functions")
        
        inventory_list = warehouse_inquiry('cc')
        print(inventory_list)
        cc_menu_frame = Frame(cc_menu_box)
        cc_menu_frame.pack(padx=40, pady=50)

        cc_full_btn = Button(cc_menu_frame, text='Full Cycle Count', command=lambda: self.start_cycle_count(frame=cc_menu_frame, box=cc_menu_box, inventory=inventory_list), width=20)
        cc_full_btn.pack(pady=(30,0))

        add_loc_btn = Button(cc_menu_frame, text='Add Location', command=lambda: self.add_location_popup(frame=cc_menu_frame, box=cc_menu_box), width=20)
        add_loc_btn.pack(pady=(30,0))

        remove_loc_btn = Button(cc_menu_frame, text='Remove Location', command=lambda: self.remove_location_popup(frame=cc_menu_frame, box=cc_menu_box), width=20)
        remove_loc_btn.pack(pady=(30,0))

    def remove_location_popup(self):
        temp_remove_loc_box = Toplevel(self.root)
        temp_remove_loc_box.geometry('530x350')
        temp_loc_frame = Frame(temp_remove_loc_box)
        temp_loc_frame.grid(row=0, column=0, padx=18, pady=25)

        loc_list = warehouse_inquiry(tag='loc', search='', mode='')
        
        loc_tree = ttk.Treeview(temp_loc_frame, height=12)
        loc_tree['columns'] = ("loc", "item", "alt_one", "alt_two")

        loc_tree.column("#0", width=0, stretch=NO)
        loc_tree.column("loc", anchor=W, width=90)
        loc_tree.column("item", anchor=W, width=130)
        loc_tree.column("alt_one", anchor=W, width=130)
        loc_tree.column("alt_two", anchor=W, width=130)
        
        loc_tree.heading("#0", text="")
        loc_tree.heading("loc", text="LOC", anchor=N)
        loc_tree.heading("item", text="Item", anchor=N)
        loc_tree.heading("alt_one", text="Alt Item One", anchor=N)
        loc_tree.heading("alt_two", text="Alt Item Two", anchor=N)
    
        loc_tree.grid(row=0, column=0)

        scrollbar = ttk.Scrollbar(temp_loc_frame, orient=VERTICAL, command=loc_tree.yview)
        loc_tree['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=0, column=1, stick='ns', pady=(10,0))

        count = 0
        for loc in loc_list:
            loc_tree.insert(parent='', index='end', iid=count, values=(loc[1], loc[4], loc[5], loc[6]))
            count += 1

        remove_btn = Button(temp_loc_frame, text='Remove Location', command=lambda: self.remove_location(box=temp_remove_loc_box, tree=loc_tree), width=25)
        remove_btn.grid(row=1, column=0, pady=(20,0))

    ### NOTE ###
    def remove_location(self, tree):
        loc_tree = tree
        selection = loc_tree.selection()
        selection_vals = loc_tree.item(selection)['values']
        position = ''
        if selection_vals == '':
            return
        
        if not messagebox.askyesno(title='WARNING', message='WARNING!  This action cannot be undone.  Do you wish to continue?'):
            return
        
        remove_loc = selection_vals[0]

        edit_loc_info = warehouse_inquiry(tag='loc_id', location=remove_loc, mode='a')
        if len(edit_loc_info) == 1:
            position = 'last'

        update_location_database(master_info=self.user_info, mode='remove', location_info=edit_loc_info, primary_vars=selection_vals, list_pos=position)
        return

    def add_location_popup(self):
        temp_add_loc_box = Toplevel(self.root)
        temp_add_loc_box.geometry('300x330')

        temp_loc_frame = Frame(temp_add_loc_box)
        temp_loc_frame.grid(row=0,column=0, padx=35, pady=25)

        new_location_label = Label(temp_loc_frame, text="*New Location:")
        new_location_label.grid(row=0, column=0, stick=E)

        new_location_entry = Entry(temp_loc_frame, width=20)
        new_location_entry.grid(row=0, column=1, padx=(10))
        
        new_zone_label = Label(temp_loc_frame, text="*Zone:")
        new_zone_label.grid(row=1, column=0, stick=E, pady=(20,0))

        new_zone_entry = Entry(temp_loc_frame, width=20)
        new_zone_entry.grid(row=1, column=1, padx=(10), pady=(20,0))

        new_utn_label = Label(temp_loc_frame, text='UTN:')
        new_utn_label.grid(row=2, column=0, stick=E, pady=(20,0))

        new_utn_entry = Entry(temp_loc_frame, width=20)
        new_utn_entry.grid(row=2, column=1, padx=(10), pady=(20,0))

        # item_label = Label(temp_loc_frame, text="Item:")
        # item_label.grid(row=3, column=0, stick=E, pady=(20,0))

        # item_entry = Entry(temp_loc_frame, width=20)
        # item_entry.grid(row=3, column=1, padx=(10), pady=(20,0))

        # GETTING LOCATIONS FOR DROPDOWN
        loc_list = warehouse_inquiry(tag='loc', mode='add_loc_pop')

        # CHANGE DROPDOWN TO LISTBOX 
        loc_drop_label = Label(temp_loc_frame, text="*Comes after:")
        loc_drop_label.grid(row=3, column=0, pady=(10,0), stick=E)

        list_var = Variable(value=loc_list)
        loc_box = Listbox(temp_loc_frame, listvariable=list_var, height=8, width=20, selectmode=SINGLE)
        loc_box.grid(row=3, column=1, pady=(10,0))
        
        scrollbar = ttk.Scrollbar(temp_loc_frame, orient=VERTICAL, command=loc_box.yview)
        loc_box['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=3, column=2, stick='ns', pady=(10,0))

        required_label = Label(temp_loc_frame, text="*required:")
        required_label.grid(row=4, column=0, pady=(10,0), stick=W)

        add_button = Button(temp_loc_frame, text='Add Location', command=lambda: self.add_location(box=temp_add_loc_box, loc=new_location_entry, zone=new_zone_entry, utn=new_utn_entry, after=loc_box, loc_list=loc_list), width=15)
        add_button.grid(row=4, column=1, pady=(10,0))        

    ### NOTE ###
    def add_location(self, box, loc, zone, utn, after, loc_list):
        new_loc = loc.get().upper()
        new_zone = zone.get().upper()
        new_utn = utn.get()
        selection = after.curselection()
                    
        if new_loc == '' or new_zone == '':
            messagebox.showwarning(title="Error", message="Please enter all *required fields")
            return

        if new_loc in loc_list:
            messagebox.showwarning(title="Error", message="Location Already Exists")
            return

        if new_utn != '':
            try:
                new_utn = int(new_utn)
            except:
                messagebox.showwarning(title="Error", message="UTN must be numbers only")
                return

        try:
            prev_loc = after.get(selection)
            print(prev_loc)
        except Exception as e:
            messagebox.showwarning(title="Error", message="Must specify what location comes before the new location.")
            print(e)
            return

        edit_loc_info = warehouse_inquiry(tag='loc_id', location=prev_loc, mode='a')
        after_loc = edit_loc_info[0]
        try:
            before_loc = edit_loc_info[1]
            if after_loc[2] == before_loc[2] and after_loc[2] != new_zone:
                if messagebox.askyesno(title="Warning", message=f"Warning: {after_loc[2]} is the recommended zone for this location.  Would you like to use {after_loc[2]} instead of {new_zone}?"):
                    new_zone = after_loc[2]
            position = ''
        except IndexError:
            position = 'last'

        zone_list = warehouse_inquiry(tag='zone')
        if new_zone not in zone_list:
            if not messagebox.askyesno(title='Zone', message=f'Zone {new_zone} does not exist.  Are you sure you want to add {new_loc} to this zone?'):
                print('mission aborted')
                return

        try:
            prev_loc = after.get(selection)
            print(prev_loc)
        except Exception as e:
            messagebox.showwarning(title="Error", message="Must specify what location comes before the new location.")
            print(e)
            return
        new_info = (new_loc, new_zone, new_utn, position)
        update_location_database(master_info=self.user_info, location_info=new_info, mode='add', edit_list=edit_loc_info)
        # add_location_to_database(location=new_loc, zone=new_zone, item=new_item, edit_list=edit_loc_info, list_pos=position)
        
        box.destroy()
        return

    def start_cycle_count(self, inventory, cc_count=0, frame='', temp_cc_box=''):
        if temp_cc_box == '':
            temp_cc_box = Toplevel(self.root)
            temp_cc_box.geometry("300x300")            
        
        if frame != '':
            frame.destroy()

        temp_cc_frame = Frame(temp_cc_box)
        temp_cc_frame.grid(row=0, column=0, padx=(15,0))
    
        inventory_list = inventory
        cycle_location = inventory_list[cc_count]
        
        location_label = Label(temp_cc_frame, text=cycle_location[1])
        location_label.grid(row=0, column=1, pady=(15,30), padx=(10,0))
        location_label.config(font=("Segoe UI", 18))
        
        # Main Item
        item_label = Label(temp_cc_frame, text="Item: ")
        item_label.grid(row=1, column=0, pady=10, stick=E)
        item_number_label = Label(temp_cc_frame, text=cycle_location[4], width=20)
        item_number_label.grid(row=1, column=1, pady=10)
        item_qty_entry = Entry(temp_cc_frame, width=8)
        item_qty_entry.grid(row=1, column=2, padx=(10,0), pady=10)
        item_qty_entry.insert(0, cycle_location[7])

        # Alt Item One
        alt_item_label = Label(temp_cc_frame, text="Item #2: ")
        alt_item_label.grid(row=2, column=0, pady=10)
        alt_item_number_label = Label(temp_cc_frame, text=cycle_location[5])
        alt_item_number_label.grid(row=2, column=1, pady=10)
        alt_item_qty_entry = Entry(temp_cc_frame, width=8)
        alt_item_qty_entry.grid(row=2, column=2, padx=(10,0), pady=10)
        alt_item_qty_entry.insert(0, cycle_location[8])
        if cycle_location[5] == '':
            alt_item_qty_entry.config(state=DISABLED)

        # Alt Item Two
        alt_item_two_label = Label(temp_cc_frame, text="Item #3: ")
        alt_item_two_label.grid(row=3, column=0, pady=10)
        alt_item_two_number_label = Label(temp_cc_frame, text=cycle_location[6])
        alt_item_two_number_label.grid(row=3, column=1, pady=10)
        alt_item_two_qty_entry = Entry(temp_cc_frame, width=8)
        alt_item_two_qty_entry.grid(row=3, column=2, padx=(10,0), pady=10)
        alt_item_two_qty_entry.insert(0, cycle_location[9])
        if cycle_location[6] == '':
            alt_item_two_qty_entry.config(state=DISABLED)

        qty_entries = [item_qty_entry, alt_item_qty_entry, alt_item_two_qty_entry]

        # Buttons
        next_button = Button(temp_cc_frame, text='Next', width=10, command=lambda:self.update_cycle_count(box=temp_cc_box, frame=temp_cc_frame, next_step='fw', count=cc_count, location=cycle_location[1], inventory=inventory_list, entries=qty_entries))
        next_button.grid(row=4, column=1, columnspan=2, stick=E, pady=(35,0))

        back_button = Button(temp_cc_frame, text='Back', width=10)
        back_button.grid(row=4, column=0, columnspan=2, stick=W, pady=(35,0))

    ### NOTE ###
    def update_cycle_count(self, box, next_step, count, location, inventory, frame, entries):
        try:
            item_qty = int(entries[0].get())
            alt_item_qty = int(entries[1].get())
            alt_item_two_qty = int(entries[2].get())
            entry_list = [item_qty, alt_item_qty, alt_item_two_qty]
        except Exception as e:
            messagebox.showwarning(title="Error", message=f"Invalid Qauntity: {entry}")
            return
        for entry in entry_list:
            if entry < 0:
                messagebox.showwarning(title="Error", message=f"Invalid Qauntity: {entry}")
                return
        temp_box = box
        temp_location = location
        temp_inventory = inventory
        temp_frame = frame
        max_count = len(temp_inventory) - 1
        
        update_location_database(master_info=self.user_info, location_info=temp_location, primary_vars=entry_list, mode='cc')

        if next_step == 'fw':
            if count < len(temp_inventory)-1:
                count += 1 
                self.start_cycle_count(box=box, cc_count=count, inventory=temp_inventory, frame=temp_frame)
            else:
                messagebox.showinfo(title='Cycle Count Complete', message='Cycle Count Complete')
                update_quantities(master_info=self.user_info)
                box.destroy()
        if next_step == 'bw':
            if count > 0:
                count -= 1
        
    def location_inv_search(self, entry, frames):
        inv_frames = frames
        search_var = entry.get()
        
        self.generate_location_inventory_screen(entry=search_var, kill_frames=inv_frames)

    ### NOTE ###
    def edit_location(self, tree):
        loc_tree = tree
        selection = loc_tree.selection()
        selection_vals = loc_tree.item(selection)['values']
    
        # print(selection)
        # print(selection_vals)
        
        if selection_vals == "":
            return
                                                        # loc. zone. utn. item. itemqty. item2. item2qty. item3. item3qty
        else:
            edit_location_box = Toplevel(self.root)
            edit_location_box.geometry('360x460')
            edit_location_box.title("Location Editor")

            edit_location_frame = Frame(edit_location_box)
            edit_location_frame.grid(row=0, column=0, padx=(25,0))

            location_label = Label(edit_location_frame, text="Location: ")
            location_label.grid(row=0, column=0, pady=(20,0))

            location_entry = Entry(edit_location_frame, width=25)
            location_entry.grid(row=0, column=1, columnspan=2, stick=W, pady=(20,0))
            location_entry.insert(0, selection_vals[0])
            location_entry.config(state=DISABLED)
            
            location_zone_label = Label(edit_location_frame, text="Zone")
            location_zone_label.grid(row=1, column=0, padx=5, pady=(20, 0), stick=E)

            location_zone_entry = Entry(edit_location_frame, width=25)
            location_zone_entry.grid(row=1, column=1, columnspan=2, stick=W, pady=(20,0))
            location_zone_entry.insert(0, selection_vals[1])
            location_zone_entry.config(state=DISABLED)
            
            location_utn_label = Label(edit_location_frame, text="UTN: ")
            location_utn_label.grid(row=2, column=0, pady=(20, 0))

            location_utn_entry = Entry(edit_location_frame, width=25)
            location_utn_entry.grid(row=2, column=1, columnspan=2, stick=W, pady=(20,0))
            location_utn_entry.insert(0, selection_vals[2])

            item_label = Label(edit_location_frame, text="Item: ")
            item_label.grid(row=3, column=0, pady=(20, 0))

            item_entry = Entry(edit_location_frame, width=25)
            item_entry.grid(row=3, column=1, columnspan=2, stick=W, pady=(20,0))
            item_entry.insert(0, selection_vals[3])

            item_prim_check_var = IntVar()
            item_primary_check = Checkbutton(edit_location_frame, text="Primary", variable=item_prim_check_var)
            item_primary_check.grid(row=3, column=3, pady=(20,0))
            
            item_qty_label = Label(edit_location_frame, text="Qauntity: ")
            item_qty_label.grid(row=4, column=0, pady=(20, 0))
            
            item_qty_entry = Entry(edit_location_frame, width=25)
            item_qty_entry.grid(row=4, column=1, columnspan=2, stick=W, pady=(20,0))
            item_qty_entry.insert(0, selection_vals[4])
            
            alt_item_one_label = Label(edit_location_frame, text="Item #2: ")
            alt_item_one_label.grid(row=5, column=0, pady=(20, 0))

            alt_item_one_entry = Entry(edit_location_frame, width=25)
            alt_item_one_entry.grid(row=5, column=1, columnspan=2, stick=W, pady=(20,0))
            alt_item_one_entry.insert(0, selection_vals[5])
            
            alt_item_one_prim_check_var = IntVar()
            alt_item_one_primary_check = Checkbutton(edit_location_frame, text="Primary", variable=alt_item_one_prim_check_var)
            alt_item_one_primary_check.grid(row=5, column=3, pady=(20,0))

            alt_item_one_qty_label = Label(edit_location_frame, text="Item #2 Qty: ")
            alt_item_one_qty_label.grid(row=6, column=0, pady=(20, 0))

            alt_item_one_qty_entry = Entry(edit_location_frame, width=25)
            alt_item_one_qty_entry.grid(row=6, column=1, columnspan=2, stick=W, pady=(20,0))
            alt_item_one_qty_entry.insert(0, selection_vals[6])
            
            alt_item_two_label = Label(edit_location_frame, text="Item #3: ")
            alt_item_two_label.grid(row=7, column=0, pady=(20, 0))            

            alt_item_two_entry = Entry(edit_location_frame, width=25)
            alt_item_two_entry.grid(row=7, column=1, columnspan=2, stick=W, pady=(20,0))
            alt_item_two_entry.insert(0, selection_vals[7])
            
            alt_item_two_prim_check_var = IntVar()
            alt_item_two_primary_check = Checkbutton(edit_location_frame, text="Primary", variable=alt_item_two_prim_check_var)
            alt_item_two_primary_check.grid(row=7, column=3, pady=(20,0))

            alt_item_two_qty_label = Label(edit_location_frame, text="Item #3 Qty: ")
            alt_item_two_qty_label.grid(row=8, column=0, pady=(20, 0))

            alt_item_two_qty_entry = Entry(edit_location_frame, width=25)
            alt_item_two_qty_entry.grid(row=8, column=1, columnspan=2, stick=W, pady=(20,0))
            alt_item_two_qty_entry.insert(0, selection_vals[8])
            
            location_list = [location_entry, location_zone_entry, location_utn_entry, item_entry, item_qty_entry, alt_item_one_entry, alt_item_one_qty_entry, alt_item_two_entry, alt_item_two_qty_entry]
            primary_vars = [item_prim_check_var, alt_item_one_prim_check_var, alt_item_two_prim_check_var]
            location_update_btn = Button(edit_location_frame, text="Update Location", width=42, command=lambda: update_location_database(master_info=self.user_info, box=edit_location_box, location_info=location_list, primary_vars=primary_vars, mode='edit'))
            location_update_btn.grid(row=9, column=0, columnspan=4, stick=E, pady=(20,0))
        pass

## ORDER SCREEN FUNCTIONS COMPLETE ##        

    def generate_order_screen(self, kill_frame):
        temp_frame = kill_frame
        self.clear_screen(temp_frame)

        order_weight = 0
        ### FRAME ONE ###
        order_frame_one = Frame(self.root)
        order_frame_one.grid(row=0, column=0, padx=(40, 0))

        search_entry = Entry(order_frame_one, width=46)
        search_entry.grid(row=0, column=0, columnspan=5, sticky=W, padx=(2,0), pady=(10,0))

        search_btn = Button(order_frame_one, width=13, text="SEARCH", command=lambda: self.order_search(box=item_box, entry=search_entry))
        search_btn.grid(row=0, column=3, columnspan=3, sticky=E, pady=(10,0))

        brs_sort = Button(order_frame_one, text='BRS', width=8, command=lambda: self.sort_items(box=item_box, tag='BRS'))
        brs_sort.grid(row=1, column=0, pady=(10, 0))
        
        mbrs_sort = Button(order_frame_one, text='MBRS', width=8, command=lambda: self.sort_items(box=item_box, tag='MBRS'))
        mbrs_sort.grid(row=1, column=1, pady=(10, 0))
        
        cass_sort = Button(order_frame_one, text='CAS', width=8, command=lambda: self.sort_items(box=item_box, tag='CAS'))
        cass_sort.grid(row=1, column=2, pady=(10, 0))

        cons_sort = Button(order_frame_one, text='CONS', width=8, command=lambda: self.sort_items(box=item_box, tag='CONS'))
        cons_sort.grid(row=1, column=3, pady=(10, 0))

        duct_sort = Button(order_frame_one, text='DUCT', width=8, command=lambda: self.sort_items(box=item_box, tag='DUCT'))
        duct_sort.grid(row=1, column=4, pady=(10, 0))

        flex_sort = Button(order_frame_one, text='FLEXX', width=8, command=lambda: self.sort_items(box=item_box, tag='FLEXX'))
        flex_sort.grid(row=1, column=5, pady=(10, 0))

        flr_sort = Button(order_frame_one, text='FLR', width=8, command=lambda: self.sort_items(box=item_box, tag='FLR'))
        flr_sort.grid(row=2, column=0)

        livs_sort = Button(order_frame_one, text='LIVS', width=8, command=lambda: self.sort_items(box=item_box, tag='LIVS'))
        livs_sort.grid(row=2, column=1)

        livv_sort = Button(order_frame_one, text='LIVV', width=8, command=lambda: self.sort_items(box=item_box, tag='LIVV'))
        livv_sort.grid(row=2, column=2)

        multi_sort = Button(order_frame_one, text='MULTI', width=8, command=lambda: self.sort_items(box=item_box, tag='MULTI'))
        multi_sort.grid(row=2, column=3)
        
        multiu_sort = Button(order_frame_one, text='MULTIU', width=8, command=lambda: self.sort_items(box=item_box, tag='MULTIU'))
        multiu_sort.grid(row=2, column=4)
        
        sap_sort = Button(order_frame_one, text='SAP', width=8, command=lambda: self.sort_items(box=item_box, tag='SAP'))
        sap_sort.grid(row=2, column=5)

        umat_sort = Button(order_frame_one, text='UMAT', width=8, command=lambda: self.sort_items(box=item_box, tag='UMAT'))
        umat_sort.grid(row=3, column=0)

        vir_sort = Button(order_frame_one, text='VIR', width=8, command=lambda: self.sort_items(box=item_box, tag='VIR'))
        vir_sort.grid(row=3, column=1)

        viru_sort = Button(order_frame_one, text='VIRU', width=8, command=lambda: self.sort_items(box=item_box, tag='VIRU'))
        viru_sort.grid(row=3, column=2)

        vir3_sort = Button(order_frame_one, text='3VIR', width=8, command=lambda: self.sort_items(box=item_box, tag='3VIR'))
        vir3_sort.grid(row=3, column=3)

        lns_sort = Button(order_frame_one, text='LNS', width=8, command=lambda: self.sort_items(box=item_box, tag='LS'))
        lns_sort.grid(row=3, column=4)

        other_sort = Button(order_frame_one, text='OTHER', width=8, command=lambda: self.sort_items(box=item_box, tag='OTHER'))
        other_sort.grid(row=3, column=5)

        
        in_sort = Button(order_frame_one, text='Indoor', width=26, command=lambda: self.sort_items(box=item_box, tag='INDOOR', type=TRUE))
        in_sort.grid(row=4, column=0, columnspan=3, stick=W)
        
        out_sort = Button(order_frame_one, text='Outdoor', width=26, command=lambda: self.sort_items(box=item_box, tag='OUTDOOR', type=TRUE))
        out_sort.grid(row=4, column=3, columnspan=3, stick=E)


        # ITEM LIST BOX
        item_list = warehouse_inquiry()
        list_var = Variable(value=item_list)
        item_box = Listbox(order_frame_one, listvariable=list_var, height=33, width=65, selectmode=SINGLE)
        item_box.grid(row=5, column=0, columnspan=6, pady=(10,0))
        scrollbar = ttk.Scrollbar(order_frame_one, orient=VERTICAL, command=item_box.yview)
        item_box['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=5, column=6, stick='ns', pady=(10,0))

        back_btn = Button(order_frame_one, text="Back", width=10, command=lambda: self.back_to_menu_screen(order_frame_one, order_frame_two, order_frame_three))
        back_btn.grid(row=6, column=0, columnspan=2, stick=W, pady=(10,0))

        ### FRAME TWO ###
        order_frame_two = Frame(self.root, width=140)
        order_frame_two.grid(row=0, column=1, padx=15)
        
        qty_lbl = Label(order_frame_two, text='Qty: ')
        qty_lbl.grid(row=0, column=0, padx=10)

        qty_entry = Entry(order_frame_two, width=10)
        qty_entry.grid(row=0, column=1)
        qty_entry.insert(0, '1')

        add_btn = Button(order_frame_two, text="Add", width=14, command=lambda: self.add_to_order(tree=order_tree, box=item_box, entry=qty_entry))
        add_btn.grid(row=1, column=0, columnspan=2, padx=(15,0), pady=20)

        remove_btn = Button(order_frame_two, text="Remove", width=14, command=lambda: self.remove_order_item(tree=order_tree, select='s'))
        remove_btn.grid(row=2, column=0, columnspan=2, padx=(15,0))

        ### FRAME THREE ###
        order_frame_three = Frame(self.root)
        order_frame_three.grid(row=0, column=2, padx=(10), pady=(5,0))

        order_num_label = Label(order_frame_three, text="Order #: ")
        order_num_label.grid(row=0, column=0, pady=10, padx=(0, 5), stick=E)

        order_num_entry = Entry(order_frame_three, width=19)
        order_num_entry.grid(row=0, column=1, sticky=W)

        order_history_btn = Button(order_frame_three, text='Order History', command=self.get_order_history)
        order_history_btn.grid(row=0, column=2, stick=E)

        order_tree = ttk.Treeview(order_frame_three, height=31)
        order_tree['columns'] = ("qty", "item", "weight", "pallet")

        order_tree.column("#0", width=0, stretch=NO)
        order_tree.column("qty", anchor=N, width=65)
        order_tree.column("item", anchor=W, width=155)
        order_tree.column("weight", anchor=E, width=85)
        order_tree.column("pallet", anchor=N, width=65)
        
        order_tree.heading("#0", text="")
        order_tree.heading("qty", text="Qty", anchor=N)
        order_tree.heading("item", text="Item", anchor=N)
        order_tree.heading("weight", text="Weight", anchor=N)
        order_tree.heading("pallet", text="Pallet", anchor=N)
        order_tree.grid(row=1, column=0, columnspan=3)

        clear_btn = Button(order_frame_three, text='Clear', width=10, command=lambda: self.remove_order_item(tree=order_tree, select='a'))
        clear_btn.grid(row=2, column=0, columnspan=2, stick=W, pady=10)

        generate_btn = Button(order_frame_three, text="Generate", command=lambda: self.generate_order(tree=order_tree, order_entry=order_num_entry), width=10)
        generate_btn.grid(row=2, column=2, pady=10, sticky="E")
       
    def add_to_order(self, tree, box, entry):
        order_tree = tree
        item_box = box
        qty_entry = entry
        cur = item_box.curselection()
        try:
            item = item_box.get(cur)
        except Exception:
            return
        qty = qty_entry.get()
        try:
            num_qty = int(qty)
        except ValueError:
            return
        for child in order_tree.get_children():
            if item == order_tree.item(child)['values'][1]:
                child_index = order_tree.index(child)
                values = order_tree.item(child)['values']
                new_qty = int(values[0]) + num_qty
                item_info = warehouse_inquiry(tag='weight', selection=item, quantity=new_qty)
                order_tree.delete(child)
                order_tree.insert(parent='', index=child_index, values=(new_qty, item, item_info[0], item_info[1]))        
                return
        item_info = warehouse_inquiry(tag='weight', selection=item, quantity=qty)

        order_tree.insert(parent='', index='end', values=(qty, item, item_info[0], item_info[1]))

    def order_search(self, box, entry):
        item_box = box
        item_box.delete(0,END)
        search_var = entry.get()
        sort_list = warehouse_inquiry(search=search_var)
        for item in sort_list:
            item_box.insert('end', item)

    def sort_items(self, box, tag, type=FALSE):
        item_box = box
        item_box.delete(0,END)
        if type:
            sort_type = tag
            sort_list = warehouse_inquiry(type=sort_type)
            for item in sort_list:
                item_box.insert('end', item)
            return
        sort_tag = tag
        sort_list = warehouse_inquiry(tag=sort_tag)
        for item in sort_list:
            item_box.insert('end', item)
        return

    def remove_order_item(self, tree, select):
        order_tree = tree
        if select == 's':
            try:
                selected = order_tree.selection()[0]
                order_tree.delete(selected)
                return
            except Exception as e:
                return
        if select == 'a':
            for item in order_tree.get_children():
                order_tree.delete(item)
            return

    def generate_order(self, tree, order_entry):
        order_number = order_entry.get().upper()
        order_nums = note_inquiry(note_type='order', mode='order_nums')
        # CHECK FOR EXISTING ORDER NUMBER
        if order_number in order_nums:
            messagebox.showwarning(title="Error", message=f"Order Number Already Exists: {order_number}")
            return
        order_tree = tree
        item_weight = 0
        pallet_count = 0
        item_count = 0
        order_items = ''
        order_items_list = []
        for child in order_tree.get_children():
            item_count += order_tree.item(child)['values'][0]
            order_items += f"{order_tree.item(child)['values'][1]} x{order_tree.item(child)['values'][0]} \n"
            order_items_list.insert(len(order_items_list), (order_tree.item(child)['values'][1], order_tree.item(child)['values'][0]))
            item_weight += order_tree.item(child)['values'][2]
            pallet_count += float(order_tree.item(child)['values'][3])
            # print(order_tree.item(child)['values'])
        pallets = math.ceil(pallet_count)
        pallet_weight = pallets * 30
        final_weight = pallet_weight + item_weight

        order_notes = f'Pieces: {item_count} \nWeight: {final_weight} \nPallet Count: {pallets}'

        order_box = Toplevel(self.root)
        order_box.geometry('300x300')
        order_box.title("Order Details")

        order_details_frame = Frame(order_box)
        order_details_frame.pack(pady=(15,0))

        order_details_label = Label(order_details_frame, text=f'ORDER#: {order_number}')
        order_details_label.grid(row=0, column=0, pady=20, padx=(15, 0))

        item_count_label = Label(order_details_frame, text=f"Piece Count:")
        item_count_label.grid(row=1, column=0, padx=(0,0), sticky=W)

        item_count_value_label = Label(order_details_frame, text=f"{item_count}")
        item_count_value_label.grid(row=1, column=1, sticky=E)

        pallet_count_label = Label(order_details_frame, text=f"Est. Pallet Count:")
        pallet_count_label.grid(row=2, column=0, padx=(0,0), sticky=W)

        pallet_count_value_label = Label(order_details_frame, text=f"{pallets}")
        pallet_count_value_label.grid(row=2, column=1, sticky=E)

        weight_count_label = Label(order_details_frame, text=f"Est Final Weight:")
        weight_count_label.grid(row=3, column=0, padx=(0,0), sticky=W)

        weight_count_value_label = Label(order_details_frame, text=f"{final_weight}")
        weight_count_value_label.grid(row=3, column=1, sticky=E)

        save_order_btn = Button(order_details_frame, text='Save Order', width=10, command=lambda: add_note(note_type='order_create', user=self.user_info, order_num=order_number, item_notes=order_items, notes=order_notes, item_list=order_items_list, box=order_box))
        save_order_btn.grid(row=4, column=0, columnspan=2, pady=(50,0), sticky=N)

    def get_order_history(self):
        order_list = note_inquiry(note_type='order', mode='order_nums')
        print(order_list)

        if not order_list:
            return

        history_box = Toplevel(self.root)
        history_box.geometry('400x400')
        history_box.title("Order History")
        
        ### LEFT FRAME
        left_frame = Frame(history_box)
        left_frame.grid(row=0, column=0, padx=(10,0), pady=10)

        order_label = Label(left_frame, text='Order List:')
        order_label.grid(row=0, column=0, stick=W)

        order_list_var = Variable(value=order_list)
        order_listbox = Listbox(left_frame, listvariable=order_list_var, width=17, height=22, selectmode=SINGLE)
        order_listbox.grid(row=1, column=0, columnspan=2)
        
        ### CENTER FRAME
        center_frame = Frame(history_box)
        center_frame.grid(row=0, column=1, padx=(5,0), pady=30, stick=N)

        date_label = Label(center_frame, text='Date Created:')
        date_label.grid(row=0, column=0, stick=E, pady=(0,20))

        user_label = Label(center_frame, text='User Creator:')
        user_label.grid(row=1, column=0, stick=E, pady=(0,20))

        piece_label = Label(center_frame, text='Piece #:')
        piece_label.grid(row=2, column=0, stick=E, pady=(0,20))

        weight_label = Label(center_frame, text='Weight:')
        weight_label.grid(row=3, column=0, stick=E, pady=(0,20))

        pallet_label = Label(center_frame, text='Pallet #:')
        pallet_label.grid(row=4, column=0, stick=E, pady=(0,20))

        items_label = Label(center_frame, text='Items:')
        items_label.grid(row=5, column=0, stick=E, pady=(0,20))

        ### RIGHT FRAME
        right_frame = Frame(history_box)
        right_frame.grid(row=0, column=2, stick=N, padx=5, pady=30)

        date_entry = Entry(right_frame, width=26)
        date_entry.grid(row=0, column=0, stick=W, pady=(0,23))

        user_entry = Entry(right_frame, width=26)
        user_entry.grid(row=1, column=0, stick=W, pady=(0,23))

        piece_entry = Entry(right_frame, width=26)
        piece_entry.grid(row=2, column=0, stick=W, pady=(0,23))

        weight_entry = Entry(right_frame, width=26)
        weight_entry.grid(row=3, column=0, stick=W, pady=(0,23))

        pallet_entry = Entry(right_frame, width=26)
        pallet_entry.grid(row=4, column=0, stick=W, pady=(0,24))

        items_listbox = Listbox(right_frame, width=26, height=8)
        items_listbox.grid(row=5, column=0, stick=W)

        def update_order_box(selection):
            try:
                cur = order_listbox.curselection()[0]
                date_entry.config(state=NORMAL)
                date_entry.delete(0, END)
                user_entry.config(state=NORMAL)
                user_entry.delete(0, END)
                piece_entry.config(state=NORMAL)
                piece_entry.delete(0, END)
                weight_entry.config(state=NORMAL)
                weight_entry.delete(0, END)
                pallet_entry.config(state=NORMAL)
                pallet_entry.delete(0, END)
                items_listbox.config(state=NORMAL)
                items_listbox.delete(0, END)
            except Exception as e:
                print(e)
                return

            select_order = order_listbox.get(cur)
            order_details = note_inquiry(note_type='order', mode='order_details', order=select_order)
            temp_date = str(order_details[0])
            temp_details = order_details[4].split('\n')
            pcs = temp_details[0].split(':')[1].strip()
            lbs = temp_details[1].split(':')[1].strip()
            plt = temp_details[2].split(':')[1].strip()        
            date_entry.insert(0, temp_date)
            date_entry.config(state=DISABLED)
            user_entry.insert(0, order_details[1])
            user_entry.config(state=DISABLED)
            piece_entry.insert(0, pcs)
            piece_entry.config(state=DISABLED)
            weight_entry.insert(0, lbs)
            weight_entry.config(state=DISABLED)
            pallet_entry.insert(0, plt)
            pallet_entry.config(state=DISABLED)
            temp_items = order_details[3].split('\n')
            count = 0
            for item in temp_items:
                items_listbox.insert(count, item)
                count += 1
            items_listbox.config(state=DISABLED)
            return

        order_listbox.bind('<<ListboxSelect>>', update_order_box)

        # get list of orders
        # fill box on left with order numbers
        # when order is clicked
            # populate box on right with order details