from PyQt6 import uic, QtWidgets
import sys

mainWindow = QtWidgets.QApplication([])


class Ui_MainWindow:
    def __init__(self) -> None:
        self.timeframe = 5
        self.mainForm = uic.loadUi('ui/MainWindow.ui')
        self.corrigirSinais()

        # Set Home Page
        self.mainForm.stackedWidget.setCurrentIndex(0)
        # Home Page!
        self.mainForm.HomeButton.clicked.connect(self.homePage)
        # Settings Page!
        self.mainForm.SettingsButton.clicked.connect(self.settingsPage)

        self.mainForm.show()

    def corrigirSinais(self):
        file = open('sinais.txt', encoding='UTF-8')
        lista = file.read()
        file.close

        lista = lista.split('\n')

        print(lista)

        for x in lista:
            dados = x.split(' ')
            dados_1 = dados[1].replace(' ', '')
            dados_2 = dados[2].replace(' ', '')
            dados_2 = dados_2.lower()
            sinais = f'{dados[0]}:00,{dados_1},{dados_2},{self.timeframe}'
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
