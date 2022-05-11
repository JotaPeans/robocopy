from datetime import datetime

sinal = "15:23:00"

date_now = datetime.now()
date_now = date_now.strftime("%d/%m/%Y")

string_date = f'{date_now} - {sinal}'
formater = "%d/%m/%Y - %H:%M:%S"
sinal_date = datetime.strptime(string_date, formater)

tempo_restante = str(sinal_date - datetime.now())
tempo_restante = tempo_restante[:7]
tempo_restante = tempo_restante.split(':')

tempo_restante_seconds = 0
hora = int(tempo_restante[0])
mins = int(tempo_restante[1])
secs = int(tempo_restante[2])

tempo_restante_seconds += (hora * 3600) + (mins * 60) + secs

print(tempo_restante, tempo_restante_seconds)