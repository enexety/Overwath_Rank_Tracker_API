import os
import signal
import tkinter as tk
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor

import functions

# TODO:
#  1. Question window before exit app > save information in text-widget or not
#  2. Multitasking
#  3. Fix error > Click check > Click Exit
#  4. Fix error > Click check > Click Links

# create main window
window = tk.Tk()
window.title('Overwatch Rank Tracker')
window.geometry('800x600')
window.configure(bg='#2B2B2B')
window.minsize(800, 600)

# set style for window
style = ttk.Style(window)
style.theme_use("clam")
style.configure('Treeview', background='#2B2B2B', foreground="white", fieldbackground="#2B2B2B")

# set table
table = ttk.Treeview(window, columns=['Status', 'Nickname', 'Season', 'Tank', 'Damage', 'Support', 'Play time', 'Win rate', 'KD'], show='headings', height=26)

# set size and centering
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_cord = int((screen_width / 2) - (800 / 2))
y_cord = int((screen_height / 2) - (600 / 2))
window.geometry("{}x{}+{}+{}".format(800, 600, x_cord, y_cord))

# set button_frame
button_frame = tk.Frame(window, bg='#2B2B2B')
button_frame.pack(side='bottom', fill='x')

# set text_frame for text_widget
text_frame = tk.Frame(window, bg="#2B2B2B")
text_frame.pack(side="left", fill="both", expand=True)

# set buttons
check_button = tk.Button(button_frame, text='Check', font=('Calibri', 17, 'bold'), pady=3, width=16,
                         command=lambda: ThreadPoolExecutor().submit(lambda: functions.check_button_click(check_button, save_button, text_frame, table, text_widget)))
save_button = tk.Button(button_frame, text='Save', font=('Calibri', 17, 'bold'), pady=3, width=16, command=lambda: functions.save_button_click(text_widget))
exit_button = tk.Button(button_frame, text='Exit', font=('Calibri', 17, 'bold'), pady=3, width=16, command=lambda: os.kill(os.getpid(), signal.SIGTERM))
check_button.pack(side='left', fill='x', expand=True)
save_button.pack(side='left', fill='x', expand=True)
exit_button.pack(side='left', fill='x', expand=True)

# create text-widget
text_widget = tk.Text(text_frame, font=('Calibri', 13, 'bold'), fg='#A0A0A0', insertbackground='white', padx=10, pady=15, bg="#2B2B2B", relief='flat')
text_widget.pack(side='left', fill='both', expand=True)
text_widget.pack(side='left', fill='both', expand=True)
functions.add_information_text_widget(text_widget)
functions.create_scrollbar(text_frame, text_widget)

# launch
window.mainloop()
