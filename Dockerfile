# Utilisez une image de base Python
FROM python:3.10

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Installez Java et nettoyez le cache apt
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless && \
    apt-get clean;

# Définissez JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64


# Copiez les fichiers de requirements dans le conteneur
COPY requirements.txt .

# Installez les packages Python avec pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste des fichiers de votre application dans le conteneur
COPY . .

# Exécutez votre application
CMD ["python", "main.py"]

