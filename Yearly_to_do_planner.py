import tkinter as tk
from tkinter import ttk
from datetime import date, datetime
import calendar
import json
import os


DATA_FILE = "yearly_tasks.json"


# Old-money style palette
BG_MAIN      = "#f5f0e8"   # warm cream
BG_PANEL     = "#f9f4ec"   # lighter cream
BG_HEADER    = "#1f3d32"   # deep green
FG_HEADER    = "#f5f0e8"   # cream text
ACCENT       = "#c9a36b"   # muted gold
ACCENT_DARK  = "#8b6b36"
TEXT_MAIN    = "#1f1a17"
TASK_ROW_ODD = "#f9f4ec"
TASK_ROW_EVN = "#efe4d4"


SCOLD_TEXT = "You said you'd do this by now, but it's still waiting. Lock in and finish it."


class TimeSelector:
    def __init__(self, parent, title="Select Time", initial_time="00:00"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("300x200")
        self.window.configure(bg=BG_PANEL)
        self.window.transient(parent)
        self.window.grab_set()


        self.selected_time = tk.StringVar(value=initial_time)


        # Hour selector - 00 to 23
        tk.Label(self.window, text="Hour:", bg=BG_PANEL, fg=TEXT_MAIN,
                 font=("Georgia", 10, "bold")).pack(pady=10)
        self.hour_var = tk.StringVar(value=initial_time[:2])
        hour_combo = ttk.Combobox(
            self.window, textvariable=self.hour_var,
            values=[f"{h:02d}" for h in range(24)],
            width=5, state="readonly", font=("Georgia", 10)
        )
        hour_combo.pack(pady=5)


        # Minute selector - 00 to 59
        tk.Label(self.window, text="Minute:", bg=BG_PANEL, fg=TEXT_MAIN,
                 font=("Georgia", 10, "bold")).pack(pady=(10, 0))
        self.minute_var = tk.StringVar(value=initial_time[3:])
        minute_combo = ttk.Combobox(
            self.window, textvariable=self.minute_var,
            values=[f"{m:02d}" for m in range(60)],
            width=5, state="readonly", font=("Georgia", 10)
        )
        minute_combo.pack(pady=5)


        # Buttons
        btn_frame = tk.Frame(self.window, bg=BG_PANEL)
        btn_frame.pack(pady=20)


        tk.Button(
            btn_frame, text="OK", command=self.ok_pressed,
            bg=ACCENT, fg="white", font=("Georgia", 10, "bold"),
            bd=0, padx=20, pady=5
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame, text="Cancel", command=self.window.destroy,
            bg=BG_HEADER, fg=FG_HEADER, font=("Georgia", 10),
            bd=0, padx=20, pady=5
        ).pack(side=tk.LEFT, padx=5)


        hour_combo.bind("<<ComboboxSelected>>", self.update_time)
        minute_combo.bind("<<ComboboxSelected>>", self.update_time)


    def update_time(self, event=None):
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        self.selected_time.set(f"{hour}:{minute}")


    def ok_pressed(self):
        self.window.destroy()


    def get_time(self):
        self.window.wait_window()
        return self.selected_time.get()


class YearlyTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yearly Todo Planner")
        self.root.geometry("950x700")
        self.root.configure(bg=BG_MAIN)


        self.tasks_data = self.load_data()
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.current_date = today
        self.current_view = "month"


        os.makedirs("task_data", exist_ok=True)


        self.build_shell()
        self.show_month_view()


    # ---------- data ----------


    def load_data(self):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}


    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.tasks_data, f, indent=2)


    def date_key(self, d):
        return d.isoformat()


    # ---------- shell + add row ----------


    def build_shell(self):
        # Top title bar
        self.title_bar = tk.Frame(self.root, bg=BG_HEADER, height=60)
        self.title_bar.pack(fill=tk.X)


        tk.Label(
            self.title_bar, text="Yearly Planner",
            font=("Georgia", 20, "bold"),
            bg=BG_HEADER, fg=FG_HEADER
        ).pack(side=tk.LEFT, padx=20, pady=10)


        controls = tk.Frame(self.title_bar, bg=BG_HEADER)
        controls.pack(side=tk.RIGHT, padx=20)


        def fancy_btn(text, cmd):
            return tk.Button(
                controls, text=text, command=cmd,
                font=("Georgia", 10),
                bg=BG_HEADER, fg=FG_HEADER,
                activebackground=ACCENT_DARK, activeforeground=FG_HEADER,
                bd=0, padx=10, pady=4,
                highlightthickness=1, highlightbackground=ACCENT
            )


        fancy_btn("Today", self.go_today).pack(side=tk.LEFT, padx=5)
        fancy_btn("Year", self.show_year_view).pack(side=tk.LEFT, padx=5)
        fancy_btn("Month", self.show_month_view).pack(side=tk.LEFT, padx=5)
        fancy_btn("Save", self.save_data).pack(side=tk.LEFT, padx=5)


        # Main area
        self.outer = tk.Frame(self.root, bg=BG_MAIN)
        self.outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)


        # Add-task panel
        self.add_panel = tk.Frame(self.outer, bg=BG_PANEL)
        self.add_panel.pack(fill=tk.X, pady=(0, 10))


        tk.Label(self.add_panel, text="Task", bg=BG_PANEL, fg=TEXT_MAIN,
                 font=("Georgia", 10, "bold")).grid(row=0, column=1, sticky="w", padx=(10, 5), pady=6)
        tk.Label(self.add_panel, text="Start Time", bg=BG_PANEL, fg=TEXT_MAIN,
                 font=("Georgia", 10, "bold")).grid(row=0, column=2, sticky="w", padx=(10, 5))
        tk.Label(self.add_panel, text="End Time", bg=BG_PANEL, fg=TEXT_MAIN,
                 font=("Georgia", 10, "bold")).grid(row=0, column=3, sticky="w", padx=(10, 5))
        tk.Label(self.add_panel, text="Feedback", bg=BG_PANEL, fg=TEXT_MAIN,
                 font=("Georgia", 10, "bold")).grid(row=0, column=4, sticky="w", padx=(10, 5))


        tk.Label(self.add_panel, text="", bg=BG_PANEL).grid(row=1, column=0, padx=(8, 5))


        self.task_entry = tk.Entry(
            self.add_panel, font=("Georgia", 10), width=25,
            bg=BG_MAIN, bd=0, highlightthickness=1,
            highlightbackground=ACCENT
        )
        self.task_entry.grid(row=1, column=1, sticky="we", padx=(10, 5), pady=(0, 8))


        # Start time button
        self.start_time_btn = tk.Button(
            self.add_panel, text="09:00",
            command=self.select_start_time,
            font=("Georgia", 10), width=8,
            bg=ACCENT, fg="white", bd=0
        )
        self.start_time_btn.grid(row=1, column=2, sticky="we", padx=(10, 5), pady=(0, 8))
        self.start_time_text = "09:00"


        # End time button
        self.end_time_btn = tk.Button(
            self.add_panel, text="10:00",
            command=self.select_end_time,
            font=("Georgia", 10), width=8,
            bg=ACCENT, fg="white", bd=0
        )
        self.end_time_btn.grid(row=1, column=3, sticky="we", padx=(10, 5), pady=(0, 8))
        self.end_time_text = "10:00"


        self.feedback_entry = tk.Entry(
            self.add_panel, font=("Georgia", 10), width=25,
            bg=BG_MAIN, bd=0, highlightthickness=1,
            highlightbackground=ACCENT
        )
        self.feedback_entry.grid(row=1, column=4, sticky="we", padx=(10, 5), pady=(0, 8))


        add_btn = tk.Button(
            self.add_panel, text="Add",
            command=self.add_task,
            font=("Georgia", 10),
            bg=ACCENT, fg="white",
            activebackground=ACCENT_DARK, activeforeground="white",
            bd=0, padx=12, pady=4
        )
        add_btn.grid(row=1, column=5, padx=(10, 10))


        self.task_entry.bind("<Return>", lambda e: self.add_task())


        self.add_panel.grid_columnconfigure(1, weight=3)
        self.add_panel.grid_columnconfigure(2, weight=1)
        self.add_panel.grid_columnconfigure(3, weight=1)
        self.add_panel.grid_columnconfigure(4, weight=2)


        # Content frame
        self.content = tk.Frame(self.outer, bg=BG_MAIN)
        self.content.pack(fill=tk.BOTH, expand=True)


    def select_start_time(self):
        selector = TimeSelector(self.root, "Select Start Time", self.start_time_text)
        new_time = selector.get_time()
        self.start_time_text = new_time
        self.start_time_btn.config(text=new_time)


    def select_end_time(self):
        selector = TimeSelector(self.root, "Select End Time", self.end_time_text)
        new_time = selector.get_time()
        self.end_time_text = new_time
        self.end_time_btn.config(text=new_time)


    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()


    # ---------- year view ----------


    def show_year_view(self):
        self.current_view = "year"
        self.clear_content()


        nav = tk.Frame(self.content, bg=BG_MAIN)
        nav.pack(fill=tk.X, pady=(0, 10))


        tk.Button(
            nav, text="← Prev Year", command=self.prev_year,
            font=("Georgia", 10),
            bg=ACCENT, fg="white", bd=0, padx=8, pady=3
        ).pack(side=tk.LEFT, padx=5)


        tk.Label(
            nav, text=str(self.current_year),
            font=("Georgia", 16, "bold"),
            bg=BG_MAIN, fg=TEXT_MAIN
        ).pack(side=tk.LEFT, expand=True)


        tk.Button(
            nav, text="Next Year →", command=self.next_year,
            font=("Georgia", 10),
            bg=ACCENT, fg="white", bd=0, padx=8, pady=3
        ).pack(side=tk.RIGHT, padx=5)


        grid = tk.Frame(self.content, bg=BG_MAIN)
        grid.pack(fill=tk.BOTH, expand=True)


        months = ["Jan", "Feb", "Mar", "Apr",
                  "May", "Jun", "Jul", "Aug",
                  "Sep", "Oct", "Nov", "Dec"]


        for i, name in enumerate(months):
            r, c = divmod(i, 4)
            m = i + 1
            count = self.month_task_count(m)
            bg = "#d8e4dd" if count > 0 else "#e8dfcf"
            btn = tk.Button(
                grid,
                text=f"{name}\n{count} tasks",
                command=lambda mm=m: self.show_month_for(mm),
                font=("Georgia", 12, "bold"),
                width=14, height=4,
                bg=bg, fg=TEXT_MAIN,
                bd=0, highlightthickness=1,
                highlightbackground=ACCENT
            )
            btn.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")


        for c in range(4):
            grid.grid_columnconfigure(c, weight=1)
        for r in range(3):
            grid.grid_rowconfigure(r, weight=1)


    def month_task_count(self, month_num):
        y = self.current_year
        total = 0
        days_in_month = calendar.monthrange(y, month_num)[1]
        for d in range(1, days_in_month + 1):
            k = date(y, month_num, d).isoformat()
            total += len(self.tasks_data.get(k, []))
        return total


    def prev_year(self):
        self.current_year -= 1
        self.show_year_view()


    def next_year(self):
        self.current_year += 1
        self.show_year_view()


    def show_month_for(self, month_num):
        self.current_month = month_num
        self.current_date = date(self.current_year, month_num, 1)
        self.show_month_view()


    # ---------- month view ----------


    def show_month_view(self):
        self.current_view = "month"
        self.clear_content()


        nav = tk.Frame(self.content, bg=BG_MAIN)
        nav.pack(fill=tk.X, pady=(0, 10))


        tk.Button(
            nav, text="← Prev", command=self.prev_month,
            font=("Georgia", 10),
            bg=ACCENT, fg="white", bd=0, padx=8, pady=3
        ).pack(side=tk.LEFT, padx=5)


        tk.Label(
            nav, text=self.current_date.strftime("%B %Y"),
            font=("Georgia", 16, "bold"),
            bg=BG_MAIN, fg=TEXT_MAIN
        ).pack(side=tk.LEFT, expand=True)


        tk.Button(
            nav, text="Next →", command=self.next_month,
            font=("Georgia", 10),
            bg=ACCENT, fg="white", bd=0, padx=8, pady=3
        ).pack(side=tk.RIGHT, padx=5)


        cal_frame = tk.Frame(self.content, bg=BG_MAIN)
        cal_frame.pack(fill=tk.BOTH, expand=True)


        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, d in enumerate(days):
            tk.Label(
                cal_frame, text=d,
                font=("Georgia", 10, "bold"),
                bg=BG_HEADER, fg=FG_HEADER,
                height=2
            ).grid(row=0, column=i, sticky="nsew", padx=1, pady=1)


        y, m = self.current_date.year, self.current_date.month
        first_wd = date(y, m, 1).weekday()  # 0 = Mon
        days_in_month = calendar.monthrange(y, m)[1]


        day_num = 1
        for r in range(1, 7):
            for c in range(7):
                if (r == 1 and c < first_wd) or day_num > days_in_month:
                    tk.Label(cal_frame, text="", bg=BG_MAIN).grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                else:
                    d_date = date(y, m, day_num)
                    k = self.date_key(d_date)
                    count = len(self.tasks_data.get(k, []))
                    text = f"{day_num}\n{count} task" + ("" if count == 1 else "s")
                    bg = "#ffef9c" if d_date == date.today() else ("#d8e4dd" if count > 0 else "#e8dfcf")
                    btn = tk.Button(
                        cal_frame, text=text,
                        command=lambda dd=d_date: self.show_day_view(dd),
                        font=("Georgia", 10),
                        bg=bg, fg=TEXT_MAIN,
                        bd=0, height=4, wraplength=90
                    )
                    btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                    day_num += 1


        for c in range(7):
            cal_frame.grid_columnconfigure(c, weight=1)
        for r in range(7):
            cal_frame.grid_rowconfigure(r, weight=1)


    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.current_date = date(self.current_year, self.current_month, 1)
        self.show_month_view()


    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.current_date = date(self.current_year, self.current_month, 1)
        self.show_month_view()


    # ---------- day view ----------


    def show_day_view(self, selected_date):
        self.current_view = "day"
        self.current_date = selected_date
        self.clear_content()


        header = tk.Label(
            self.content,
            text=selected_date.strftime("%A, %d %B %Y"),
            font=("Georgia", 16, "bold"),
            bg=BG_MAIN, fg=TEXT_MAIN
        )
        header.pack(pady=(0, 10))


        table = tk.Frame(self.content, bg=BG_PANEL, highlightthickness=1,
                         highlightbackground=ACCENT)
        table.pack(fill=tk.BOTH, expand=True)


        tk.Label(table, text="", width=3, bg=BG_HEADER).grid(row=0, column=0, sticky="nsew")
        tk.Label(table, text="Task", bg=BG_HEADER, fg=FG_HEADER,
                 font=("Georgia", 10, "bold")).grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
        tk.Label(table, text="Time", bg=BG_HEADER, fg=FG_HEADER,
                 font=("Georgia", 10, "bold")).grid(row=0, column=2, sticky="nsew", padx=1, pady=1)
        tk.Label(table, text="Feedback", bg=BG_HEADER, fg=FG_HEADER,
                 font=("Georgia", 10, "bold")).grid(row=0, column=3, sticky="nsew", padx=1, pady=1)


        self.table_frame = table
        self.refresh_tasks()


        for c in range(4):
            table.grid_columnconfigure(c, weight=1)


    # ---------- task ops ----------


    def add_task(self):
        text = self.task_entry.get().strip()
        start_time = self.start_time_text
        end_time = self.end_time_text
        fb = self.feedback_entry.get().strip()
        if not text:
            return


        key = self.date_key(self.current_date)
        if key not in self.tasks_data:
            self.tasks_data[key] = []


        self.tasks_data[key].append({
            "text": text,
            "start_time": start_time,
            "end_time": end_time,
            "feedback": fb,
            "done": False
        })


        self.task_entry.delete(0, tk.END)
        self.feedback_entry.delete(0, tk.END)
        self.save_data()


        if self.current_view == "day":
            self.refresh_tasks()


    def refresh_tasks(self):
        if not hasattr(self, "table_frame"):
            return


        # clear rows except header
        for w in self.table_frame.winfo_children():
            if w.grid_info()["row"] != 0:
                w.destroy()


        key = self.date_key(self.current_date)
        tasks = self.tasks_data.get(key, [])


        now = datetime.now()


        for i, task in enumerate(tasks):
            row = i + 1
            bg = TASK_ROW_ODD if row % 2 else TASK_ROW_EVN


            var = tk.BooleanVar(value=task["done"])


            def make_cmd(idx, v):
                return lambda: self.toggle_checkbox(idx, v)


            cb = tk.Checkbutton(
                self.table_frame, variable=var,
                command=make_cmd(i, var),
                bg=bg, activebackground=bg
            )
            cb.grid(row=row, column=0, padx=(8, 4), pady=4, sticky="w")


            # fonts: strike only task text
            task_font = ("Georgia", 10, "overstrike") if task["done"] else ("Georgia", 10)
            normal_font = ("Georgia", 10)


            # right-click on checkbox row to delete task
            def make_right_click(idx):
                def handler(event):
                    self.delete_task(idx)
                return handler
            cb.bind("<Button-3>", make_right_click(i))


            # Task text
            tk.Label(
                self.table_frame, text=task["text"],
                bg=bg, fg=TEXT_MAIN, font=task_font
            ).grid(row=row, column=1, sticky="w", padx=4, pady=4)


            # Time (never struck through)
            time_display = f"{task['start_time']}-{task['end_time']}"
            time_label = tk.Label(
                self.table_frame, text=time_display,
                bg=bg, fg=TEXT_MAIN, font=normal_font
            )
            time_label.grid(row=row, column=2, sticky="w", padx=4, pady=4)


            def make_time_edit(idx):
                return lambda e: self.edit_time_range(idx)


            time_label.bind("<Double-1>", make_time_edit(i))


            # build feedback + scold if overdue and not done
            feedback_text = task.get("feedback", "")
            if (not task["done"] and task["start_time"] and self.current_date == date.today()):
                try:
                    start_t = datetime.strptime(task["start_time"], "%H:%M").time()
                    task_dt = datetime.combine(self.current_date, start_t)
                    if now > task_dt and SCOLD_TEXT not in feedback_text:
                        feedback_text = (feedback_text + "  |  " + SCOLD_TEXT).strip()
                        task["feedback"] = feedback_text
                        self.save_data()
                except ValueError:
                    pass  # invalid time format, ignore


            # Feedback (never struck through)
            fb_label = tk.Label(
                self.table_frame, text=feedback_text,
                bg=bg, fg=TEXT_MAIN, font=normal_font,
                anchor="w", justify="left", wraplength=450
            )
            fb_label.grid(row=row, column=3, sticky="nsew", padx=4, pady=4)


            def make_fb_edit(idx):
                return lambda e: self.edit_feedback(idx, row)


            fb_label.bind("<Double-1>", make_fb_edit(i))


        self.save_data()


    def edit_time_range(self, index):
        """Edit both start and end time with time selectors"""
        key = self.date_key(self.current_date)
        if key not in self.tasks_data or index >= len(self.tasks_data[key]):
            return


        task = self.tasks_data[key][index]


        editor = tk.Toplevel(self.root)
        editor.title("Edit Time Range")
        editor.geometry("350x300")
        editor.configure(bg=BG_PANEL)
        editor.transient(self.root)
        editor.grab_set()


        tk.Label(
            editor, text="Start Time", bg=BG_PANEL, fg=TEXT_MAIN,
            font=("Georgia", 12, "bold")
        ).pack(pady=10)
        start_selector = TimeSelector(editor, "Select Start Time", task["start_time"])
        start_time = start_selector.get_time()


        tk.Label(
            editor, text="End Time", bg=BG_PANEL, fg=TEXT_MAIN,
            font=("Georgia", 12, "bold")
        ).pack(pady=(20, 10))
        end_selector = TimeSelector(editor, "Select End Time", task["end_time"])
        end_time = end_selector.get_time()


        def save_times():
            task["start_time"] = start_selector.selected_time.get()
            task["end_time"] = end_selector.selected_time.get()
            self.save_data()
            self.refresh_tasks()
            editor.destroy()


        btn_frame = tk.Frame(editor, bg=BG_PANEL)
        btn_frame.pack(pady=20)
        tk.Button(
            btn_frame, text="Save", command=save_times,
            bg=ACCENT, fg="white", font=("Georgia", 10, "bold"),
            bd=0, padx=20, pady=8
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame, text="Cancel", command=editor.destroy,
            bg=BG_HEADER, fg=FG_HEADER, font=("Georgia", 10),
            bd=0, padx=20, pady=8
        ).pack(side=tk.LEFT, padx=5)


    def edit_feedback(self, index, row):
        """Inline edit for feedback"""
        key = self.date_key(self.current_date)
        if key not in self.tasks_data or index >= len(self.tasks_data[key]):
            return


        task = self.tasks_data[key][index]
        old_feedback = task.get("feedback", "")


        entry = tk.Entry(
            self.table_frame, font=("Georgia", 10),
            bg=BG_MAIN, bd=0, highlightthickness=1,
            highlightbackground=ACCENT, width=40
        )
        entry.insert(0, old_feedback)
        entry.grid(row=row, column=3, sticky="nsew", padx=4, pady=4)
        entry.focus_set()
        entry.selection_range(0, tk.END)


        def finish_edit(event=None):
            new_feedback = entry.get().strip()
            task["feedback"] = new_feedback
            self.save_data()
            self.refresh_tasks()


        def cancel_edit(event=None):
            self.refresh_tasks()


        entry.bind("<Return>", finish_edit)
        entry.bind("<Escape>", cancel_edit)
        entry.bind("<FocusOut>", finish_edit)


    def toggle_checkbox(self, index, var):
        key = self.date_key(self.current_date)
        if key not in self.tasks_data or index >= len(self.tasks_data[key]):
            return


        task = self.tasks_data[key][index]


        task["done"] = not task["done"]


        if task["done"] and task.get("feedback"):
            task["feedback"] = task["feedback"].replace(SCOLD_TEXT, "").replace("  |  ", " ").strip()


        self.save_data()
        self.refresh_tasks()


    def delete_task(self, index):
        key = self.date_key(self.current_date)
        if key not in self.tasks_data or index >= len(self.tasks_data[key]):
            return
        del self.tasks_data[key][index]
        if not self.tasks_data[key]:
            del self.tasks_data[key]
        self.save_data()
        self.refresh_tasks()


    # ---------- misc ----------


    def go_today(self):
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.current_date = today
        self.show_day_view(today)


if __name__ == "__main__":
    root = tk.Tk()
    app = YearlyTodoApp(root)
    root.mainloop()
if __name__ == "__main__":
    root = tk.Tk()
    
    # Add this block - sets your Downloads/logo.ico as window icon
    import os
    from pathlib import Path
    icon_path = Path.home() / "Downloads" / "logo.ico"
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
            print(f"✅ Icon loaded: {icon_path}")
        except Exception as e:
            print(f"❌ Icon failed: {e}")
    else:
        print(f"❌ Icon not found: {icon_path}")
    
    app = YearlyTodoApp(root)
    root.mainloop()
