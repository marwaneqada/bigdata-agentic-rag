# Rapport — Assistant Agentic RAG Big Data & Cloud

**Étudiant : Marwane Qada**

> Maximum demandé : 4 pages. Remplacer les champs entre crochets après l'exécution réelle.

## 1. Objectif et base documentaire

Le projet vise à développer un assistant capable de répondre à des questions complexes
sur le Big Data et le Cloud à partir de supports de cours. La base contient des documents
sur Apache Airflow, Hadoop HDFS, MinIO, Kafka Streams, Spark SQL et Spark Structured
Streaming.

Les documents sont extraits, nettoyés, découpés en chunks puis vectorisés avec
`paraphrase-multilingual-MiniLM-L12-v2`. Les embeddings sont stockés dans Chroma.

## 2. Architecture Agentic RAG

Le système utilise un `StateGraph` LangGraph construit manuellement. Le routeur choisit
entre recherche documentaire, comparaison et calcul. Les documents sont évalués avant la
génération. Une requête peu pertinente est reformulée au maximum deux fois. La réponse
est ensuite vérifiée par un nœud de groundedness.

La mémoire conversationnelle est assurée par un checkpointer et un `thread_id`.

Outils :
- recherche documentaire ;
- comparaison de technologies ;
- calcul de capacité de stockage.

Insérer ici la figure `results/langgraph_workflow.svg`.

## 3. Évaluation

Le système a été testé avec 10 questions simples et 10 questions complexes.

- Temps moyen : **[X] secondes**
- Qualité moyenne : **[X]/5**
- Pertinence documentaire : **[X]/5**
- Groundedness : **[X]/5**

Ajouter un petit tableau avec 4 à 6 exemples représentatifs et commenter les différences
entre questions simples et complexes.

## 4. Limites et améliorations

Limites possibles :
- dépendance à la qualité des supports ;
- téléchargement initial du modèle d'embeddings ;
- évaluation LLM imparfaite ;
- mémoire en RAM non persistante après redémarrage ;
- couverture limitée aux documents indexés.

Améliorations :
- checkpointer SQLite ou PostgreSQL ;
- reranker CrossEncoder ;
- davantage de supports ;
- citations plus précises ;
- authentification et journalisation.
