from library import *
import news_window
import venv_account_window


class MyWidget(QMainWindow):
    """<Главное окно>.
    Вывод графика.
    Вывод первых 4-х новостей.
    Перенос в окна <Виртуальный счет> и <Просмотр всех новостей>"""

    def __init__(self):
        super().__init__()
        uic.loadUi("./untitled.ui", self)
        MyWidget.setWindowTitle(self, "Predictor Quotes")
        MyWidget.setFixedSize(self, MyWidget.width(self), MyWidget.height(self))

        self.plot_widget = QWebEngineView(self)

        self.add_elem_comboBox(self.comboBox)
        self.graph_draw(self.comboBox, self.comboBox_2, self.comboBox_3, self.plot_widget)
        self.update_news()
        self.thread()

        self.pushButton.clicked.connect(self.open_venv_account)
        self.pushButton_2.clicked.connect(self.open_all_news)
        self.pushButton_3.clicked.connect(
            lambda: self.graph_draw(self.comboBox, self.comboBox_2, self.comboBox_3, self.plot_widget))

    def open_venv_account(self):
        """Открывает <Виртуальный счет>.
        И закрывает настоящее окно."""
        self.exit_bool = False
        self.venvAcc = venv_account_window.MyWidgetVenvAccount()
        self.venvAcc.show()
        self.hide()

    def open_all_news(self):
        """Открывает <Просмотр всех новостей>.
        И закрывает настоящее окно."""
        self.exit_bool = False
        self.allnews = news_window.MyWidgetAllNews()
        self.allnews.show()
        self.hide()

    def thread(self):
        """Теперь таймер выполняется в потоке"""
        self.exit_bool = True
        self.auto_update_news()
        self.t1 = threading.Thread(target=self.timer)
        self.t1.start()

    def auto_update_news(self):
        """Обновляет таймер до начальных значений"""
        self.times = 0
        QtCore.QTimer.singleShot(1000, self.timer)

    def timer(self):
        """Обновляет ленту новостей каждые 10 секунд"""
        self.times += 1

        if self.exit_bool:
            if self.times < 10:  # 10 секунд
                QtCore.QTimer.singleShot(1000, self.timer)
            else:
                self.update_news()
                self.thread()
        else:
            return

    def update_news(self):
        """Парсит новости по криптовалютам.
        И добавляет их в textEdit"""
        url = 'https://1prime.ru/trend/bitcoins/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        quotes = soup.find_all("h2", class_="rubric-list__article-title")[:4]  # т.к. только первые 4 новости

        widgets = [self.textEdit, self.textEdit_2, self.textEdit_3, self.textEdit_4]
        for i, wid in enumerate(widgets):
            wid.setText(quotes[i].text)
            wid.setReadOnly(True)

    def add_elem_comboBox(self, name_combo_box):
        """Парсинг названий топ-10 рейтинга криптовалют.
        И передача их в QComboBox"""
        url = 'https://coinmarketcap.com/ru/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        quotes = soup.find_all("p", class_="q7nmo0-0 krbrab coin-item-symbol")

        for elem in quotes[9::]:  # у значений такой-же класс при парсинге, но в quotes их учитывать не нужно
            name_combo_box.addItem(elem.text)

    def graph_draw(self, combo_box, combo_box_2, combo_box_3, plot_widget):
        """Создание 2-ух графиков:
        1)краткосрочный скользящий средний с 5-ю периодами
        2)долгосрочный скользящий средний с 20-ю периодами
        И вывод их в QWebEngineView"""
        crypto = combo_box.currentText()
        period = combo_box_2.currentText()
        interval = combo_box_3.currentText()

        data = yf.download(tickers=crypto + "-USD", period=period, interval=interval)

        data['MA5'] = data['Close'].rolling(5).mean()  # 5-ти периодный график
        data['MA20'] = data['Close'].rolling(20).mean()  # 20-ти периодный график

        fig = Figure()
        fig.update_layout(title="Алгоритм 'Золотой Крест'",
                          xaxis_title="Цена",
                          yaxis_title="Дата",
                          margin=dict(l=0, r=0, t=30, b=0))

        fig.add_trace(Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'],
                                  close=data['Close'], name='Price'))
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.add_trace(Scatter(x=data.index, y=data['MA20'], line=dict(color='blue', width=1.5), name='Long MA'))
        fig.add_trace(Scatter(x=data.index, y=data['MA5'], line=dict(color='orange', width=1.5), name='Short MA'))

        html = '<html><body>'
        html += plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
        html += '</body></html>'

        plot_widget.setHtml(html)
        plot_widget.setGeometry(10, 10, 921, 501)  # размеры окна
        plot_widget.resize(921, 501)  # размеры окна


if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    widget = MyWidget()
    widget.show()

    sys.exit(app.exec())
