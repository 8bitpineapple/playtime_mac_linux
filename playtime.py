import sqlite3
import os
import sys
import shutil
from sys import platform

# Helper function to output the header lines
def print_header():
    print("Playtime v1.1 - OnionUI Activity Tracker Utilities")
    print("Report Issues: https://github.com/maxpereira/playtime\n")

# Helper function to clear the screen output
def clear_screen():
    os_name = os.name
    if os_name == 'posix':  # Linux and macOS
        os.system('clear')
    elif os_name == 'nt':  # Windows
        os.system('cls')
    else:
        print("Screen clearing not supported for this operating system.")

clear_screen()
print_header()
dbfile = "./play_activity_db.sqlite"
conn=sqlite3.connect(dbfile)
c=conn.cursor()
# Merge play activity entries
def merge_entries():
    src_game_id = input("\nType the SOURCE game ID (this will be merged with the DESTINATION game ID): ")
    dest_game_id = input("Type the DESTINATION game ID: ")
    
    c.execute("SELECT name FROM rom WHERE id = ?", (src_game_id,))
    selected_names = c.fetchall()
    src_game_name = ', '.join(name[0] for name in selected_names)
    
    c.execute("SELECT name FROM rom WHERE id = ?", (dest_game_id,))
    selected_names = c.fetchall()
    dest_game_name = ', '.join(name[0] for name in selected_names)
    
    answer = input("\nConfirm merging entries for "+src_game_name+" into "+dest_game_name+"? (y/n): ")
    if answer.lower() in ["y","yes"]:
        c.execute("UPDATE play_activity SET rom_id = "+dest_game_id+" WHERE rom_id = "+src_game_id)
        conn.commit()
        
        clear_screen()
        print_header()
        print("The play entries were merged!")
        input("Press Enter to return to menu...")
    elif answer.lower() in ["n","no"]:
        print("Returning to menu")
    else:
        print("Invalid entry - returning to menu")

# View all play activity entries
def view_entries():
    clear_screen()
    print_header()
    c.execute("SELECT * FROM play_activity")
    
    del_rows = c.fetchall()
    result_dict = {}

    # Sum the play activity entries and count occurrences based on the rom_id
    for item in del_rows:
        key = item[0]
        value = item[1]
        result_dict[key] = result_dict.get(key, {"sum": 0, "count": 0})
        result_dict[key]["sum"] += value
        result_dict[key]["count"] += 1

    print("Listing all play activity entries:\n")

    # Display the play activity entries
    for key, values in result_dict.items():
        c.execute("SELECT name FROM rom WHERE id = ?", (key,))
        selected_names = c.fetchall()
        selected_names_first_entry = ', '.join(name[0] for name in selected_names)
        print(f"ID {key} - {selected_names_first_entry}: {values['sum']} seconds, {values['count']} plays")
    
    if merge_mode == 1:
        merge_entries()
    else:
        input("\nPress Enter to return to menu...")    

# Handle deletion of rows based on mode chosen
def del_entries():
    clear_screen()
    print_header()
    del_choice = 0
    
    if del_mode == 1:
        del_choice = input("Enter second count for deletion threshold: ")
        c.execute("SELECT * FROM play_activity WHERE rom_id IN ( SELECT rom_id FROM play_activity GROUP BY rom_id HAVING SUM(play_time) < "+str(del_choice)+")")
    elif del_mode == 2:
        del_choice = input("Enter play count for deletion threshold: ")
        c.execute("SELECT * FROM play_activity WHERE rom_id IN ( SELECT rom_id FROM play_activity GROUP BY rom_id HAVING COUNT(*) <= "+str(del_choice)+")")
    elif del_mode == 3:
        c.execute('SELECT name FROM rom')

        names = c.fetchall()
        count = 1
        for name in names:
            print(str(count) + ": "+name[0])
            count = count+1
    
        del_choice = input("\nEnter the ID of the game to delete: ")
        c.execute("SELECT * FROM play_activity WHERE rom_id = "+del_choice)

    del_rows = c.fetchall()
    result_dict = {}

    # Sum the play activity entries and count occurrences based on the rom_id
    for item in del_rows:
        key = item[0]
        value = item[1]
        result_dict[key] = result_dict.get(key, {"sum": 0, "count": 0})
        result_dict[key]["sum"] += value
        result_dict[key]["count"] += 1

    clear_screen()
    print_header()
    print("The following entries will be deleted:\n")

    # Display the play activities entries to be deleted
    for key, values in result_dict.items():
        c.execute("SELECT name FROM rom WHERE id = ?", (key,))
        selected_names = c.fetchall()
        selected_names_first_entry = ', '.join(name[0] for name in selected_names)
        print(f"{selected_names_first_entry}: {values['sum']} seconds, {values['count']} plays")

    # Ask for confirmation then delete the play activity entries
    answer = input("\nContinue? (y/n): ")
    if answer.lower() in ["y","yes"]:
        if del_mode == 1:
            c.execute("DELETE FROM play_activity WHERE rom_id IN ( SELECT rom_id FROM play_activity GROUP BY rom_id HAVING SUM(play_time) < "+str(del_choice)+")")
        elif del_mode == 2:
            c.execute("DELETE FROM play_activity WHERE rom_id IN ( SELECT rom_id FROM play_activity GROUP BY rom_id HAVING COUNT(*) <= "+str(del_choice)+")")
        elif del_mode == 3:
            c.execute("DELETE FROM play_activity WHERE rom_id = "+del_choice)
        conn.commit()
        
        clear_screen()
        print_header()
        print("The play entries were deleted!")
        input("Press Enter to return to menu...")
    elif answer.lower() in ["n","no"]:
        print("Returning to menu")
    else:
        print("Invalid entry - returning to menu")

# Show the main menu
while True:
    clear_screen()
    print_header()
    merge_mode = 0
    print("1. View all play activity entries")
    print("2. Delete play activity entries under X seconds of playtime")
    print("3. Delete play activity entries under X plays")
    print("4. Delete all play activity entries for a particular game")
    print("5. Merge play activity entries from one game into another")
    print("6. Exit")

    menu_choice = input("\nChoose an option: ")
    
    if menu_choice == '1':
        view_entries()
    elif menu_choice == '2':
        del_mode = 1
        del_entries()
    elif menu_choice == '3':
        del_mode = 2
        del_entries()
    elif menu_choice == '4':
        del_mode = 3
        del_entries()
    elif menu_choice == '5':
        merge_mode = 1
        view_entries()
    elif menu_choice == '6':
        conn.close()
        print("Closing database connection and exiting...")
        break
    else:
        print("Invalid choice.")        
