# Spark SQL et analyse de données structurées

Source de cours : activité pratique Spark SQL.

Spark SQL permet d'analyser des données structurées avec des DataFrames et des requêtes SQL.
Une SparkSession initialise l'application. Un fichier CSV peut être lu avec une ligne
d'en-tête et une inférence de schéma.

L'exploration commence par l'affichage du schéma, des premières lignes et du nombre
d'enregistrements. Les valeurs nulles peuvent être supprimées ou traitées avant l'analyse.

Une vue temporaire associe un nom SQL à un DataFrame. Après
`createOrReplaceTempView("bike_rentals_view")`, une requête
`SELECT ... FROM bike_rentals_view` peut utiliser les colonnes du DataFrame. La vue est
temporaire et liée à la session Spark.

Spark SQL prend en charge les filtres, les agrégations, les regroupements et les analyses
temporelles. Pour un jeu de locations de vélos, il est possible de rechercher les locations
de plus de 30 minutes, calculer le revenu total, compter les locations par station, calculer
la durée moyenne, extraire l'heure de départ et identifier les heures de pointe.

Spark SQL convient aux analyses batch ou interactives sur des données déjà disponibles.
Kafka Streams est plutôt utilisé pour transformer des événements continus. Structured
Streaming étend le modèle DataFrame aux traitements en flux et micro-batch.
