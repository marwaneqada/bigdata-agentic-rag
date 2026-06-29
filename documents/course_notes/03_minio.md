# MinIO et le stockage objet compatible S3

Source de cours : Atelier Big Data Stockage Objet avec MinIO.

Le stockage objet représente les données sous forme d'objets. Un objet contient la donnée,
des métadonnées et une clé unique. Contrairement à un système de fichiers classique,
l'organisation se fait avec des buckets, des objets, des clés et des métadonnées.

Un bucket est un conteneur logique. Un objet peut être un CSV, une image, un log, un PDF
ou un modèle d'intelligence artificielle. La clé d'objet identifie l'objet dans le bucket,
par exemple `ventes/2026/ventes.csv`. Les métadonnées décrivent notamment la taille, le
type, la date, le propriétaire ou les permissions.

MinIO fournit une API compatible S3. Le port 9000 est utilisé par l'API S3 et les
applications. Le port 9001 est utilisé par la console Web d'administration. La console
permet de créer des buckets, déposer des objets, observer les métadonnées, télécharger et
supprimer des objets.

## Déploiement Docker

Un service Docker MinIO utilise l'image `minio/minio`. La commande de serveur peut préciser
`--console-address ":9001"`. Un volume monté sur `/data` permet de conserver les données
après le redémarrage du conteneur.

Les variables `MINIO_ROOT_USER` et `MINIO_ROOT_PASSWORD` définissent les identifiants
administrateur. Après `docker compose up -d`, `docker compose ps` vérifie le conteneur et
`docker compose logs -f minio` affiche ses logs.

## API S3 et Postman

Postman peut accéder à MinIO avec l'autorisation AWS Signature. Une requête PUT dépose un
objet, GET le télécharge, HEAD retourne ses métadonnées et une requête avec
`?list-type=2` liste les objets d'un bucket.

MinIO est particulièrement utile quand des applications doivent utiliser des opérations
S3 et manipuler des objets par HTTP. HDFS stocke des fichiers découpés en blocs distribués,
alors que MinIO expose une abstraction de stockage objet avec buckets, clés et API S3.
