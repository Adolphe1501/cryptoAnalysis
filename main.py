import select
import sys
import tty
import termios
import psutil
import schedule
from predictRt import predictRealTime
from collectRtDataKafka import collectRtdatakafka
from collectHistDataHdfs import collectHistDataHdfs
from collectMonthlyDataHdfs import collectMonthlyDataHdfs
from prediction import trainModel
def getChar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

result = collectHistDataHdfs()
result = collectMonthlyDataHdfs()
result = trainModel()

# Planifier les tâches
schedule.every().day.at("00:30").do(collectMonthlyDataHdfs)
schedule.every().week.at("00:30").do(collectHistDataHdfs)
schedule.every().week.at("00:30").do(trainModel)

with open("dashboardRt.py") as f:
    code = compile(f.read(), "dashboardRt.py", 'exec')
    exec(code)

print("La plateforme d'analyse et de prediction de cryptos est disponible sur http://127.0.0.1:8050/")
print(" ")
print(" Appuyez sur s pour stopper l'application")

def stop_process(name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == name:
            proc.kill()


while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        key_stroke = getChar()
        if(key_stroke == 's'):
            print(f"Vous avez decider d'arreter l'application")
            stop_process('dashboardRt.py')      
            break
    else:
        schedule.run_pending()
        collectRtdatakafka()
        predictRealTime()

