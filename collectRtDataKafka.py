from confluent_kafka import Producer, KafkaException
import requests
import json
import time

def collectRtdatakafka():

    # Configuration du producteur Kafka pour les données en temps réel
    conf = {
        'bootstrap.servers': 'kafka:9092',  # Remplacez par l'adresse de votre broker Kafka
        'message.max.bytes': 10000000  # Ajustez cette valeur en fonction de la taille de vos messages
    }

    producer = Producer(conf)

    # Fonction pour la collecte des données en temps réel
    def collecte_donnees_temps_reel(api_url, api_params, topic):
        i=0
        while i==0:
            try:
                # Appel à l'API en temps réel
                response = requests.get(api_url, params=api_params)
                data = response.json()

                # Envoi des données à Kafka
                producer.produce(topic, value=json.dumps(data))

                print("Données en temps réel envoyées à Kafka:", data)

                # Attendre la livraison du message
                producer.flush()

                # Pause entre chaque collecte (ajustez selon vos besoins)
                time.sleep(60)  # Une minute entre chaque collecte
            except KafkaException as e:
                print("Erreur lors de l'envoi des données en temps réel à Kafka:", str(e))
            except Exception as e:
                print("Erreur lors de la collecte des données en temps réel:", str(e))
            i+=1

    # Remplacez ceci par l'URL de l'API de cryptomonnaie en temps réel
    api_url_temps_reel = 'https://api.coincap.io/v2/assets'

    api_params = {
        'limit': '2000',
        # Ajoutez d'autres paramètres au besoin
    }

    # Remplacez ceci par le nom du topic auquel vous souhaitez envoyer les données en temps réel
    topic_temps_reel = 'cryptoProducerTempsReel'

    # Démarrage de la collecte des données en temps réel
    collecte_donnees_temps_reel(api_url_temps_reel, api_params, topic_temps_reel)
