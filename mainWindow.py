from PyQt6 import uic, QtWidgets
import sys

mainWindow = QtWidgets.QApplication([])

class Ui_MainWindow:
    def __init__(self) -> None:
        self.mainForm = uic.loadUi('ui/MainWindow.ui')
        self.mainForm.pushButton.clicked.connect(self.config)
        self.mainForm.show()

    def corrigirSinais(self):
        file = open('sinais.txt', encoding='UTF-8')
        lista = file.read()
        file.close

        lista = lista.split('\n')

        for index, a in enumerate(lista):
            if a == '':
                del lista[index]
        try:
            for x in lista:
                dados = x.split(' ')
                dados_1 = dados[1].replace(' ', '')
                dados_2 = dados[3].replace(' ', '')
                dados_2 = dados_2.lower()
                sinais = f'{dados[0]}:00,{dados_1},{dados_2},{self.timeframe}'
                with open(f'sinais corrigidos.txt', 'a') as file:
                    file.write(f'{sinais}\n')
        except:
            pass
        self.config()

    def config(self):
        print('oi')