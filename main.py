from tkinter import ttk, LEFT, LabelFrame, Entry, Frame, StringVar, Label, TOP, X, IntVar, Radiobutton
import tkinter as tk
import requests
from bs4 import BeautifulSoup
import datetime


def get_db_by_date(date):
    str_date = date.strftime("%d/%m/%Y")
    r = requests.get("http://www.cbr.ru/scripts/XML_daily.asp?date_req={}".format(str_date))
    text = r.text.encode("windows-1251")
    soup = BeautifulSoup(text, 'xml', from_encoding="windows-1251")
    names = list(map(lambda x: x.get_text(), soup.find_all('Name')))
    values = list(map(lambda x: x.get_text().replace(',', '.'), soup.find_all('Value')))
    nominals = list(map(lambda x: x.get_text(), soup.find_all('Nominal')))

    for i in range(len(values)):
        values[i] = float(values[i])/float(nominals[i])
    return {"names": names, "values": values}


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
        sum = col* val
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

    def graph_button(self, frame):
        self.Button_graph = ttk.Button(frame, text="Построить график")
        self.Button_graph.config(command=self.calk)
        self.Button_graph.pack(side=LEFT, padx=20, pady=20)


    def period_box(self, frame):
        self.combo_period = ttk.Combobox(frame,
                                         textvariable=self.ch_period,
                                         state="readonly")
        self.combo_period.pack(side=LEFT, padx=20, pady=20)

    def calk_period(self):
        to_day = datetime.date.today()
        dates = []
        if self.date.get() == 0:
            step = datetime.timedelta(weeks=1)
            date_last = to_day
            for i in range(3):
                days_ago = date_last - step
                str_date = days_ago.strftime("%d/%m/%Y") + "-" + date_last.strftime("%d/%m/%Y")
                dates.append(str_date)
                date_last = days_ago
        if self.date.get() == 1:
            date_last = to_day
            for i in range(3):
                days_ago = date_last.replace(day=1) - datetime.timedelta(days=1)
                str_date = date_last.strftime("%B") + " " + date_last.strftime("%Y")
                dates.append(str_date)
                date_last = days_ago
        if self.date.get() == 2:
            step = datetime.timedelta(months=3)
        if self.date.get() == 3:
            step = datetime.timedelta(months=12)
        self.combo_period['values'] = dates

    def choise_date(self, frame):
        self.week = Radiobutton(frame, text="Неделя", variable=self.date, value=0, command=self.calk_period)
        self.month = Radiobutton(frame, text="Месяц", variable=self.date, value=1, command=self.calk_period)
        self.quarter = Radiobutton(frame, text="Квартал", variable=self.date, value=2, command=self.calk_period)
        self.year = Radiobutton(frame, text="Год", variable=self.date, value=3, command=self.calk_period)

        self.week.pack(side=TOP, padx=20, pady=20)
        self.month.pack(side=TOP, padx=20, pady=20)
        self.quarter.pack(side=TOP, padx=20, pady=20)
        self.year.pack(side=TOP, padx=20, pady=20)

    def run(self):
        note = ttk.Notebook(self.app)

        f1 = Frame(note)

        note.add(f1, text="Калькулятор валют")

        self.data = get_db_by_date(datetime.date.today())
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



        note.pack()
        self.app.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()

