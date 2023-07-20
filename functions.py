import concurrent
import datetime
import time
from tkinter import ttk, messagebox
import tkinter as tk
import requests
from concurrent.futures import ThreadPoolExecutor

# create global variables
public_profiles = []
limited_profiles = []
private_profiles = []
user_want_stop = False


def add_information_text_widget(text_widget):
    """if file with battle-tags exist > add this battle-tags in text-widget
       if file with battle-tags not exist > it is ignored"""

    # add battle tags in text-widget
    try:
        with open('saved_battle_tags.json', 'r') as f:
            data = f.read().strip()
            if data:
                text_widget.insert('1.0', data)

    # when file not exist
    except FileNotFoundError:
        pass


def create_scrollbar(frame, widget):
    """It creates scrollbar"""
    scrollbar = ttk.Scrollbar(frame, command=widget.yview)
    scrollbar.pack(side='right', fill='y', pady=10)
    widget.config(yscrollcommand=scrollbar.set)


def save_button_click(text_widget):
    """Saves information from text-widget"""

    # get information from text-widget
    data = text_widget.get('1.0', tk.END)

    # save the information
    with open('saved_battle_tags.json', 'w') as f:
        f.write(data)


def links_button_click(save_button, table, text_frame, text_widget):
    """Open text-widget, change "Link" button to "Save" button"""

    # flag for stop check
    global user_want_stop
    user_want_stop = True

    # change button
    save_button.configure(text='Save', command=lambda: save_button_click(text_widget))

    # remove table-widget
    table.pack_forget()

    # open text-widget
    text_frame.pack(side="left", fill="both", expand=True)


def create_table_widget(table):
    """Create table-widget, columns = 9
       for 800x600, full length = 796
       if you set the minimum length for all columns, full length = 598"""

    # delete information from the table if it exists
    if table.get_children():
        table.delete(*table.get_children())

    # set parameters
    table.column('Status', minwidth=47, width=69, anchor='center', stretch=False)
    table.column('Nickname', minwidth=80, width=102, anchor='center', stretch=False)
    table.column('Season', minwidth=47, width=69, anchor='center', stretch=False)
    table.column('Tank', minwidth=87, width=109, anchor='center', stretch=False)
    table.column('Damage', minwidth=87, width=109, anchor='center', stretch=False)
    table.column('Support', minwidth=87, width=109, anchor='center', stretch=False)
    table.column('Play time', minwidth=72, width=94, anchor='center', stretch=False)
    table.column('Win rate', minwidth=54, width=76, anchor='center', stretch=False)
    table.column('KD', minwidth=37, width=59, anchor='center', stretch=False)

    # push table and columns
    table.heading('Status', text='Status')
    table.heading('Nickname', text='Nickname')
    table.heading('Season', text='Season')
    table.heading('Tank', text='Tank')
    table.heading('Damage', text='Damage')
    table.heading('Support', text='Support')
    table.heading('Play time', text='Play time')
    table.heading('Win rate', text='Win rate')
    table.heading('KD', text='KD')
    table.pack(fill='both', expand=True)

    # set colors for certain tags
    table.tag_configure('Limited', background='#460000')
    table.tag_configure('Private', background='#460000')


def check_button_click(check_button, save_button, text_frame, table, text_widget):
    """Performs a series of actions to retrieve information about each user entered in the text widget field"""

    global user_want_stop
    check_button.configure(state='disabled')  # block button

    try:
        with open('saved_battle_tags.json', 'r') as file:

            # change button
            save_button.configure(text='Links', command=lambda: links_button_click(save_button, table, text_frame, text_widget))

            # change widget on table
            text_frame.pack_forget()
            create_table_widget(table)

            # push information on table
            battle_tags = file.read().strip()
            if battle_tags:
                battle_tags = battle_tags.split(',')
                battle_tags = [unit.strip() for unit in battle_tags if unit.strip() != '']
                if not user_want_stop:
                    get_content(battle_tags, table)
            check_button.configure(state='normal')  # unblock button

    # when file with battle-tags not exist
    except FileNotFoundError:
        check_button.configure(state='normal')  # unblock button
        if not user_want_stop:
            ThreadPoolExecutor().submit(lambda: error_window('Error', 'List of battle-tags is empty!\nPlease click "save" button if you have not already'))

    user_want_stop = False


