import main_window
from library import *


class MyWidgetAllNews(QMainWindow):
    """Поиск новостей по тексту и дате.
    Добавление новостей в избранное"""

    def __init__(self):
        super().__init__()
        uic.loadUi("./untitled_2.ui", self)
        MyWidgetAllNews.setWindowTitle(self, "All News")
        MyWidgetAllNews.setFixedSize(self, MyWidgetAllNews.width(self), MyWidgetAllNews.height(self))

        self.pushButton.clicked.connect(self.back)
        self.pushButton_2.clicked.connect(self.thread)

        self.pushButton_3.clicked.connect(lambda: self.add_and_sub_count(False))
        self.pushButton_4.clicked.connect(lambda: self.add_and_sub_count(True))
        self.pushButton_5.clicked.connect(lambda: self.favorites_news(self.result[self.count]))
        self.pushButton_6.clicked.connect(self.open_favorites_news)

    def back(self):
        """Закрывает <Просмотр всех новостей>.
        Открывает <Главное окно>"""
        self.mywidget = main_window.MyWidget()
        self.mywidget.show()
        self.start_stop = False
        self.hide()

    def thread(self):
        """Запускает парсинг в потоке.
        Меняет текст кнопки и способность не нажимать её"""
        self.pushButton_2.setText("Поиск идет🔍")
        self.pushButton_2.setEnabled(False)
        self.t1 = threading.Thread(target=self.update_db)
        self.t1.daemon = True
        self.t1.start()

    def update_db(self):
        """Добавление в БД новые новости с их датами публикации"""
        url = 'https://1prime.ru/trend/bitcoins/'  # url сайта с новостями
        self.start_stop = True

        con = sqlite3.connect("./date_news_db.db")
        cur = con.cursor()

        compare_value = cur.execute("""SELECT * FROM date_news""").fetchall()
        if compare_value == []:
            compare_value_data = False
            compare_value_news = False
        else:
            compare_value = compare_value[-1]  # самая новая новость
            compare_value_data = compare_value[0]  # дата самой новой новости
            compare_value_news = compare_value[1]  # текст самой новой новости

        while self.start_stop:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            quotes = soup.find_all("article", class_="rubric-list__article rubric-list__article_default")

            for quote in quotes:
                date = quote.find("time", class_="rubric-list__article-time").get("datetime")[:10]  # дата публиакции
                new = quote.find("h2", class_="rubric-list__article-title").text  # текст новости

                if (compare_value_data == date) and (compare_value_news == new):
                    self.start_stop = False
                    break
                else:
                    cur.execute("""INSERT INTO date_news(date, news) VALUES(?, ?)""", (date, new,))
                    con.commit()

            url = "https://1prime.ru" + soup.find("a", class_="button button_inline button_rounded button_more").get(
                "href")  # новый url(автоподгрузка страницы)

        self.search()

    def search(self):
        """Поиск новостей по критериям(дата, текст)"""
        data = self.calendarWidget.selectedDate()
        data = f"{data.year()}-{data.month()}-{data.day()}"  # дата новости которую надо вывести
        text = self.textEdit.toPlainText()  # текст новости которую надо вывести
        search_text = self.checkBox.isChecked()  # флаг проверки по тексту
        search_date = self.checkBox_2.isChecked()  # флаг проверки по дате
        self.result = []  # список всех найденных новостей

        con = sqlite3.connect("./date_news_db.db")
        cur = con.cursor()

        if (search_text is True) and (search_date is True):
            self.result = cur.execute(f"""SELECT * FROM date_news WHERE date = ? AND news LIKE ?""",
                                      (data, "%" + text + "%",)).fetchall()
        elif search_date is True:
            self.result = cur.execute("""SELECT * FROM date_news WHERE date = ?""", (data,)).fetchall()
        elif search_text is True:
            self.result = cur.execute(f"""SELECT * FROM date_news WHERE news LIKE ?""", ("%" + text + "%",)).fetchall()

        self.pushButton_2.setText("ПОИСК🔍")
        self.pushButton_2.setEnabled(True)

        print(self.result)

        cur.close()

        self.count = 0  # индекс новости которую надо вывести из списка
        self.iter_result()

    def iter_result(self):
        """Итерация по списку найденых новостей
        Обработка ошибки когда новостей нет
        Отключение кнопок на границах списка новостей"""
        try:
            if self.count == 0:
                self.pushButton_3.setEnabled(False)
            else:
                self.pushButton_3.setEnabled(True)

            if self.count + 1 == len(self.result):
                self.pushButton_4.setEnabled(False)
            else:
                self.pushButton_4.setEnabled(True)

            self.label_3.setText(self.result[self.count][0])  # отображение даты публикации
            self.plainTextEdit.setPlainText(self.result[self.count][1])  # отображение текста новости

        except IndexError:
            if self.count == 0:
                self.plainTextEdit.setPlainText("Новостей НЕ найдено")

    def add_and_sub_count(self, proverka):
        """Увеличение либо уменьшение индекса для вывода новости"""
        if proverka is True:
            self.count += 1
        if proverka is False:
            self.count -= 1
        self.iter_result()

    def favorites_news(self, favorite_news):
        """Добавление в БД избранной новости"""
        try:
            date = favorite_news[0]
            news = favorite_news[1]
            con = sqlite3.connect("./date_news_db.db")
            cur = con.cursor()
            cur.execute("""INSERT INTO favorites_news(date, favorite_news) VALUES(?, ?)""",
                        (date, news + "★",)).fetchall()
            con.commit()
        except sqlite3.IntegrityError:  # обработка ошибки на универсальность текста новости
            return

    def open_favorites_news(self):
        """Вывод всех избранных новостей"""
        con = sqlite3.connect("./date_news_db.db")
        cur = con.cursor()
        self.result = cur.execute("""SELECT * FROM favorites_news""").fetchall()
        self.count = 0
        cur.close()
        self.iter_result()
