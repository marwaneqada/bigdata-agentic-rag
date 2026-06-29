# Apache Airflow pour l'orchestration des pipelines Big Data

Source de cours : Atelier Apache Airflow.

Apache Airflow est une plateforme d'orchestration de workflows. Son rôle est de définir,
planifier, exécuter et surveiller des pipelines. Il ne remplace pas les moteurs de traitement
comme Spark, Flink ou Kafka Streams : il organise leur exécution et leurs dépendances.

Un pipeline Big Data typique peut contenir l'ingestion, le stockage brut, la validation,
le nettoyage, la transformation, le calcul d'indicateurs, le chargement des résultats et
la génération d'un rapport. Airflow permet de préciser l'ordre de ces étapes, d'observer
leur état et de relancer les tâches qui échouent.

## DAG et tâches

Un DAG, Directed Acyclic Graph, est un graphe orienté sans cycle. Dans Airflow, il représente
un pipeline composé de tâches et de dépendances. Le DAG définit les tâches à exécuter,
leur ordre, la fréquence d'exécution et le comportement en cas d'échec.

Une tâche est une étape individuelle du pipeline. Un Operator indique comment cette tâche
est exécutée. PythonOperator exécute une fonction Python, BashOperator lance une commande
Bash et EmptyOperator sert à structurer le graphe.

Le scheduler décide quand les DAGs et les tâches doivent être lancés. Le worker exécute
réellement les tâches. L'interface Web permet d'activer les DAGs, de les déclencher,
d'observer la vue Graph, de consulter les logs et de relancer une tâche échouée.

## Planification et fiabilité

`schedule=None` signifie que le DAG est déclenché manuellement. `@daily` indique une
planification quotidienne et `@hourly` une planification horaire. Une expression cron
comme `0 2 * * *` lance le DAG tous les jours à 2 heures.

Les retries permettent de relancer automatiquement une tâche après un échec temporaire.
Le paramètre `retries=2` autorise deux nouvelles tentatives. `retry_delay` définit le délai
entre les tentatives. Cette stratégie est utile en cas de serveur indisponible, de fichier
retardé, de panne réseau ou de base momentanément inaccessible.

Les logs sont essentiels pour identifier l'étape ayant échoué et comprendre les messages
produits par les fonctions Python. La vue Graph montre les dépendances et les tâches
réussies, en cours ou échouées.

## Parallélisme

Un DAG n'est pas obligatoirement linéaire. Après une validation, plusieurs traitements
peuvent s'exécuter en parallèle, par exemple une analyse par ville et une analyse par
produit. Une tâche de rapport final attend ensuite la fin des deux branches.

Airflow rend un pipeline automatisé, supervisé, traçable, fiable, maintenable et
compréhensible. Sa valeur principale est la coordination des outils dans une architecture
Data Engineering.
