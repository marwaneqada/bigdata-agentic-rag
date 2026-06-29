# Kafka Streams : traitement d'événements en temps réel

Source de cours : TP Traitement de flux avec Kafka Streams.

Kafka Streams est une bibliothèque Java permettant de développer des applications de
traitement de flux directement au-dessus d'Apache Kafka. Elle consomme des événements
depuis des topics, transforme et filtre les messages, effectue des agrégations et publie
les résultats dans d'autres topics.

Un KStream représente un flux continu d'événements indépendants. Une KTable représente
une vue continuellement mise à jour, souvent produite par une agrégation. Un
KGroupedStream est un flux regroupé par clé utilisé avec `count`, `reduce` ou `aggregate`.

Un topic d'entrée fournit les messages à l'application. Un topic de sortie contient les
résultats. Un Dead Letter Topic stocke les messages invalides ou rejetés afin de ne pas
les perdre et de permettre leur analyse.

## Nettoyage et validation

Un pipeline de texte peut lire `text-input`, supprimer les espaces inutiles, remplacer les
espaces multiples, convertir en majuscules puis valider les messages. Les messages valides
sont publiés dans `text-clean`. Les messages vides, trop longs ou contenant un mot interdit
sont routés vers `text-dead-letter`.

Cette stratégie sépare les événements propres des événements problématiques sans arrêter
le flux complet.

## Comptage de clics

Une architecture orientée événements peut contenir une application Web productrice,
un traitement Kafka Streams et une API REST consommatrice. Chaque clic produit un
événement dans le topic `clicks`. Kafka Streams calcule un total global ou un total par
utilisateur, puis publie le résultat dans `click-counts`. Une API REST expose ensuite le
compteur.

Kafka Streams est adapté aux événements continus et aux réactions à faible latence.
Airflow orchestre des étapes et des dépendances, alors que Kafka Streams transforme
continuellement les événements qui traversent Kafka.
