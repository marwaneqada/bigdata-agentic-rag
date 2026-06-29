# Script de vidéo — maximum 2 minutes

**0:00–0:15**  
Bonjour, je présente mon assistant Agentic RAG spécialisé en Big Data et Cloud. Il utilise
LangGraph, une base vectorielle Chroma, des embeddings multilingues et le modèle Groq.

**0:15–0:35**  
Voici le graphe. Le système analyse la question, choisit entre recherche, comparaison ou
calcul, évalue les documents récupérés, reformule la requête si nécessaire, génère puis
vérifie la réponse. La mémoire utilise un thread de conversation.

**0:35–1:05**  
Je pose une question simple : « Quel est le rôle d'Airflow ? ». L'application montre la
réponse, les sources, le score de pertinence et le temps.

**1:05–1:35**  
Je pose une question complexe : « Compare HDFS et MinIO ». Le système choisit l'outil de
comparaison et utilise des extraits des deux supports.

**1:35–1:50**  
Je montre le calcul de stockage avec réplication. Ce résultat vient d'un outil
déterministe et non d'une estimation du modèle.

**1:50–2:00**  
Enfin, le projet contient une évaluation automatique de 10 questions simples et
10 questions complexes, avec qualité, temps et pertinence documentaire.
