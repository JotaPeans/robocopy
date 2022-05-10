from datetime import datetime, timedelta
from iqoptionapi.stable_api import IQ_Option
import sys
import time

class Robo:
    def __init__(self):    
        self.__operationMode = None #Real ou Practice -> str
        self.__stop = None #True or False -> bool
        self.__tend = None #True or False -> bool
        self.__tendCandles = None #numero de velas para o calculo da tendencia -> int
        self.__gale = None #0 - 1 - 2 -> int
        self.__bancaINC = None #float
        self.__amount = None #float
        self.__StopWIN = None #float or percent
        self.__StopLOSS = None #float or percent
        self.__payout = None #porcentagem

    @property
    def operationMode(self) -> str:
        return self.__operationMode

    @operationMode.setter
    def operationMode(self, mode:str):
        self.__operationMode = mode

    @property
    def stop(self) -> bool:
        return self.__stop

    @stop.setter
    def stop(self, mode:bool):
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
        self.__amount = num

    @property
    def stopWin(self) -> float:
        return self.__StopWIN
    
    @stopWin.setter
    def stopWin(self, num:float) -> float:
        self.__StopWIN = num

    @property
    def stopLoss(self) -> float:
        return self.__StopLOSS

    @stopLoss.setter
    def stopLoss(self, num:float) -> float:
        self.__StopLOSS = num


    def config(self):
        self.amount = float(self.bancaINC) * 0.01
        self.amount = round(self.amount, 2)
        self.StopWIN = self.bancaINC + (self.bancaINC * 0.05)
        self.StopWIN = round(self.StopWIN, 2)
        self.StopLOSS = self.bancaINC - (self.bancaINC * 0.035)
        self.StopLOSS = round(self.StopLOSS, 2)


    def tendencia(self, par, timeframe):
        velas = self.API._candles(par, (int(timeframe) * 60), self.__tendCandles,  time.time())
        ultimo = round(velas[0]['close'], 5)
        primeiro = round(velas[-1]['close'], 5)
        diferenca = abs(round(((ultimo - primeiro) / primeiro) * 100, 5))
        tendencia = "call" if ultimo < primeiro and diferenca > 0.01 else "put" if ultimo > primeiro and diferenca > 0.01 else False
        return tendencia


    def payout(self, par):
        prc = self.API._all_profit()
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
            if not self.Exit.is_():
                self.delay = 2
                hora = datetime.now()
                self.hora_c_delay = hora + timedelta(seconds=self.delay)
                self.hora_c_delay = self.hora_c_delay.strftime("%H:%M:%S")
                console.print(f"[{hora.strftime('%H:%M:%S')}] :: [bold white]Aguardando operação... - Banca: [/ bold white][bold green]R$ {self.API._balance()}[/ bold green]", end='\r')

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
                                if self.Exit.is_():
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
                if self.stop == 'Y' and self.API._balance() >= self.StopWIN:
                    console.print('\n   :heavy_dollar_sign:[green]StopWIN Atingido[/], [cyan]volte amanhã...[/]', style = 'bold')
                    self.Exit()
                else:
                    self.amount = float(self.API._balance()) * 0.01
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

