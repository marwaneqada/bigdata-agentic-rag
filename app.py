from __future__ import annotations

import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from src.config import get_settings
from src.graph import get_graph, initial_state
from src.vector_store import get_vector_store


st.set_page_config(
    page_title="Big Data Agentic RAG",
    page_icon="🧠",
    layout="wide",
)

settings = get_settings()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "display_messages" not in st.session_state:
    st.session_state.display_messages = [
        {
            "role": "assistant",
            "content": (
                "Bonjour. Je suis un assistant Agentic RAG spécialisé en Big Data et Cloud. "
                "Interrogez-moi sur Airflow, HDFS, MinIO, Kafka Streams, Spark SQL "
                "ou Structured Streaming."
            ),
        }
    ]

if "last_result" not in st.session_state:
    st.session_state.last_result = None


@st.cache_resource
def load_graph():
    return get_graph()


@st.cache_resource
def load_store():
    return get_vector_store()


graph = load_graph()
store = load_store()

with st.sidebar:
    st.title("Configuration")
    st.metric("Chunks indexés", store.count)
    st.caption(f"Modèle : {settings.groq_model}")
    st.caption(f"Embeddings : {settings.embedding_model}")
    st.caption(f"Thread : {st.session_state.thread_id[:8]}…")

    if not settings.has_groq_key:
        st.error("Ajoutez GROQ_API_KEY dans le fichier .env.")

    if store.count == 0:
        st.warning("Exécutez `python ingest.py --reset` avant de poser des questions.")

    if st.button("Nouvelle conversation", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.display_messages = [
            {
                "role": "assistant",
                "content": "Nouvelle conversation créée. Quelle est votre question ?",
            }
        ]
        st.session_state.last_result = None
        st.rerun()

    st.divider()
    st.markdown(
        """
**Routes disponibles**
- Recherche documentaire
- Comparaison de technologies
- Calcul de stockage
- Reformulation automatique
- Vérification de la réponse
"""
    )

st.title("🧠 Assistant Agentic RAG — Big Data & Cloud")
st.caption(
    "LangGraph manuel, outils, mémoire de conversation, recherche vectorielle et vérification."
)

for message in st.session_state.display_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Posez une question sur les supports de cours…")

if question:
    st.session_state.display_messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("L'agent analyse la question et choisit ses outils…"):
            try:
                result = graph.invoke(
                    initial_state(question),
                    config={
                        "configurable": {
                            "thread_id": st.session_state.thread_id,
                        }
                    },
                )
                answer = result.get("answer", "Aucune réponse générée.")
                st.markdown(answer)
                st.session_state.display_messages.append(
                    {"role": "assistant", "content": answer}
                )
                st.session_state.last_result = result
            except Exception as exc:
                error = f"Erreur : {exc}"
                st.error(error)
                st.session_state.display_messages.append(
                    {"role": "assistant", "content": error}
                )

result = st.session_state.last_result

if result:
    st.divider()
    left, middle, right = st.columns(3)

    left.metric("Route", result.get("route", "-"))
    middle.metric(
        "Pertinence",
        f"{result.get('relevance_score', 0.0) * 100:.0f} %",
    )
    right.metric(
        "Temps",
        f"{result.get('response_time', 0.0):.2f} s",
    )

    with st.expander("Détails de l'exécution"):
        st.write("**Raison du routage :**", result.get("route_reason", "-"))
        st.write("**Statut :**", result.get("status", "-"))
        st.write(
            "**Vérification :**",
            result.get("verification_reason", "-"),
        )
        st.write(
            "**Score de vérification :**",
            f"{result.get('verification_score', 0.0) * 100:.0f} %",
        )
        st.write("**Reformulations :**", result.get("rewrite_count", 0))

    with st.expander("Sources récupérées"):
        sources = result.get("sources", [])
        if sources:
            for source in sources:
                st.write(f"- {source}")
        else:
            st.info("Aucune source documentaire.")
