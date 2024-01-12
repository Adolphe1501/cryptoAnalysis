<p align="center">
  <img src="https://img.icons8.com/?size=512&id=55494&format=png" width="100" />
</p>
<p align="center">
    <h1 align="center">CRYPTOANALYSIS</h1>
</p>
<p align="center">
    <em><code> This project is a cryptocurrency market analysis project that uses historical and real time data to predict the future value over 1 day, 3 days, 7 days and 30 days.</code></em>
</p>
<p align="center">
	<!-- Shields.io badges not used with skill icons. --><p>
<p align="center">
		<em>This project is not an investment consultancy and has been developed in conjunction with the software and tools below and more( Hadoop, Spark, Dash, ...).</em>
</p>
<p align="center">
	<a href="https://skillicons.dev">
		<img src="https://skillicons.dev/icons?i=fastapi,docker,kafka,py,tensorflow&theme=light">
	</a></p>
<hr>




##  Overview

<code> 
Ce projet est une tentative de comprendre et de prédire les tendances du marché des cryptomonnaies en utilisant des techniques d’analyse de données avancées. Cependant, il est important de noter que les prédictions fournies par ce projet ne doivent pas être utilisées comme des conseils d’investissement. Les marchés des cryptomonnaies sont extrêmement volatils et imprévisibles, et il est toujours recommandé de faire ses propres recherches et de consulter un conseiller financier professionnel avant de prendre des décisions d’investissement.</code>

---

##  Repository Structure

```sh
└── cryptoAnalysis/
    ├── Dockerfile
    ├── Dockerfile.hadoop-master
    ├── Dockerfile.hadoop-slave
    ├── collectHistDataHdfs.py
    ├── collectMonthlyDataHdfs.py
    ├── collectRtDataKafka.py
    ├── dashboardRt.py
    ├── docker-compose.yml
    ├── main.py
    ├── predictRt.py
    ├── prediction.py
    ├── requirements.txt
    ├── start-hadoop.sh
    ├── start-kafka.sh
    └── start-zookeeper.sh
```


---

##  Getting Started

***Requirements***

Ensure you have the following dependencies installed on your system:

* **Docker with docker-compose ( Docker desktop maybe a better fit )**: `version >= 4.12`

###  Installation

1. Clone the cryptoAnalysis repository:

```sh
git clone https://github.com/Adolphe1501/cryptoAnalysis.git
```

2. Change to the project directory:

```sh
cd cryptoAnalysis
```


###  Running cryptoAnalysis

Use the following command to run cryptoAnalysis (Make sure to have enough Memory allocated to your containers for model updating (recommended : 10Gb)):

```sh
docker-compose build 
docker-compose up
```
You should get this on [http://127.0.0.1:8050](http://127.0.0.1:8050)


##  Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Submit Pull Requests](https://github/Adolphe1501/cryptoAnalysis.git/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **[Join the Discussions](https://github/Adolphe1501/cryptoAnalysis.git/discussions)**: Share your insights, provide feedback, or ask questions.
- **[Report Issues](https://github/Adolphe1501/cryptoAnalysis.git/issues)**: Submit bugs found or log feature requests for Cryptoanalysis.

<details closed>
    <summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a Git client.
   ```sh
   git clone https://github.com/Adolphe1501/cryptoAnalysis.git
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.

Once your PR is reviewed and approved, it will be merged into the main branch.

</details>

---

##  License

This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