def get_content(battle_tags, table):
    """Get content > record on right order > push to table"""

    global user_want_stop

    if not battle_tags:

        # exit if needed
        if user_want_stop:
            return

        # error no battle tags
        ThreadPoolExecutor().submit(lambda: error_window('Error', 'List of battle tags is empty!'))

    else:

        # clear content from lists
        private_profiles.clear()
        public_profiles.clear()
        limited_profiles.clear()

        def request_processing(tag):
            """add information in 3 lists"""
            information = process_get_content(tag)

            # if needed exit
            if user_want_stop:
                return

            # record 3 different types to the relevant lists
            if information:
                if information[0] == 'Public':
                    public_profiles.append(information)
                elif information[0] == 'Limited':
                    limited_profiles.append(information)
                else:
                    private_profiles.append(information)

        # if code have problems change count max_workers, recommend maximum 6
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(request_processing, i) for i in battle_tags]

            # handle exceptions if any occur during the execution of threads
            for future, battle_tag in zip(futures, battle_tags):
                try:
                    future.result()
                except Exception as e:
                    ThreadPoolExecutor().submit(lambda: error_window(f'{battle_tag}', f'Something went wrong: {e}'))

        if user_want_stop:
            return

        # push content in the right order
        for unit in public_profiles:
            if user_want_stop:
                return
            table.insert('', tk.END, values=unit, tags=['Public'])
        for unit in limited_profiles:
            if user_want_stop:
                return
            table.insert('', tk.END, values=unit, tags=['Limited'])
        for unit in private_profiles:
            if user_want_stop:
                return
            table.insert('', tk.END, values=unit, tags=['Private'])


def process_get_content(unit):
    """Get content from API and return this data"""

    global user_want_stop

    # variables
    nickname = unit.split("-")[0]
    tank_rating = '-'
    damage_rating = '-'
    support_rating = '-'
    time_played = '-'
    win_rate = '-'
    kd = '-'
    season = '-'

    if user_want_stop:
        return

    # get content from API
    response = requests.get(f'https://overfast-api.tekrop.fr/players/{unit}').json()

    try:
        status = str(response['summary']['privacy']).capitalize()
        if status == 'Public':

            if type(response['summary']['competitive']) is dict:  # this return "None" if no competitive
                try:

                    # stats
                    season = response['summary']['competitive']['pc']['season']
                    stats = response['stats']['pc']['competitive']['career_stats']['all-heroes']
                    eliminations = next(stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'eliminations')
                    deaths = next(stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'deaths')
                    sec_played = next(stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'time_played')
                    games_played = next(stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'games_played')
                    games_won = next(stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'games_won')

                    # stats calculation
                    time_played = f'{sec_played // 3600}hr {(sec_played % 3600) // 60}min'
                    win_rate = f"{(games_won / games_played) * 100:.2f}%"
                    kd = f'{eliminations / deaths:.2f}'

                    # tank rating
                    if type(response['summary']['competitive']['pc']['tank']) is dict:
                        tank_division = str(response['summary']['competitive']['pc']['tank']['division']).capitalize()
                        tank_division_tier = str(response['summary']['competitive']['pc']['tank']['tier'])
                        tank_rating = tank_division + '-' + tank_division_tier

                    if user_want_stop:
                        return

                    # damage rating
                    if type(response['summary']['competitive']['pc']['damage']) is dict:
                        damage_division = str(response['summary']['competitive']['pc']['damage']['division']).capitalize()
                        damage_division_tier = str(response['summary']['competitive']['pc']['damage']['tier'])
                        damage_rating = damage_division + '-' + damage_division_tier

                    # support rating
                    if type(response['summary']['competitive']['pc']['support']) is dict:
                        support_division = str(response['summary']['competitive']['pc']['support']['division']).capitalize()
                        support_division_tier = str(response['summary']['competitive']['pc']['support']['tier'])
                        support_rating = support_division + '-' + support_division_tier

                    return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

                # possibly could happen if no 'pc' stats
                except Exception as e:
                    if user_want_stop:
                        return
                    ThreadPoolExecutor().submit(lambda: error_window(f'{unit}', f'Something went wrong: {e}'))

            else:  # no competitive
                status = 'Limited'
                return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

        # profile is closed
        else:
            return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

    # it happens when could not get blizzard page
    except KeyError:
        if user_want_stop is not True:
            ThreadPoolExecutor().submit(lambda: error_window('Error', f'{unit}: Timeout exceeded.'))
        return


def error_window(title: str, text: str):
    return messagebox.showerror(title, text)
