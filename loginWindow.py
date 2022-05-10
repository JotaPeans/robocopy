from datetime import datetime
from threading import Thread
from time import sleep
from PyQt6 import uic, QtWidgets
from iqoptionapi.stable_api import IQ_Option
import sys
import os
from mainWindow import Ui_MainWindow
from robocopy import Robo


class LoginWindow:
    def __init__(self) -> None:
        self.bot = Robo()
        self.loginForm = uic.loadUi('ui/login.ui')
        self.loginForm.Login.clicked.connect(self.getLoginValues)

        if os.path.exists('remember.txt'):
            self.loginForm.rememberMe.click()
            file = open('remember.txt', encoding='UTF-8')
            email = file.read()
            self.loginForm.user.setText(email)

        self.loginForm.show()

    def getLoginValues(self):
        self.user = self.loginForm.user.text()
        self.password = self.loginForm.password.text()
        self.warning = self.loginForm.warning

        if self.user or self.password == '':
            if self.user == '':
                self.changeUserStyleSheet()

            if self.password == '':
                self.changePasswordStyleSheet()

        if self.user and self.password != '':
            self.API = IQ_Option(self.user, self.password)

            if self.loginForm.rememberMe.isChecked():
                with open('remember.txt', 'w') as file:
                    file.write(self.user)

            else:
                if os.path.exists('remember.txt'):
                    os.remove('remember.txt')

            self.connect()

    def changeUserStyleSheet(self):
        self.loginForm.user.setStyleSheet('''QLineEdit {
                                            border-radius: 25px;
                                            border: 2px solid red;
                                            padding: 10px;
                                    }
                                    QLineEdit:focus {
                                        border: 2px solid black;
                                    }
                                    ''')
        self.warning.setText('Preencha todos os campos!')

    def changePasswordStyleSheet(self):
        self.loginForm.password.setStyleSheet('''QLineEdit {
                                                border-radius: 25px;
                                                border: 2px solid red;
                                                padding: 10px;
                                        }
                                        QLineEdit:focus {
                                            border: 2px solid black;
                                        }''')
        self.warning.setText('Preencha todos os campos!')

    def changeWarningStyleSheet(self):
        self.warning.setStyleSheet('color: rgb(0, 170, 91);')

    def connect(self):
        self.API.connect()

        if self.API.check_connect():
            self.changeWarningStyleSheet()
            self.warning.setText('Conectado com sucesso!')
            self.principalWindow()
        else:
            self.warning.setText('Erro ao conectar, tente novamente.')

    def principalWindow(self):
        self.mainWindow = Ui_MainWindow()
        self.main = self.mainWindow.mainForm
        self.main.saveSettings.clicked.connect(lambda: Thread(target=self.configs, daemon=True).start())
        # daemon -> diz que se a thread principal terminar, ele termina tb
        Thread(target=self.hours, daemon=True).start()

        self.initConfigs()

    def hours(self):
        while True:
            hour = datetime.now().strftime('%H:%M:%S')
            self.main.horaLine.setText(hour)
            sleep(1)

    def initConfigs(self):
        entry = datetime.now().strftime('%H:%M:%S')
        self.bot.operationMode = self.API.change_balance(self.main.operationMode.currentText().upper())
        self.main.output.append(f'[{entry}] - Conectado com Sucesso!')

    def configs(self):
        # seta o modo de operação
        self.bot.operationMode = self.API.change_balance(
            self.main.operationMode.currentText().upper())
        # seta a banca inicial
        self.bot.bancaInicial = self.API.get_balance()

        # calcula o valor da entrada:
        if self.main.entryType.currentText() == 'Valor':
            self.bot.amount = self.main.entryValue.value()
        else:
            self.bot.amount = self.main.entryValue.value() / 100

        # Verifica se vai ser usado StopWin e StopLoss
        if self.main.stopType.currentText() == 'Valor':
            self.bot.stop = True
            self.bot.stopWin = float(self.main.stopWinValue.value())
            self.bot.stopLoss = float(self.main.stopLossValue.value())

        elif self.main.stopType.currentText() == 'Porcentagem':
            self.bot.stop = True
            self.bot.stopWin = float(self.main.stopWinValue.value()) / 100
            self.bot.stopLoss = float(self.main.stopLossValue.value()) / 100

        elif self.main.stopType.currentText() == 'Não Usar':
            self.bot.stop = False

        # verifica se será usado tendência
        if self.main.tendenciaCheckBox.isChecked():
            self.bot.tend = True
            self.bot.tendCandles = self.main.QntdVelasSpinBox.value()
        else:
            self.bot.tend = False

        # seta o valor dos gales
        self.bot.gale = int(self.main.galeValue.currentText())

        # coloca na tela inicial quanto tem na banca
        self.main.saldoLine.setText(str(self.bot.bancaInicial))

        # mostra que foi salvo com sucesso!
        self.main.saveLabel.setText('Configurações Salvas com sucesso!')
        sleep(2)
        self.main.saveLabel.setText('')


login = QtWidgets.QApplication([])
LoginWindow = LoginWindow()

sys.exit(login.exec())
