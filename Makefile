install:
	python -m pip install -r requirements.txt

ingest:
	python ingest.py --reset

app:
	streamlit run app.py

graph:
	python generate_graph.py

evaluate:
	python -m evaluation.run_evaluation

test:
	pytest -q
