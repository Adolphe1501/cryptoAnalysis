from confluent_kafka import Consumer, TopicPartition
import json
from sklearn.preprocessing import MinMaxScaler
from pyspark.ml.feature import StringIndexer
from pyspark.sql.functions import unix_timestamp, col
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.sql.types import FloatType
import numpy as np
from keras.models import load_model

def predictRealTime() :
        
    def get_last_message(topic):
        consumer = Consumer({
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'beforePredictionReaders',
        'auto.offset.reset': 'earliest'
    })

        partition = TopicPartition(topic, 0, -1)  # -1 signifie "dernier message"
        last_offset = consumer.get_watermark_offsets(partition)[1] - 1  # obtenir l'offset du dernier message
        if last_offset < 0:
            return None  # le topic est vide

        partition.offset = last_offset
        consumer.assign([partition])

        msg = consumer.consume(num_messages=1, timeout=1.0)
        if msg:
            return msg[0].value().decode('utf-8')  # renvoie la valeur du dernier message
        else:
            return None  # aucun message n'a été consommé

    # Initialiser Spark
    spark = SparkSession.builder.appName("crypto_prediction").getOrCreate()

    cryptos = json.loads(get_last_message('cryptoProducerTempsReel'))

    # Charger les données historiques depuis HDFS
    monthly_data = spark.read.parquet("hdfs://hadoop-master:9000/root/MonthlyData-input/")

    # Ajouter une colonne "crypto_index" pour indexer les cryptos
    indexer = StringIndexer(inputCol="crypto", outputCol="crypto_index")
    pipeline = Pipeline(stages=[indexer])
    monthly_data = pipeline.fit(monthly_data).transform(monthly_data)

    # Filtrage des colonnes inutiles
    monthly_data = monthly_data.drop("time")

    # Gestion des valeurs manquantes
    monthly_data = monthly_data.na.drop()

    # Conversion des types de données
    monthly_data = monthly_data.withColumn("priceUsd", col("priceUsd").cast(FloatType()))

    # Convertir la colonne "date" en timestamp
    monthly_data = monthly_data.withColumn("timestamp", unix_timestamp("date", "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'").cast("double"))

    # Statistiques descriptives
    monthly_data.describe().show()

    # Importer les bibliothèques nécessaires
    from keras.models import Sequential, load_model
    from keras.layers import Dense, LSTM, Bidirectional
    from keras.optimizers import Adam
    from keras.callbacks import EarlyStopping
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_squared_error
    from math import sqrt
    import numpy as np

    # Trier les données par crypto et par date
    sorted_data = monthly_data.orderBy(col("crypto"), col("date"))

    # Convertir les données en un DataFrame Pandas
    predict_data = sorted_data.toPandas()
    # Initialiser les listes pour les caractéristiques et les cibles
    predict_features = []
    n_steps_in = 30  # Nombre de pas de temps à utiliser comme entrée
    n_steps_out = 30  # Nombre de pas de temps à prédire

    # Pour chaque crypto, créer des fenêtres glissantes de 30 jours pour les caractéristiques et les cibles
    for crypto in predict_data['crypto'].unique():
        crypto_data = predict_data[predict_data['crypto'] == crypto]
        if len(crypto_data) >= n_steps_in:
            predict_features.append(crypto_data[-n_steps_in:][['crypto_index', 'timestamp', 'priceUsd']].values)
            
    # Convertir les listes en tableaux NumPy
    X_predict = np.array(predict_features)
    print("X_predict" , X_predict)
    # Normaliser les caractéristiques et les cibles
    feature_scaler = MinMaxScaler(feature_range=(0, 1))
    X_predict = feature_scaler.fit_transform(X_predict.reshape(-1, X_predict.shape[-1])).reshape(X_predict.shape)
    # Normaliser les cibles
    target_scaler = MinMaxScaler(feature_range=(0, 1))
    Y_predict = target_scaler.fit_transform(monthly_data.select('priceUsd').collect())

    # Charger le modèle sauvegardé
    loaded_model = load_model("model5/")

    # Prédire le 'priceUsd' pour les 30 prochains jours pour chaque crypto
    predicted_prices = []
    for i in range(0, X_predict.shape[0], n_steps_in):
        # Utiliser les données en temps réel pour la première prédiction
        input_data = X_predict[i:i+n_steps_in]
        # Faire des prédictions
        predicted_price = loaded_model.predict(input_data)
        # Aplatir predicted_price
        predicted_price_flat = predicted_price.flatten()
        # Ajouter predicted_price_flat à la liste
        predicted_prices.append(predicted_price_flat)


    # Find the maximum length of subarrays in predicted_prices
    max_len = max(len(x) for x in predicted_prices)

    # Pad shorter subarrays with np.nan
    predicted_prices_padded = [np.pad(x, (0, max_len - len(x)), 'constant', constant_values=np.nan) for x in predicted_prices]

    # Now you can safely convert predicted_prices_padded to a NumPy array
    predicted_prices_np = np.array(predicted_prices_padded)

    predicted_prices_flat = predicted_prices_np.reshape(-1, 30)

    # Inverse transformer les valeurs mises à l'échelle
    predicted_prices_inv = target_scaler.inverse_transform(predicted_prices_flat)

    # Initialiser le dictionnaire de prédictions
    predictions = {}
    print(len(predict_data['crypto'].unique()))
    # Pour chaque crypto, ajouter les prédictions au dictionnaire
    unique_cryptos = predict_data['crypto'].unique()
    if len(unique_cryptos) > len(predicted_prices_inv):
        unique_cryptos = unique_cryptos[:len(predicted_prices_inv)]

    for i, crypto in enumerate(unique_cryptos): 
        predictions[crypto] = {
            "1_day": predicted_prices_inv[i, 0],
            "3_days": predicted_prices_inv[i, 2],
            "1_week": predicted_prices_inv[i, 6],
            "1_month": predicted_prices_inv[i, 29]
        }

    # Pour chaque crypto dans la liste de cryptos
    for i in range(len(cryptos['data'])):
        # Obtenir l'ID de la crypto
        crypto_id = cryptos['data'][i]['id']
        
        # Vérifier si des prédictions existent pour cette crypto
        if crypto_id in predictions:
            # Ajouter les prédictions à l'objet crypto
            cryptos['data'][i]['1_day prediction'] = str(float(cryptos['data'][i]['priceUsd']) + float(predictions[crypto_id]['1_day']))
            cryptos['data'][i]['3_days prediction'] = str(float(cryptos['data'][i]['priceUsd']) + float(predictions[crypto_id]['3_days']))
            cryptos['data'][i]['1_week prediction'] = str(float(cryptos['data'][i]['priceUsd']) + float(predictions[crypto_id]['1_week']))
            cryptos['data'][i]['1_month prediction'] = str(float(cryptos['data'][i]['priceUsd']) + float(predictions[crypto_id]['1_month']))

    print(cryptos['data'])

    import csv
    csv_columns = ['id','rank','symbol','name','supply', 'maxSupply', 'marketCapUsd', 'volumeUsd24Hr', 'priceUsd',  'changePercent24Hr', 'vwap24Hr', 'explorer', '1_day prediction', '3_days prediction', '1_week prediction','1_month prediction' ]

    csv_file = "realtimeCrypto.csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in cryptos['data']:
                writer.writerow(data)
    except IOError:
        print("I/O error")
