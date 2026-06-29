# Hadoop HDFS : stockage distribué, blocs et réplication

Source de cours : Atelier pratique Hadoop HDFS avec Docker.

HDFS est un système de fichiers distribué conçu pour stocker de grands volumes de données
sur plusieurs machines. Un cluster HDFS contient un NameNode et plusieurs DataNodes.

Le NameNode gère les métadonnées : noms et chemins des fichiers, blocs associés aux fichiers,
emplacement des blocs et informations de réplication. Il ne stocke pas directement le
contenu utilisateur. Les DataNodes stockent réellement les blocs.

Lorsqu'un fichier est envoyé dans HDFS, il est découpé en blocs. Ces blocs sont distribués
sur différents DataNodes. La réplication conserve plusieurs copies de chaque bloc. Si un
DataNode tombe en panne, les données restent accessibles depuis les autres copies.

## Commandes essentielles

`hdfs dfs -mkdir -p /datalake/ventes/raw` crée une arborescence. L'option `-p` crée
automatiquement les dossiers parents. Une organisation de Data Lake peut séparer les
zones `raw`, `processed` et `archive`.

`hdfs dfs -put fichier.csv /datalake/ventes/raw/` dépose un fichier local dans HDFS.
`hdfs dfs -ls -R /datalake` affiche l'arborescence. `hdfs dfs -cat` lit un fichier.
`hdfs dfs -cp` copie, `hdfs dfs -mv` déplace ou renomme et `hdfs dfs -rm` supprime.
`hdfs dfs -get` télécharge un fichier HDFS vers le système local.

`hdfs dfsadmin -report` présente l'état du cluster. `hdfs fsck` permet d'analyser les
fichiers, les blocs et leur réplication.

## HDFS et tolérance aux pannes

Le facteur de réplication indique le nombre de copies physiques de chaque bloc. Un facteur
3 signifie que chaque bloc existe trois fois, ce qui augmente la disponibilité mais
multiplie aussi la capacité physique requise. Pour 500 GB sans compression avec un facteur
3, il faut environ 1500 GB de stockage brut.

Dans un atelier Docker, plusieurs DataNodes peuvent être simulés sur une seule machine.
Dans un environnement réel, ils sont répartis sur plusieurs serveurs. HDFS est adapté aux
fichiers volumineux et aux traitements distribués, mais il n'est pas conçu comme une API
de stockage objet compatible S3.
