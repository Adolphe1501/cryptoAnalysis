#!/bin/bash

# Démarrez le serveur SSH au démarrage du conteneur
service ssh start 

# Démarrez le service Hadoop
/root/start-hadoop.sh
# Créez les répertoires HDFS
hdfs dfs -mkdir -p HistData-input 
hdfs dfs -mkdir -p MonthlyData-input

# Gardez le conteneur en vie
tail -f /dev/null
