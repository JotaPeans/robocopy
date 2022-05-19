from PyQt6 import uic, QtWidgets
import os
from datetime import datetime

mainWindow = QtWidgets.QApplication([])


class Ui_BotWindow:
    def __init__(self) -> None:
        self.dateToday = datetime.now().strftime('%d-%m-%Y')
        self.timeframe = 5
        self.mainForm = uic.loadUi('ui/MainWindow.ui')
        self.mainForm.tableWidget.setColumnWidth(4, 70)
        self.mainForm.tableWidget.setColumnWidth(5, 132)
        self.mainForm.tableWidget.setColumnWidth(1, 76)
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
            if lista[0] == 'Mestre dos sinais VIP':
                try:
                    dados = x.split(', ')
                    horario = f'{dados[0]}:00'
                    par = dados[1].replace(' ', '')
                    timeframe = dados[2].replace('M1', '1')
                    timeframe = timeframe.replace('M5', '5')
                    timeframe = timeframe.replace('M15', '15')
                    dir = dados[3].replace(' ', '')
                    dir = dir.lower()
                    sinal = f'{horario},{par},{dir},{timeframe}'
                    self.showTable(lista=lista, row=row, horario=horario, par=par, dir=dir, timeframe=timeframe)
                    self.writeFile(sinal=sinal)
                    row += 1
                except:
                    print('erro de formatação')
            
            elif lista[0] == 'Tigre dos Sinais':
                try:
                    dados = x.split(' ')
                    horario = f'{dados[0]}:00'
                    par = dados[1].replace(' ', '')
                    dir = dados[3].replace(' ', '')
                    dir = dir.lower()
                    sinal = f'{horario},{par},{dir},{self.timeframe}'
                    self.showTable(lista=lista, row=row, horario=horario, par=par, dir=dir, timeframe=str(self.timeframe))
                    self.writeFile(sinal=sinal)
                    row += 1
                except:
                    print('erro de formatação')

    def homePage(self):
        self.mainForm.stackedWidget.setCurrentIndex(0)
        self.mainForm.currentWindow.setText('HOME')

    def settingsPage(self):
        self.mainForm.stackedWidget.setCurrentIndex(1)
        self.mainForm.currentWindow.setText('SETTINGS')

    def showTable(self, lista:list, row:int, horario:str, par:str, dir:str, timeframe:str):
        self.mainForm.tableWidget.setRowCount(len(lista))
        #table date value
        self.mainForm.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(f'{self.dateToday}'))
        #table hour value
        self.mainForm.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(horario))
        #table par value
        self.mainForm.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(par))
        #table dir value
        self.mainForm.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(dir.upper()))
        #table timeframe value
        self.mainForm.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(timeframe))
        #table Status value
        self.mainForm.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem('Em espera...'))

    def writeFile(self, sinal:str):
        with open(f'sinais corrigidos.txt', 'a') as file:
            file.write(f'{sinal}\n')