from datetime import datetime, timedelta
from threading import Thread, Event
from time import sleep, time

from PyQt6 import uic, QtWidgets, QtCore
from PyQt6.QtCore import QPropertyAnimation, QRect

from iqoptionapi.stable_api import IQ_Option
from BotWindow import Ui_MainWindow
import sys
import os


class LoginWindow:
    def __init__(self) -> None:
        self.__operationMode = None #Real ou Practice -> str
        self.__stop = None #True or False -> bool
        self.__tend = None #True or False -> bool
        self.__tendCandles = None #numero de velas para o calculo da tendencia -> int
        self.__gale = None #0 - 1 - 2 -> int
        self.__bancaINC = None #float
        self.__amount = None #float
        self.__StopWIN = None #float or percent
        self.__StopLOSS = None #float or percent

        self.wins = 0 #int
        self.hits = 0 #int
        self.winPercentage = 100.0 #float

        self.loginForm = uic.loadUi('ui/login.ui')
        self.loginForm.Login.clicked.connect(self.getLoginValues)

        self.Exit = Event()

        if os.path.exists('remember.txt'):
            self.loginForm.rememberMe.click()
            file = open('remember.txt', encoding='UTF-8')
            email = file.read()
            self.loginForm.user.setText(email)

    @property
    def operationMode(self) -> str:
        return self.__operationMode

    @operationMode.setter
    def operationMode(self, mode:str) -> str:
        self.__operationMode = mode

    @property
    def stop(self) -> bool:
        return self.__stop

    @stop.setter
    def stop(self, mode:bool) -> bool:
        self.__stop = mode

    @property
    def tend(self) -> bool:
        return self.__tend

    @tend.setter
    def tend(self, mode:bool) -> bool:
        self.__tend = mode

    @property
    def tendCandles(self) -> int:
        return self.__tendCandles

    @tendCandles.setter
    def tendCandles(self, num:int) -> int:
        self.__tendCandles = num

    @property
    def gale(self) -> int:
        return self.__gale

    @gale.setter
    def gale(self, num:int) -> int:
        self.__gale = num

    @property
    def bancaInicial(self) -> float:
        return self.__bancaINC

    @bancaInicial.setter
    def bancaInicial(self, num:float) -> float:
        self.__bancaINC = num

    @property
    def amount(self) -> float:
        return self.__amount

    @amount.setter
    def amount(self, num:float) -> float:
        if num < 1:
            self.__amount = self.API.get_balance() * num
        else:
            self.__amount = num

    @property
    def stopWin(self) -> float:
        return self.__StopWIN
    
    @stopWin.setter
    def stopWin(self, num:float) -> float:
        if num < 1:
            self.__StopWIN = self.__bancaINC * num
        else:
            self.__StopWIN = num

    @property
    def stopLoss(self) -> float:
        return self.__StopLOSS

    @stopLoss.setter
    def stopLoss(self, num:float) -> float:
        if num < 1:
            self.__StopLOSS = self.__bancaINC * num
        else:
            self.__StopLOSS = num

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
        self.loginForm.hide() #fecha a tela de login!
        self.mainWindow = Ui_MainWindow()
        self.main = self.mainWindow.mainForm
        self.main.saveSettings.clicked.connect(lambda: Thread(target=self.configs, daemon=True).start())
        self.main.iniciar.clicked.connect(lambda: Thread(target=self.operation, daemon=True).start())
        self.main.finalizar.clicked.connect(lambda: self.Exit.set())
        self.main.inserirFile.clicked.connect(self.chooseFile)

        # daemon -> diz que se a thread principal terminar, ele termina tb
        Thread(target=self.hours, daemon=True).start()

        self.initConfigs()

    def pushStopWin(self):
        self.anim = QPropertyAnimation(self.main.stopWin, b"geometry")
        self.anim.setDuration(200)
        self.anim.setStartValue(QRect(190,-65, 321,61))
        self.anim.setEndValue(QRect(190,30, 321,61))
        self.anim.start()

    def pushStopLoss(self):
        self.anim = QPropertyAnimation(self.main.stopLoss, b"geometry")
        self.anim.setDuration(200)
        self.anim.setStartValue(QRect(190,-65, 321,61))
        self.anim.setEndValue(QRect(190,30, 321,61))
        self.anim.start()

    def hours(self):
        while True:
            hour = datetime.now().strftime('%H:%M:%S')
            self.main.horaLine.setText(hour)
            self.main.saldoLine.setText(str(self.API.get_balance()))
            if self.wins != 0:
                prct = (self.wins / (self.hits + self.wins)) * 100
                prct = round(prct, 2)
                if prct > 0:
                    self.main.prctLine.setText(f'{prct} %')
                else:
                    self.main.prctLine.setText('0.0 %')

            sleep(1)

    def initConfigs(self):
        entryHour = datetime.now().strftime('%H:%M:%S')
        self.operationMode = self.API.change_balance(self.main.operationMode.currentText().upper())
        self.main.winsLine.setText(str(self.wins))
        self.main.hitsLine.setText(str(self.hits))
        self.main.prctLine.setText('0.0 %')
        self.main.output.append(f'[{entryHour}] - Conectado com Sucesso!')

    def refreshWins_Hits(self):
        self.main.winsLine.setText(str(self.wins))
        self.main.hitsLine.setText(str(self.hits))

    def configs(self):
        # seta o modo de operação
        self.operationMode = self.API.change_balance(self.main.operationMode.currentText().upper())
        # seta a banca inicial
        self.bancaInicial = self.API.get_balance()


        # calcula o valor da entrada:
        if self.main.entryType.currentText() == 'Valor':
            self.amount = self.main.entryValue.value()

        elif self.main.entryType.currentText() == 'Porcentagem':
            self.amount = self.main.entryValue.value() / 100


        # Verifica se vai ser usado StopWin e StopLoss
        if self.main.stopType.currentText() == 'Valor':
            self.stop = True
            self.stopWin = float(self.main.stopWinValue.value())
            self.stopLoss = float(self.main.stopLossValue.value())

        elif self.main.stopType.currentText() == 'Porcentagem':
            self.stop = True
            self.stopWin = float(self.main.stopWinValue.value()) / 100
            self.stopLoss = float(self.main.stopLossValue.value()) / 100

        elif self.main.stopType.currentText() == 'Não Usar':
            self.stop = False


        # verifica se será usado tendência
        if self.main.tendenciaCheckBox.isChecked():
            self.tend = True
            self.tendCandles = int(self.main.QntdVelasSpinBox.value())
        else:
            self.tend = False


        # seta o valor dos gales
        self.gale = int(self.main.galeValue.currentText())

        # coloca na tela inicial quanto tem na banca
        self.main.saldoLine.setText(str(self.bancaInicial))

        # mostra que foi salvo com sucesso!
        self.main.saveLabel.setText('Configurações Salvas com sucesso!')
        sleep(2)
        self.main.saveLabel.setText('')

    def chooseFile(self):
        self.arquivo = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.mainWindow.corrigirSinais(caminho=self.arquivo)
        self.main.FileWay.setText(self.arquivo)

    def tendencia(self, par, timeframe):
        velas = self.API._candles(par, (int(timeframe) * 60), self.__tendCandles,  time.time())
        ultimo = round(velas[0]['close'], 5)
        primeiro = round(velas[-1]['close'], 5)
        diferenca = abs(round(((ultimo - primeiro) / primeiro) * 100, 5))
        tendencia = "call" if ultimo < primeiro and diferenca > 0.01 else "put" if ultimo > primeiro and diferenca > 0.01 else False
        return tendencia

    def outputs(self, outputstring:str):
        hour = datetime.now().strftime('%H:%M:%S')
        self.main.output.append(f'[{hour}] - {outputstring}')

    def payout(self, par):
        prc = self.API.get_all_profit()
        return float(prc[par]['binary'])

    def operation(self):
        self.main.saveLabel.setText('Operações iniciadas!')
        sleep(2)
        self.main.saveLabel.setText('')
        
        self.main.statusLine.setText('Em Operação!')
        file = open('sinais corrigidos.txt', encoding='UTF-8')
        lista = file.read()
        file.close

        lista = lista.split('\n')

        for index, a in enumerate(lista):
            if a == '':
                del lista[index]

        while not self.Exit.is_set():
            sleep(1)
            self.analise(lista=lista)

    def analise(self, lista):
        self.delay = 2
        hora = datetime.now()
        self.hora_c_delay = hora + timedelta(seconds=self.delay)
        self.hora_c_delay = self.hora_c_delay.strftime("%H:%M:%S")

        index = 0
        for sinal in lista:
            dados = sinal.split(',')
            if self.hora_c_delay == dados[0]:
                if self.tend:
                    sinalTendencia = self.tendencia(str(dados[1]), int(dados[3]))

                    if sinalTendencia != str(dados[2]):
                        outputString = f'Ativo [{str(dados[1])}] contra a tendência!'
                        self.outputs(outputString)

                    elif sinalTendencia == str(dados[2]):
                        outputString = f'Abrindo operação - [{str(dados[1])}] -> {str(dados[2]).upper()}'
                        self.outputs(outputString)
                        Thread(target=self.buy, args=(str(dados[1]), str(dados[2]), int(dados[3]), self.amount), daemon=True).start()
                        self.main.tableWidget.setItem(index, 5, QtWidgets.QTableWidgetItem('Operação aberta'))
                else:
                    outputString = f'Abrindo operação - [{str(dados[1])}] -> {str(dados[2]).upper()}'
                    self.outputs(outputString)
                    Thread(target=self.buy, args=(str(dados[1]), str(dados[2]), int(dados[3]), self.amount, index), daemon=True).start()
                    self.main.tableWidget.setItem(index, 5, QtWidgets.QTableWidgetItem('Operação aberta'))

            index += 1

    def buy(self, par:str, dir:str, timeframe:int, amount:float, index:int, method="digital", gale=1):
        par = str(par)
        dir = str(dir)
        timeframe = int(timeframe)

        if method == "digital":
            status, id = self.API.buy_digital_spot(par, amount, dir, timeframe)
            if status == False:
                self.buy(par, dir, timeframe, amount, method = "binary")
            else:
                status = False
                sleep((timeframe * 60) - 10)
                i = 0
                while not status:
                    status, lucro = self.API.check_win_digital_v2(id)
                    sleep(0.5)
                    i += 0.5
                    if i == 20:
                        outputString = f'Time out, ordem [{par}] nao adquirida'
                        self.outputs(outputString)

        elif method == "binary":
            status, id = self.API.buy(amount, par, dir, timeframe)
            if status:
                status = False
                sleep((timeframe * 60) - 10)
                i = 0 
                while True:
                    lucro = self.API.check_win_v3(id)
                    sleep(0.5)
                    i += 0.5
                    if i == 20:
                        outputString = f'Time out, ordem [{par}] nao adquirida'
                        self.outputs(outputString)
                        break
                    elif lucro != None :
                        break
            
        try:
            diferenca = self.API.get_balance() - self.__bancaINC

            if lucro > 0:
                outputString = f'WIN - [{par}] - Lucro de R$ {round(lucro, 2)}'
                self.outputs(outputString)
                self.main.tableWidget.setItem(index, 5, QtWidgets.QTableWidgetItem('WIN'))
                self.wins += 1
                self.refreshWins_Hits()

                if self.stop == True and diferenca >= self.stopWin:
                    outputString = 'StopWIN Atingido, volte amanhã...'
                    self.outputs(outputString)
                    self.pushStopWin()
                    self.Exit.set()

                else:
                    self.amount = float(self.API.get_balance()) * 0.01
                    self.amount = round(self.amount, 2)
                    
            else:
                outputString = f'LOSS - [{par}] - Perca de R$ {round(lucro, 2)}'
                self.outputs(outputString)
                self.main.tableWidget.setItem(index, 5, QtWidgets.QTableWidgetItem('LOSS'))
                self.hits += 1
                self.refreshWins_Hits()

                if self.gale == 1:
                    self.buy(par, dir, timeframe, amount = ((self.amount / self.payout(par)) + self.amount), index=index)
                    
                elif self.gale == 2:
                    if gale == 1:
                        outputString = f'Executando Martingale - ordem 1 - [{par}] -> {dir.upper()}'
                        self.outputs(outputString)
                        self.main.tableWidget.setItem(index, 5, QtWidgets.QTableWidgetItem('MARTINGALE 1'))
                        self.buy(par, dir, timeframe, gale = 2, amount = ((self.amount / self.payout(par)) + self.amount), index=index)
                    
                    elif gale == 2:
                        outputString = f'Executando Martingale - ordem 2 - [{par}] -> {dir.upper()}'
                        self.outputs(outputString)
                        self.main.tableWidget.setItem(index, 5, QtWidgets.QTableWidgetItem('MARTINGALE 2'))
                        self.buy(par, dir, timeframe, gale = None, amount = (((((self.amount / self.payout(par)) + self.amount) + self.amount) / self.payout(par)) + self.amount), index=index)
                    
                    else:
                        self.amount = self.amount + ((((self.amount / self.payout(par)) + self.amount) + (((((self.amount / self.payout(par)) + self.amount) + self.amount) / self.payout(par)) + self.amount)) + self.amount) / self.payout(par)
                        self.amount = round(self.amount, 2)

                if self.stop == True and diferenca >= self.stopLoss:
                    outputString = 'StopLoss Atingido, volte amanhã...'
                    self.outputs(outputString)
                    self.pushStopLoss()
                    self.Exit.set()
        except:
            outputString = 'Erro ao adiquirir a Ordem!'
            self.outputs(outputString)

if __name__ == '__main__':
    login = QtWidgets.QApplication([])
    W = LoginWindow()
    W.loginForm.show()

    sys.exit(login.exec())

