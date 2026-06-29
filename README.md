# Big Data Agentic RAG — Marwane Qada

Assistant pédagogique Agentic RAG consacré aux technologies Big Data et Cloud, construit manuellement avec LangGraph.

Repository :
https://github.com/marwaneqada/bigdata-agentic-rag

## Objectif

Ce projet permet d’interroger une base documentaire de cours portant sur :

* Apache Airflow
* Hadoop HDFS
* MinIO
* Kafka Streams
* Spark SQL
* Spark Structured Streaming

L’assistant sélectionne automatiquement le chemin d’exécution adapté à la question : recherche documentaire, comparaison de technologies ou calcul de capacité de stockage.

## Fonctionnalités

* Chargement de documents PDF, Markdown et TXT
* Découpage des documents en chunks
* Embeddings multilingues avec Sentence Transformers
* Base vectorielle persistante Chroma
* LLM Groq avec sorties structurées
* `StateGraph` LangGraph construit manuellement
* Aucun usage de `create_agent`
* Routage automatique des questions
* Recherche vectorielle
* Évaluation individuelle de la pertinence des chunks
* Reformulation automatique lorsque les documents sont insuffisants
* Vérification de la groundedness des réponses
* Mémoire conversationnelle par `thread_id`
* Interface Streamlit
* Visualisation du graphe en Mermaid et SVG
* Évaluation sur 10 questions simples et 10 questions complexes
* Export des résultats en CSV et JSON

## Corpus documentaire

Le corpus fourni contient 6 documents Markdown dans :

```text
documents/course_notes/
```

Documents indexés :

* `01_airflow.md`
* `02_hdfs.md`
* `03_minio.md`
* `04_kafka_streams.md`
* `05_spark_sql.md`
* `06_structured_streaming.md`

Après le découpage, la collection Chroma contient 18 chunks.

Le chargeur accepte également des fichiers PDF et TXT. Des documents supplémentaires peuvent être ajoutés dans `documents/pdfs/`.

## Architecture Agentic RAG

```text
START
  → route_question
      ├── retrieve_documents
      ├── compare_technologies
      └── calculate_storage
  → grade_documents
      ├── generate_answer
      ├── rewrite_query → retrieve_documents
      └── fallback_answer
  → verify_answer
  → finalize_answer
  → END
```

Le système utilise trois routes principales :

* `retrieve` : recherche d’informations dans le corpus
* `compare` : comparaison de plusieurs technologies
* `calculate` : calcul local d’une capacité de stockage

La visualisation complète est disponible dans :

```text
results/langgraph_workflow.svg
```

![Workflow LangGraph](results/langgraph_workflow.svg)

## Technologies utilisées

* Python 3.11
* LangGraph
* LangChain Core
* Groq
* ChromaDB
* Sentence Transformers
* Streamlit
* PyMuPDF
* Pytest
* Pandas

## Installation sous Windows

Cloner le projet :

```powershell
git clone https://github.com/marwaneqada/bigdata-agentic-rag.git
cd bigdata-agentic-rag
```

Créer l’environnement virtuel :

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Créer le fichier de configuration local :

```powershell
Copy-Item .env.example .env
notepad .env
```

Ajouter une clé Groq valide dans `.env` :

```env
GROQ_API_KEY=votre_cle_groq
GROQ_MODEL=votre_modele_groq
```

Le fichier `.env` est ignoré par Git et ne doit jamais être publié.

## Indexation des documents

```powershell
python ingest.py --reset
```

Résultat de la dernière indexation :

```text
Documents/pages chargés : 6
Chunks indexés : 18
Collection totale : 18
```

Le premier lancement peut télécharger le modèle d’embeddings depuis Hugging Face.

## Lancer l’application

```powershell
python -m streamlit run app.py
```

Puis ouvrir :

```text
http://localhost:8501
```

## Générer le graphe

```powershell
python generate_graph.py
```

Fichiers générés :

```text
results/langgraph_workflow.mmd
results/langgraph_workflow.svg
```

## Tests

```powershell
pytest -q
```

Dernier résultat :

```text
5 passed
```

## Évaluation finale

L’évaluation contient :

* 10 questions simples
* 10 questions complexes
* 20 questions au total

Commande :

```powershell
python -m evaluation.run_evaluation
```

Résultats obtenus :

| Métrique                        |        Résultat |
| ------------------------------- | --------------: |
| Questions évaluées              |              20 |
| Questions simples               |              10 |
| Questions complexes             |              10 |
| Temps de réponse moyen          | 32.426 secondes |
| Qualité moyenne des réponses    |         5.0 / 5 |
| Pertinence documentaire moyenne |         5.0 / 5 |
| Groundedness moyenne            |         5.0 / 5 |
| Réponses vides                  |               0 |
| Fallbacks                       |               0 |
| Erreurs                         |               0 |

Les scores de qualité, de pertinence et de groundedness sont attribués par un évaluateur LLM automatisé. Ils ne doivent donc pas être considérés comme une mesure humaine parfaitement objective.

Les résultats détaillés sont disponibles dans :

```text
results/evaluation_results.csv
results/evaluation_summary.json
```

## Exemples de routage

| Question                                                                   | Route       |
| -------------------------------------------------------------------------- | ----------- |
| What is Apache Airflow used for?                                           | `retrieve`  |
| Compare HDFS and MinIO.                                                    | `compare`   |
| Calculate storage for 500 GB, compression 0.6, replication 3 and 2 copies. | `calculate` |

Le calcul de stockage retourne :

```text
1800 GB
```

## Limites

* Le corpus fourni est limité à six documents de cours.
* Le temps de réponse moyen est d’environ 32 secondes.
* Une question peut nécessiter plusieurs appels au LLM : routage, évaluation des documents, génération et vérification.
* La mémoire conversationnelle est stockée en mémoire vive et disparaît après le redémarrage de l’application.
* Le fonctionnement du LLM nécessite une connexion Internet et une clé Groq valide.
* Les résultats d’évaluation sont produits automatiquement par un LLM.
* La base Chroma doit être reconstruite localement après le clonage du repository.

## Structure principale

```text
bigdata-agentic-rag/
├── app.py
├── ingest.py
├── generate_graph.py
├── documents/
│   └── course_notes/
├── evaluation/
├── results/
├── src/
├── tests/
├── report/
├── video/
├── requirements.txt
├── .env.example
└── README.md
```

## Livrables

* Repository GitHub
* Rapport PDF de 4 pages maximum
* Vidéo commentée de 2 minutes maximum
