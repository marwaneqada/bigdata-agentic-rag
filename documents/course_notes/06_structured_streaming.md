# Spark Structured Streaming avec HDFS

Source de cours : TP Analyse quasi temps réel de mesures de capteurs.

Spark Structured Streaming permet de traiter des données qui arrivent progressivement en
utilisant l'API DataFrame. Dans un scénario de capteurs, des fichiers CSV sont déposés dans
un dossier HDFS et lus automatiquement par l'application.

Le programme définit un schéma explicite pour garantir les types des colonnes et éviter une
inférence répétée. Il peut calculer des statistiques en continu, filtrer des mesures et
détecter des valeurs anormales.

Un checkpoint enregistre la progression et l'état du traitement. Si l'application redémarre
avec le même checkpoint, elle peut reprendre sans retraiter toute la source. Les checkpoints
sont essentiels aux agrégations et à la tolérance aux pannes.

`maxFilesPerTrigger` limite le nombre de nouveaux fichiers traités à chaque déclenchement.
Structured Streaming fonctionne généralement en micro-batch : les données reçues pendant
un petit intervalle sont traitées comme un lot court.

Le mode `append` écrit les nouvelles lignes finales. Le mode `complete` réécrit la table
complète des résultats et convient aux agrégations dont les valeurs évoluent.

Les alertes peuvent être enregistrées dans HDFS au format Parquet. Une colonne `statut`
peut contenir `NORMAL` ou `ANORMAL`. Des seuils différents peuvent être appliqués selon
le type de capteur, par exemple une température supérieure à 35 ou une humidité supérieure
à 80.

Kafka est plus adapté qu'une source HDFS quand les événements arrivent continuellement,
avec une faible latence et un besoin de lecture ordonnée depuis des topics. HDFS est adapté
à l'arrivée progressive de fichiers et au stockage distribué.
