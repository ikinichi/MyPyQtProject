import qasync

from library import *
import main_window


class MyWidgetVenvAccount(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("./untitled_3.ui", self)
        MyWidgetVenvAccount.setWindowTitle(self, "Venv Account")
        MyWidgetVenvAccount.setFixedSize(
            self,
            MyWidgetVenvAccount.width(self),
            MyWidgetVenvAccount.height(self)
        )

        self.plot_widget = QWebEngineView(self)

        main_window.MyWidget().add_elem_comboBox(self.comboBox)

        self.crypto = self.comboBox.currentText()
        self.label_14.setText("ВСЕГО '" + self.crypto + "'")

        self.pushButton.clicked.connect(self.update_graph_and_label)
        self.pushButton_2.clicked.connect(self.thread_buy)
        self.pushButton_3.clicked.connect(self.thread_sell)
        self.pushButton_4.clicked.connect(self.back)

    def thread_buy(self):
        self.t1 = threading.Thread(target=self.buy_crypto)
        self.t1.start()

    def thread_sell(self):
        self.t2 = threading.Thread(target=self.sell_crypto)
        self.t2.start()

    def back(self):
        """Закрывает <Виртуальный счет>.
        Открывает <Главное окно>"""
        self.mywidget = main_window.MyWidget()
        self.mywidget.show()
        self.hide()

    @qasync.asyncSlot()
    async def update_graph_and_label(self):
        await main_window.MyWidget()._graph_draw(
            self.comboBox,
            self.comboBox_2,
            self.comboBox_3,
            self.plot_widget
        )
        self.crypto = self.comboBox.currentText()
        self.label_14.setText("ВСЕГО '" + self.crypto + "'")

    def buy_crypto(self):
        self.price_crypto_usd()
        crypto = self.comboBox.currentText()
        try:
            buy_crypto = float(self.lineEdit.text())
        except ValueError:
            return
        buy_crypto_usd = buy_crypto * self.dct_crypto_price.get(crypto)

        con = sqlite3.connect("./date_news_db.db")
        cur = con.cursor()
        cur.execute(
            """UPDATE cryptos SET sum = sum + ?, invest = invest + ? WHERE name LIKE ?""",
            (buy_crypto, buy_crypto_usd, crypto)
        ).fetchall()
        con.commit()

        self.update_value_crypto()

    def sell_crypto(self):
        self.price_crypto_usd()
        crypto = self.comboBox.currentText()
        try:
            buy_crypto = float(self.lineEdit_6.text())
        except ValueError:
            return
        buy_crypto_usd = buy_crypto * self.dct_crypto_price.get(crypto)

        con = sqlite3.connect("./date_news_db.db")
        cur = con.cursor()
        proverka_price = \
            cur.execute("""SELECT sum FROM cryptos WHERE name LIKE ?""", (crypto,)).fetchall()[0][0]
        if proverka_price - buy_crypto < 0:
            return
        else:
            cur.execute(
                """UPDATE cryptos SET sum = sum - ?, invest = invest - ? WHERE name LIKE ?""",
                (buy_crypto, buy_crypto_usd, crypto)
            ).fetchall()
            con.commit()

        self.update_value_crypto()

    def update_value_crypto(self):
        crypto = self.comboBox.currentText()

        con = sqlite3.connect("./date_news_db.db")
        cur = con.cursor()

        sum_buy_crypto = cur.execute("""SELECT sum FROM cryptos WHERE name LIKE ?""", (crypto,)).fetchall()
        self.lineEdit_5.setText(str(sum_buy_crypto[0][0]))

        # TOTAL
        invest_total = sum(
            [float(elem[0]) for elem in cur.execute("""SELECT invest FROM cryptos""").fetchall()]
        )
        quotes_result_total = cur.execute("""SELECT name, sum FROM cryptos""").fetchall()
        result_total = 0
        for elem in quotes_result_total:
            result_total += elem[1] * self.dct_crypto_price.get(elem[0])
        difference_total = result_total - invest_total

        self.lineEdit_2.setText(str(invest_total))
        self.lineEdit_3.setText(str(result_total))
        self.lineEdit_4.setText(str(difference_total))

        # TOTAL crypto
        invest_total_crypto = cur.execute(
            """SELECT invest FROM cryptos WHERE name LIKE ?""", (crypto,)
        ).fetchall()[0][0]
        quotes_result_total_crypto = cur.execute(
            """SELECT name, sum FROM cryptos WHERE name LIKE ?""", (crypto,)
        ).fetchall()
        result_total_crypto = float(quotes_result_total_crypto[0][1]) * self.dct_crypto_price.get(
            quotes_result_total_crypto[0][0]
        )
        difference_total_crypto = result_total_crypto - float(invest_total_crypto)

        self.lineEdit_8.setText(str(invest_total_crypto))
        self.lineEdit_9.setText(str(result_total_crypto))
        self.lineEdit_7.setText(str(difference_total_crypto))

    def price_crypto_usd(self):
        url = 'https://coinmarketcap.com/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        quotes_price = soup.find_all("a", class_="cmc-link")
        quotes_name = soup.find_all("p", class_="q7nmo0-0 krbrab coin-item-symbol")

        result_name = [elem.text for elem in quotes_name[9::]]
        result_price_usd = [float(q.text[1:].replace(",", "")) for q in quotes_price[66:104:4]]

        self.dct_crypto_price = {}
        for i in range(10):
            self.dct_crypto_price[result_name[i]] = result_price_usd[i]
