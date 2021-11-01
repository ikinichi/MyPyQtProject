import sys
import sqlite3
import datetime
import threading
import logging

from plotly.graph_objects import Figure, Scatter, Candlestick
import plotly
import yfinance as yf

import requests
from bs4 import BeautifulSoup

from PyQt5.QtWidgets import QMainWindow, QApplication, QComboBox, QTextEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import uic, QtGui
from PyQt5 import QtCore
from qt_material import apply_stylesheet
