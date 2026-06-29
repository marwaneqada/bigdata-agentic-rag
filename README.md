# Big Data Agentic RAG — Marwane Qada

Assistant pédagogique Agentic RAG construit manuellement avec LangGraph.

## Ce qui est implémenté

- Base documentaire PDF, Markdown et TXT
- Découpage et vectorisation multilingue
- Chroma persistant
- Groq avec sortie structurée
- `StateGraph` manuel, sans `create_agent`
- Routage vers 3 outils
- Évaluation de pertinence documentaire
- Reformulation automatique
- Vérification de groundedness
- Mémoire par `thread_id`
- Interface Streamlit
- Visualisation Mermaid et SVG
- 10 questions simples + 10 complexes
- Export CSV et résumé JSON

## Sources du corpus de départ

Les notes présentes dans `documents/course_notes` synthétisent les supports de cours :

- Apache Airflow
- Hadoop HDFS
- MinIO
- Kafka Streams
- Spark SQL
- Spark Structured Streaming

Vous pouvez ajouter les PDF originaux dans `documents/pdfs`.

## Installation Windows

```powershell
python --version
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copier la configuration :

```powershell
Copy-Item .env.example .env
notepad .env
```

Ajouter la vraie clé Groq uniquement dans `.env`.

## Indexation

```powershell
python ingest.py --reset
```

Le premier lancement télécharge le modèle d'embeddings, ce qui peut prendre quelques
minutes.

## Lancer l'application

```powershell
streamlit run app.py
```

Puis ouvrir l'adresse affichée, généralement `http://localhost:8501`.

## Générer le graphe

```powershell
python generate_graph.py
```

Une visualisation SVG est déjà fournie dans `results/langgraph_workflow.svg`.

## Évaluation finale

```powershell
python -m evaluation.run_evaluation
```

Résultats :

```text
results/evaluation_results.csv
results/evaluation_summary.json
```

Ces fichiers doivent être générés sur votre ordinateur avant de finaliser le rapport.

## Tests

```powershell
pytest -q
```

## Publication GitHub

Depuis le dossier du projet :

```powershell
git init
git add .
git commit -m "Initial Agentic RAG project"
git branch -M main
git remote add origin URL_DE_VOTRE_REPOSITORY
git push -u origin main
```

Le fichier `.env` est ignoré par Git. Ne publiez jamais votre vraie clé Groq.

## Architecture du graphe

```text
START
  → route_question
      → retrieve_documents
      → compare_technologies
      → calculate_storage
  → grade_documents
      → generate_answer
      → rewrite_query → retrieve_documents
      → fallback_answer
  → verify_answer
  → finalize_answer
  → END
```

## Livrables finaux

- Lien GitHub
- Rapport PDF de 4 pages maximum
- Vidéo commentée de 2 minutes maximum
