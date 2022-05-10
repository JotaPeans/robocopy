from time import sleep
from PyQt6 import uic, QtWidgets
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime, timedelta
from rich.console import Console
import sys
import os
from mainWindow import Ui_MainWindow

console = Console()

class LoginWindow:
    def __init__(self) -> None:
        self.loginForm = uic.loadUi('ui/login.ui')
        self.loginForm.Login.clicked.connect(self.getLoginValues)

        if os.path.exists('remember.txt'):
            self.loginForm.rememberMe.click()
            file =  open('remember.txt', encoding='UTF-8')
            email = file.read()
            print(email)
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
        self.warning.setStyleSheet('color: rgb(0, 170, 91);;')

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


login = QtWidgets.QApplication([])
LoginWindow = LoginWindow()

sys.exit(login.exec())