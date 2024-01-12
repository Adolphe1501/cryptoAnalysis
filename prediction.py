from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer
from pyspark.ml import Pipeline
from pyspark.sql.functions import unix_timestamp, col
from pyspark.sql.types import FloatType

def trainModel():
        
    # Initialiser Spark
    spark = SparkSession.builder.appName("crypto_prediction").getOrCreate()

    # Charger les données historiques depuis HDFS
    historical_data = spark.read.parquet("hdfs://hadoop-master:9000/root/HistData-input/")

    # Ajouter une colonne "crypto_index" pour indexer les cryptos
    indexer = StringIndexer(inputCol="crypto", outputCol="crypto_index")
    pipeline = Pipeline(stages=[indexer])
    historical_data = pipeline.fit(historical_data).transform(historical_data)

    # Filtrage des colonnes inutiles
    historical_data = historical_data.drop("time")

    # Gestion des valeurs manquantes
    historical_data = historical_data.na.drop()

    # Conversion des types de données
    historical_data = historical_data.withColumn("priceUsd", col("priceUsd").cast(FloatType()))

    # Convertir la colonne "date" en timestamp
    historical_data = historical_data.withColumn("timestamp", unix_timestamp("date", "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'").cast("double"))

    # Statistiques descriptives
    historical_data.describe().show()

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
    sorted_data = historical_data.orderBy(col("crypto"), col("date"))

    # Diviser les données en ensemble d'entraînement et ensemble de test
    train_data, test_data = sorted_data.randomSplit([0.8, 0.2], seed=42)

    # Convertir les données en un DataFrame Pandas
    train_data = train_data.toPandas()
    test_data = test_data.toPandas()

    # Initialiser les listes pour les caractéristiques et les cibles
    train_features = []
    test_features = []
    train_target = []
    test_target = []
    n_steps_in = 30  # Nombre de pas de temps à utiliser comme entrée
    n_steps_out = 30  # Nombre de pas de temps à prédire


    # Pour chaque crypto, créer des fenêtres glissantes de 30 jours pour les caractéristiques et les cibles
    for crypto in train_data['crypto'].unique():
        crypto_data = train_data[train_data['crypto'] == crypto]
        for i in range(len(crypto_data)-n_steps_in-n_steps_out):
            train_features.append(crypto_data[i:i+n_steps_in][['crypto_index', 'timestamp', 'priceUsd']].values)
            train_target.append(crypto_data[i+n_steps_in:i+n_steps_in+n_steps_out]['priceUsd'].values)

    for crypto in test_data['crypto'].unique():
        crypto_data = test_data[test_data['crypto'] == crypto]
        for i in range(len(crypto_data)-n_steps_in-n_steps_out):
            test_features.append(crypto_data[i:i+n_steps_in][['crypto_index', 'timestamp', 'priceUsd']].values)
            test_target.append(crypto_data[i+n_steps_in:i+n_steps_in+n_steps_out]['priceUsd'].values)

    # Convertir les listes en tableaux NumPy
    X_train = np.array(train_features)
    X_test = np.array(test_features)
    y_train = np.array(train_target)
    y_test = np.array(test_target)

    # Normaliser les caractéristiques et les cibles
    feature_scaler = MinMaxScaler(feature_range=(0, 1))
    X_train = feature_scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
    X_test = feature_scaler.fit_transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)

    target_scaler = MinMaxScaler(feature_range=(0, 1))
    y_train = target_scaler.fit_transform(y_train)
    y_test = target_scaler.fit_transform(y_test)

    # Construire le modèle LSTM
    def build_lstm_model(input_shape, output_shape):
        model = Sequential()
        model.add(Bidirectional(LSTM(50, return_sequences=True), input_shape=input_shape))
        model.add(Bidirectional(LSTM(50)))
        model.add(Dense(output_shape))
        model.compile(optimizer=Adam(lr=0.01), loss='mse')
        return model

    lstm_model = build_lstm_model((X_train.shape[1], X_train.shape[2]), n_steps_out)

    # Entraîner le modèle LSTM avec arrêt précoce
    early_stopping = EarlyStopping(monitor='val_loss', patience=10)
    lstm_model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=2, validation_split=0.2, callbacks=[early_stopping])

    # Sauvegarder le modèle
    lstm_model.save("model5/")

    #Charger le modèle sauvegardé
    loaded_model = load_model("model5/")

    # Prédire les prix
    train_predict = loaded_model.predict(X_train)
    test_predict = loaded_model.predict(X_test)

    print("Train Predict :", train_predict)
    print("Test Predict :", test_predict)
    # Inverse transformer les valeurs mises à l'échelle
    y_train_inv = target_scaler.inverse_transform(y_train)
    train_predict_inv = target_scaler.inverse_transform(train_predict)
    y_test_inv = target_scaler.inverse_transform(y_test)
    test_predict_inv = target_scaler.inverse_transform(test_predict)

    # Aplatir les dimensions supplémentaires
    y_train_inv_flat = y_train_inv.reshape(-1, 1)
    train_predict_inv_flat = train_predict_inv.reshape(-1, 1)
    y_test_inv_flat = y_test_inv.reshape(-1, 1)
    test_predict_inv_flat = test_predict_inv.reshape(-1, 1)

    # Remettre les données dans leur forme originale
    y_train_inv = y_train_inv.reshape(y_train.shape)
    train_predict_inv = train_predict_inv.reshape(train_predict.shape)
    y_test_inv = y_test_inv.reshape(y_test.shape)
    test_predict_inv = test_predict_inv.reshape(test_predict.shape)


    print("Train Predict Inverse :", train_predict_inv)
    print("Test Predict Inverse :", test_predict_inv)

    # Calculer RMSE pour chaque prédiction
    train_rmse = np.mean([sqrt(mean_squared_error(y_train_inv[i], train_predict_inv[i])) for i in range(len(y_train))])
    print("LSTM Train RMSE: ", train_rmse)

    test_rmse = np.mean([sqrt(mean_squared_error(y_test_inv[i], test_predict_inv[i])) for i in range(len(y_test))])
    print("LSTM Test RMSE: ", test_rmse)
