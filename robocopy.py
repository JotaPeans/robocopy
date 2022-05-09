from datetime import datetime, timedelta
from iqoptionapi.stable_api import IQ_Option
from rich.console import Console
import os
import sys
import time
import threading
from getpass import getpass

console = Console()

class Robo:
    def __init__(self):    
        os.system('cls')    
        user = input("Email: ")
        senha = getpass(prompt="Password: ")
        self.API = IQ_Option(user, senha)
        self.count = 0
        self.timeframe = 5
        self.Exit = threading.Event()
        self.connect()


    def corrigir_sinais(self):
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


    def connect(self):
        self.API.connect()

        if self.API.check_connect():
            os.system('cls')
            console.print(':heavy_check_mark: [bold green]Conectado com sucesso![/bold green]')
            if os.path.exists('sinais corrigidos.txt'):
                os.remove('sinais corrigidos.txt')
                self.corrigir_sinais()
            else:
                self.corrigir_sinais()
        else:
            os.system('cls')
            console.print('[red]Erro ao conectar, tente novamente[/]')
            console.print('\n\nAperte [cyan]Enter[/] para tentar novamente')
            input()
            self.count += 1
            self.__init__()


    def config(self):
        # Define o tipo de operação
        console.print('\n[bold cyan]Tipo de operação[/bold cyan] ([bold green]REAL[/ bold green] OU [bold yellow]PRACTICE[/bold yellow]): ', style='italic', end = '')
        self.modo = input()
        self.modo = self.modo.upper()

        # Muda qual banca o robo vai operar
        self.API.change_balance(self.modo)
        
        # StopWin e StopLoss ativado ou desativado
        console.print('\n[bold cyan]Operar com StopWIN e StopLOSS [/bold cyan][bold yellow](Y/N)[/bold yellow]? ', end = '')
        self.stop = input()
        self.stop = self.stop.upper()
        
        # Tendencia, sim ou nao
        console.print('\n[bold cyan]Utilizar análise de tendência[/bold cyan] [bold yellow](Y/N)[/bold yellow][cyan]? ', end = '')
        self.tend = input()
        self.tend = self.tend.upper()
        
        # MartinGale
        console.print('\n[bold cyan]Operar com 0, 1 ou 2 martingale(s)?[/bold cyan] [bold yellow](0/1/2)[/bold yellow][cyan]? [/]', end = '')
        self.gale = int(input())

        self.bancaINC = self.API.get_balance()
        self.amount = float(self.bancaINC) * 0.01
        self.amount = round(self.amount, 2)
        self.StopWIN = self.bancaINC + (self.bancaINC * 0.05)
        self.StopWIN = round(self.StopWIN, 2)
        self.StopLOSS = self.bancaINC - (self.bancaINC * 0.035)
        self.StopLOSS = round(self.StopLOSS, 2)

        time.sleep(0.1)
        if self.modo == 'PRACTICE':
            console.print(f'   :pushpin: [bold white]Modo escolhido:[/bold white] [bold yellow]{self.modo}[/bold yellow]')
        elif self.modo == 'REAL':
            console.print(f'   :pushpin: [bold white]Modo escolhido:[/bold white] [bold green]{self.modo}[/bold green]')
        time.sleep(0.1)
        console.print(f'   :pushpin: [bold white]Banca:[/bold white] [bold green]R$ {self.bancaINC}[/bold green]')
        time.sleep(0.1)
        console.print(f'   :pushpin: [bold white]Valor da entrada de [/bold white][bold yellow]1%[/bold yellow][bold white] da banca:[/bold white] [bold green]R$ {self.amount}[/bold green]')
        time.sleep(0.1)
        if self.stop == 'Y':
            console.print(f'   :pushpin: [bold white]StopWIN de[/bold white] [bold green]5%[/bold green]: [bold cyan]{self.StopWIN}[/bold cyan]')
            time.sleep(0.1)
            console.print(f'   :pushpin: [bold white]StopLOSS de[/bold white] [bold red]3,5%[/bold red]: [bold cyan]{self.StopLOSS}[/bold cyan]')
            time.sleep(0.1)
        else:
            pass
        print('\n')
        self.analise()


    def tendencia(self, par, timeframe):
        velas = self.API.get_candles(par, (int(timeframe) * 60), 15,  time.time())
        ultimo = round(velas[0]['close'], 5)
        primeiro = round(velas[-1]['close'], 5)
        diferenca = abs(round(((ultimo - primeiro) / primeiro) * 100, 5))
        tendencia = "call" if ultimo < primeiro and diferenca > 0.01 else "put" if ultimo > primeiro and diferenca > 0.01 else False
        return tendencia


    def payout(self, par):
        prc = self.API.get_all_profit()
        return float(prc[par]['turbo'])
    

    def carregar_sinais(self):
        file = open('sinais corrigidos.txt', encoding='UTF-8')
        lista = file.read()
        file.close

        lista = lista.split('\n')

        for index, a in enumerate(lista):
            if a == '':
                del lista[index]

        return lista


    def analise(self):
        while True:
            time.sleep(0.5)
            if not self.Exit.is_set():
                self.delay = 2
                hora = datetime.now()
                self.hora_c_delay = hora + timedelta(seconds=self.delay)
                self.hora_c_delay = self.hora_c_delay.strftime("%H:%M:%S")
                console.print(f"[{hora.strftime('%H:%M:%S')}] :: [bold white]Aguardando operação... - Banca: [/ bold white][bold green]R$ {self.API.get_balance()}[/ bold green]", end='\r')

                lista = self.carregar_sinais()
                for sinal in lista:
                    dados = sinal.split(',')
                    if self.hora_c_delay == dados[0]:
                        if self.tend == 'Y':
                            tend_func = self.tendencia(str(dados[1]), int(dados[3]))
                            if tend_func == False:      #TIRAR SE QUISER
                                console.print(f'\n\n    :warning: [bold white]ATIVO[/bold white] [bold yellow][{str(dados[1])}][/bold yellow] [bold white]COM TENDÊNCIA DE LATERIZAÇÃO![/bold white]\n')
                                
                            elif tend_func != str(dados[2]):
                                console.print(f'\n\n    :stop_sign: [bold white]ATIVO[/bold white] [bold yellow][{str(dados[1])}][/bold yellow] [bold red]CONTRA[/bold red] [bold white]A TENDÊNCIA![/bold white]\n')

                            elif tend_func == str(dados[2]):
                                if self.Exit.is_set():
                                    print('\n\n')
                                    console.print('[cyan]Encerrando...[/]')
                                    sys.exit()
                                else:
                                    console.print(f'\n   [bold white]:arrow_lower_right: Abrindo operação - [/bold white][bold yellow][{str(dados[1])}][/bold yellow] [bold white]-> [/bold white]' + ("[bold green]CALL[/]" if str(dados[2]) == 'call' else "[bold red]PUT[/]\n"))
                                    self.buy(str(dados[1]), str(dados[2]), int(dados[3]), amount=self.amount)
                        
                        else:
                            console.print(f'\n   [bold white]:arrow_lower_right: Abrindo operação - [/bold white][bold yellow][{str(dados[1])}][/bold yellow] [bold white]-> [/bold white]' + ("[bold green]CALL[/]" if str(dados[2]) == 'call' else "[bold red]PUT[/]\n"))
                            self.buy(str(dados[1]), str(dados[2]), int(dados[3]), amount=self.amount)

            else:
                print('\n\n')
                console.print('[cyan]Encerrando...[/]')
                sys.exit()
    

    def buy(self, par, dir, timeframe, amount, method = "digital", gale=1):

        par = str(par)
        dir = str(dir)
        timeframe = int(timeframe)

        if method == "digital":
            status, id = self.API.buy_digital_spot(par, amount, dir, timeframe)
            if status == False:
                self.buy(par, dir, timeframe, amount, method = "binary")
            else:
                status = False
                time.sleep((timeframe * 60) - 10)
                i = 0
                while not status:
                    status, lucro = self.API.check_win_digital_v2(id)
                    time.sleep(0.5)
                    i += 0.5
                    if i == 20:
                        console.print("[bold red]Time out, ordem nao adquirida[/]")

        elif method == "binary":
            status, id = self.API.buy(amount, par, dir, timeframe)
            if status:
                status = False
                time.sleep((timeframe * 60) - 10)
                i = 0 
                while True:
                    lucro = self.API.check_win_v3(id)
                    time.sleep(0.5)
                    i += 0.5
                    if i == 20:
                        console.print("[bold red]Time out, ordem nao adquirida[/]")
                    else:
                        break
            
        try:
            if lucro > 0:
                console.print(f'\n   :heavy_dollar_sign:[green]WIN[/] para [bold yellow][{par}][/ bold yellow] - Lucro de [bold cyan]R$[/]', round(lucro, 2), style = 'bold')
                if self.stop == 'Y' and self.API.get_balance() >= self.StopWIN:
                    console.print('\n   :heavy_dollar_sign:[green]StopWIN Atingido[/], [cyan]volte amanhã...[/]', style = 'bold')
                    self.Exit.set()
                else:
                    self.amount = float(self.API.get_balance()) * 0.01
                    self.amount = round(self.amount, 2)
            else:
                console.print(f'\n   :x: [red]LOSS[/] para [bold yellow][{par}][/ bold yellow] - Perca de [bold cyan]R$[/]', round(lucro, 2), style = 'bold')
                if self.gale == 1:
                    self.buy(par, dir, timeframe)
                elif self.gale == 2:
                    if gale == 1:
                        console.print(f'\n   [bold white]:arrow_lower_right: Executando Martingale - ordem 1 - [/bold white][bold yellow][{par}][/bold yellow] [bold white]-> [/bold white]' + ("[bold green]CALL[/]" if dir == 'call' else "[bold red]PUT[/]\n"))
                        self.buy(par, dir, timeframe, gale = 2, amount = ((self.amount / self.payout(par)) + self.amount))
                    elif gale == 2:
                        console.print(f'\n   [bold white]:arrow_lower_right: Executando Martingale - ordem 2 - [/bold white][bold yellow][{par}][/bold yellow] [bold white]-> [/bold white]' + ("[bold green]CALL[/]" if dir == 'call' else "[bold red]PUT[/]\n"))
                        self.buy(par, dir, timeframe, gale = None, amount = (((((self.amount / self.payout(par)) + self.amount) + self.amount) / self.payout(par)) + self.amount))
                    else:
                        self.amount = self.amount + ((((self.amount / self.payout(par)) + self.amount) + (((((self.amount / self.payout(par)) + self.amount) + self.amount) / self.payout(par)) + self.amount)) + self.amount) / self.payout(par)
                        self.amount = round(self.amount, 2)
        except:
            console.print("\n[bold red]Erro ao adiquirir a Ordem![/]\n")


Robo()