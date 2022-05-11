from PyQt6 import uic, QtWidgets
import sys
import os
from datetime import datetime, timedelta

mainWindow = QtWidgets.QApplication([])


class Ui_MainWindow:
    def __init__(self) -> None:
        self.dateToday = datetime.now().strftime('%d-%m-%Y')
        self.timeframe = 5
        self.mainForm = uic.loadUi('ui/MainWindow.ui')
        self.mainForm.tableWidget.setColumnWidth(5, 104)
        #self.corrigirSinais()

        # Set Home Page
        self.mainForm.stackedWidget.setCurrentIndex(0)
        # Home Page!
        self.mainForm.HomeButton.clicked.connect(self.homePage)
        # Settings Page!
        self.mainForm.SettingsButton.clicked.connect(self.settingsPage)

        self.mainForm.show()

    def corrigirSinais(self, caminho:str):

        file = open(caminho, encoding='UTF-8')
        lista = file.read()
        file.close

        lista = lista.split('\n')

        # if os.path.exists('sinais corrigidos.txt'):
        #     os.remove('sinais corrigidos.txt')

        if os.path.exists('sinais corrigidos.txt'):
            os.remove('sinais corrigidos.txt')

        row = 0
        for x in lista:
            dados = x.split(' ')
            dados_1 = dados[1].replace(' ', '')
            dados_2 = dados[2].replace(' ', '')
            dados_2 = dados_2.lower()
            sinais = f'{dados[0]}:00,{dados_1},{dados_2},{self.timeframe}'

            #print(self.mainForm.tableWidget.row())

            self.mainForm.tableWidget.setRowCount(len(lista))
            #table date value
            self.mainForm.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(f'{self.dateToday}'))
            #table hour value
            self.mainForm.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(f'{dados[0]}:00'))
            #table par value
            self.mainForm.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(dados_1))
            #table dir value
            self.mainForm.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(dados_2.upper()))
            #table timeframe value
            self.mainForm.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(f'{self.timeframe}'))
            #table Status value
            self.mainForm.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem('Em espera...'))

            row += 1

            with open(f'sinais corrigidos.txt', 'a') as file:
                file.write(f'{sinais}\n')

    def homePage(self):
        self.mainForm.stackedWidget.setCurrentIndex(0)
        self.mainForm.currentWindow.setText('HOME')

    def settingsPage(self):
        self.mainForm.stackedWidget.setCurrentIndex(1)
        self.mainForm.currentWindow.setText('SETTINGS')

    def config(self):
        pass
