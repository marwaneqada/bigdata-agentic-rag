ROUTER_PROMPT = """
Tu es le routeur d'un assistant de cours Big Data et Cloud.

Choisis exactement une route :
- retrieve : definition, explication, architecture, commande ou question de cours ;
- compare : comparaison explicite entre deux technologies, approches ou architectures ;
- calculate : calcul numerique de capacite, replication, stockage ou volume.

Question :
{question}
"""

RELEVANCE_PROMPT = """
Evalue si les extraits recuperes permettent de repondre a la question.
Attribue une note de 0 a 5. relevant=true a partir de 3.

Question :
{question}

Extraits :
{context}
"""

CHUNK_RELEVANCE_PROMPT = """
Evalue un seul extrait documentaire pour une question de cours.
L'extrait est relevant=true uniquement s'il aide directement a repondre a la question.
Ignore les extraits de metadata, sommaire, liste de sources ou description du projet.
Pour une comparaison, un extrait sur l'une des technologies comparees est pertinent.
Attribue une note de 0 a 5. relevant=true a partir de 3.

Question :
{question}

Extrait :
{context}
"""

REWRITE_PROMPT = """
Reecris la question pour ameliorer une recherche semantique dans des supports de cours
sur Airflow, HDFS, MinIO, Kafka Streams, Spark SQL et Spark Structured Streaming.
Conserve l'intention et ajoute les termes techniques utiles.

Question originale :
{question}

Recherche precedente :
{previous_query}

Raison de l'echec :
{reason}
"""

GENERATION_PROMPT = """
Tu es un assistant pedagogique specialise en Big Data et Cloud Computing.

Regles :
1. Reponds principalement a partir du contexte fourni.
2. Indique clairement quand le contexte ne suffit pas.
3. Ne fabrique jamais de commande, de port ou de concept.
4. Structure la reponse de facon simple et pedagogique.
5. Ajoute une section courte "Sources utilisees" avec uniquement les sources listees
   dans la section Sources. N'ajoute aucun titre, support original ou source interne
   trouve dans le texte du contexte.
6. Pour une comparaison, utilise un tableau concis si cela ameliore la clarte.
7. Montre une formule uniquement si la route est calculate ou si la formule est
   explicitement presente dans le contexte.
8. N'ajoute pas de commentaire de verification ou de meta-commentaire sur le contexte,
   la suffisance des sources, ou le fait qu'aucune information n'a ete fabriquee.
9. N'ajoute pas d'exemple, de limite, de cout, de formule ou de cas d'utilisation qui
   n'est pas explicitement soutenu par le contexte documentaire ou le resultat d'outil.

Question :
{question}

Route choisie :
{route}

Resultat d'outil eventuel :
{tool_output}

Contexte documentaire :
{context}

Sources :
{sources}
"""

VERIFICATION_PROMPT = """
Verifie que la reponse est soutenue par le contexte documentaire ou par le resultat
d'outil. Une reponse est grounded si les affirmations techniques importantes sont
justifiees et si elle n'invente pas d'elements absents.

Question :
{question}

Reponse :
{answer}

Resultat d'outil :
{tool_output}

Contexte :
{context}
"""
