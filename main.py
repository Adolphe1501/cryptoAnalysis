import select
import sys
import psutil
import schedule
from predictRt import predictRealTime
from collectRtDataKafka import collectRtdatakafka
from collectHistDataHdfs import collectHistDataHdfs
from collectMonthlyDataHdfs import collectMonthlyDataHdfs
from prediction import trainModel

result = collectHistDataHdfs()
result = collectMonthlyDataHdfs()

# Planifier les tâches
schedule.every().day.at("00:30").do(collectMonthlyDataHdfs)
schedule.every(7).days.at("00:40").do(collectHistDataHdfs)
schedule.every(7).days.at("00:50").do(trainModel)


collect = collectRtdatakafka()
collect = predictRealTime()
with open("dashboardRt.py") as f:
    code = compile(f.read(), "dashboardRt.py", 'exec')
    exec(code)


while True:
    
    schedule.run_pending()
    collect = collectRtdatakafka()
    predictRealTime()

