from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import col, explode
import requests
import json
import time
import datetime

def collectMonthlyDataHdfs():
        
    # Obtenir le temps actuel
    now = datetime.datetime.now()

    # Obtenir le temps il y a 5 ans
    ten_years_ago = now - datetime.timedelta(days=31)

    # Convertir en temps Unix en millisecondes
    end = int(now.timestamp() * 1000)
    start = int(ten_years_ago.timestamp() * 1000)



    # Fonction pour la collecte des données historiques par Crypto
    def collecte_donnees_historiques_crypto():
        i=0
        while i==0:
            i+=1
            # Initialisez la session Spark
            spark = SparkSession.builder.appName("HistoricalCryptoData").getOrCreate()

            data_historique_crypto = {}
            
            data = requests.get('https://api.coincap.io/v2/assets', params={'limit' : '2000'}).json()
            for crypto in data['data'] :
                # Appel à l'API historique par Crypto
                response = requests.get('https://api.coincap.io/v2/assets/'+crypto['id']+'/history?interval=d1', params={'start': start, 'end': end})
                if (response.status_code == 429) :
                    time.sleep(30) # si on atteint le nombre maximal de requete par minute on patiente 30s avant de relancer
                    response = requests.get('https://api.coincap.io/v2/assets/'+crypto['id']+'/history?interval=d1', params={'start': start, 'end': end})
                    
                if('error' not in response.json()):
                    data_historique_crypto[crypto['id']] = response.json()['data']
                else :
                    break
            # Convertir le dictionnaire en liste de dictionnaires
            data_list = []
            for crypto, crypto_data in data_historique_crypto.items():
                for entry in crypto_data:
                    entry["crypto"] = crypto
                    data_list.append(entry)

            # Créer le DataFrame Spark
            df = spark.createDataFrame(data_list)

            # Afficher le schéma
            df.printSchema()
            # Écrire dans HDFS
            df.write.mode("overwrite").parquet("hdfs://hadoop-master:9000/root/MonthlyData-input/")

            # Arrêtez la session Spark
            spark.stop()
            
            

    # Démarrage de la collecte des données historiques par Crypto
    collecte_donnees_historiques_crypto()
