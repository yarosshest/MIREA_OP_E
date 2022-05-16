from tkinter import ttk, LEFT, LabelFrame, Entry, Frame, StringVar, Label, TOP, X, IntVar, Radiobutton
import tkinter as tk
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
from calendar import monthrange
import tkinter as tk
import matplotlib.dates as mdates
import matplotlib
from matplotlib.figure import Figure
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)


def get_db_by_date(dt):
    str_date = dt.strftime("%d/%m/%Y")
    r = requests.get("http://www.cbr.ru/scripts/XML_daily.asp?date_req={}".format(str_date))
    text = r.text.encode("windows-1251")
    soup = BeautifulSoup(text, 'xml', from_encoding="windows-1251")
    names = list(map(lambda x: x.get_text(), soup.find_all('Name')))
    values = list(map(lambda x: x.get_text().replace(',', '.'), soup.find_all('Value')))
    nominals = list(map(lambda x: x.get_text(), soup.find_all('Nominal')))

    for i in range(len(values)):
        values[i] = float(values[i]) / float(nominals[i])
    return {"names": names, "values": values}


def get_val_of_date(val, dt):
    bd = get_db_by_date(dt)
    return bd["values"][bd["names"].index(val)]



class App(object):
    def __init__(self):
        self.data = None
        self.app = tk.Tk()
        self.app.geometry('800x300')
        self.res = StringVar()
        self.am = StringVar()
        self.fr = StringVar()
        self.to = StringVar()
        self.ch = StringVar()
        self.date = IntVar()
        self.ch_period = StringVar()

    def cur_from(self, frame, names):
        self.combo_from = ttk.Combobox(frame,
                                       textvariable=self.fr,
                                       values=names,
                                       state="readonly")
        self.combo_from.pack(side=LEFT, padx=20, pady=20)

    def cur_to(self, frame, names):
        self.combo_to = ttk.Combobox(frame,
                                     textvariable=self.to,
                                     values=names,
                                     state="readonly")
        self.combo_to.pack(side=LEFT, padx=20, pady=20)

    def write_am(self, frame):
        self.Entry_write = ttk.Entry(frame, textvariable=self.am)
        self.Entry_write.pack(side=LEFT, padx=20, pady=20)

    def reed_am(self, frame):
        self.Text_reed = Label(frame)
        self.Text_reed.pack(side=LEFT, padx=20, pady=20)

    def calk(self):
        col = float(self.am.get())
        val = self.data["values"][self.data["names"].index(self.fr.get())]
        sum = col * val
        res = sum / self.data["values"][self.data["names"].index(self.to.get())]
        self.Text_reed.config(text=res)

    def calk_button(self, frame):
        self.Button_calk = ttk.Button(frame, text="конвертировать")
        self.Button_calk.config(command=self.calk)
        self.Button_calk.pack(side=LEFT, padx=20, pady=20)

    def choice_box(self, frame, names):
        self.combo_choice = ttk.Combobox(frame,
                                         textvariable=self.ch,
                                         values=names,
                                         state="readonly")
        self.combo_choice.pack(side=LEFT, padx=20, pady=20)

    def period_box(self, frame):
        self.combo_period = ttk.Combobox(frame,
                                         textvariable=self.ch_period,
                                         state="readonly")
        self.combo_period.pack(side=LEFT, padx=20, pady=20)

    def calk_period(self):
        to_day = date.today()
        dates = []
        date_dates = {}
        if self.date.get() == 0:
            step = timedelta(weeks=1)
            date_last = to_day
            for i in range(3):
                days_ago = date_last - step
                str_date = days_ago.strftime("%d/%m/%Y") + "-" + date_last.strftime("%d/%m/%Y")
                date_dates.update({str_date: [days_ago, date_last]})
                dates.append(str_date)
                date_last = days_ago
        if self.date.get() == 1:
            date_last = to_day
            for i in range(4):
                days_ago = date_last.replace(day=1) - timedelta(days=1)
                if i != 0:
                    str_date = date_last.strftime("%B") + " " + date_last.strftime("%Y")
                    date_dates.update({str_date: [date_last.replace(day=1), date_last.replace(
                        day=monthrange(date_last.year, date_last.month)[1])]})
                    dates.append(str_date)
                date_last = days_ago
        if self.date.get() == 2:
            q = round((to_day.month - 1) // 3 + 1)
            date_last = datetime(to_day.year, 3 * q - 2, 1)
            for i in range(4):
                days_ago = datetime(date_last.year, 3 * q - 2, 1) - timedelta(days=1)
                if i != 0:
                    str_date = date_last.strftime("%Y") + 'Q' + str(q)
                    date_dates.update({str_date: [datetime(date_last.year, 3 * q - 2, 1),
                                                  datetime(date_last.year, 3 * q + 1, 1) + timedelta(days=-1)]})
                    dates.append(str_date)

                date_last = days_ago
                q = round((date_last.month - 1) // 3 + 1)
        if self.date.get() == 3:
            date_last = to_day.replace(day=1, month=1)
            for i in range(4):
                days_ago = date_last.replace(day=1, month=1) - timedelta(days=1)
                if i != 0:
                    str_date = date_last.strftime("%Y")
                    date_dates.update({str_date: [days_ago + timedelta(days=1), date_last]})
                    dates.append(str_date)

                date_last = days_ago
        self.combo_period['values'] = dates
        self.str_dates = dates
        self.date_dates = date_dates

    def choise_date(self, frame):
        self.week = Radiobutton(frame, text="Неделя", variable=self.date, value=0, command=self.calk_period)
        self.month = Radiobutton(frame, text="Месяц", variable=self.date, value=1, command=self.calk_period)
        self.quarter = Radiobutton(frame, text="Квартал", variable=self.date, value=2, command=self.calk_period)
        self.year = Radiobutton(frame, text="Год", variable=self.date, value=3, command=self.calk_period)

        self.week.pack(side=TOP, padx=20, pady=20)
        self.month.pack(side=TOP, padx=20, pady=20)
        self.quarter.pack(side=TOP, padx=20, pady=20)
        self.year.pack(side=TOP, padx=20, pady=20)

    def prep_data(self):
        begin = self.date_dates[self.ch_period.get()][0]
        end = self.date_dates[self.ch_period.get()][1]
        y = []
        x = []
        while begin <= end:
            y.append(get_val_of_date(self.ch.get(), begin))
            x.append(begin)
            begin += timedelta(days=1)
        return [matplotlib.dates.date2num(x), y]

    def prep_mpl(self, frame):
        figure = Figure(figsize=(6, 4), dpi=100)
        self.figure_canvas = FigureCanvasTkAgg(figure, frame)
        self.axes = figure.add_subplot()
        self.axes.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))
        self.axes.xaxis.set_minor_locator(mdates.MonthLocator())
        self.figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def draw_mpl(self):
        self.axes.plot(self.prep_data())
        self.figure_canvas.draw()

    def graph_button(self, frame):
        self.Button_graph = ttk.Button(frame, text="Построить график")
        self.Button_graph.config(command=self.draw_mpl)
        self.Button_graph.pack(side=LEFT, padx=20, pady=20)

    def run(self):
        note = ttk.Notebook(self.app)

        f1 = Frame(note)

        note.add(f1, text="Калькулятор валют")

        self.data = get_db_by_date(date.today())
        from_frame = LabelFrame(f1, text="Из")
        to_frame = LabelFrame(f1, text="В")
        button = Frame(f1)

        self.cur_from(from_frame, self.data['names'])
        self.cur_to(to_frame, self.data['names'])

        self.write_am(from_frame)
        self.reed_am(to_frame)
        self.calk_button(button)

        from_frame.pack()
        to_frame.pack()
        button.pack()

        f2 = Frame(note)
        note.add(f2, text="Динамика курса")

        choice_frame = Frame(f2)

        box_frame = Frame(choice_frame)
        button_frame = Frame(choice_frame)

        self.choice_box(box_frame, self.data['names'])
        self.graph_button(button_frame)

        box_frame.pack()
        button_frame.pack()

        choice_frame.pack(side=LEFT)

        date_frame = Frame(f2)

        self.choise_date(date_frame)

        date_frame.pack(side=LEFT)

        period_frame = Frame(f2)
        self.period_box(period_frame)

        period_frame.pack()

        self.prep_mpl(f2)

        note.pack()
        self.app.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()
