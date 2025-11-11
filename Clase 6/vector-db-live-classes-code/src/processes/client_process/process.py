from src.processes import summaries
from src.services.llms import llm_google_genai 
from src.services.embeddings import  embeddings_google_genai
from src.services.vector_store import qdrant_client, async_qdrant_client
from qdrant_client import models
from google.genai.types import Part, UserContent, ModelContent
from typing import Literal
from pydantic import BaseModel, Field

content_summaries = '\n'.join([f'{source}: {content}' for source, content in summaries.items()])
categories_description = "\n".join(
    [f"- {key}: {value}" for key, value in summaries.items()]
)

selection_prompt = (f'''
    Eres un sistema experto encargado de seleccionar la mejor fuente conocimiento para responder una pregunta.
    Aca estan las posibilidades de conocimientos que posees.
    Si la pregunta no tiene nada que ver con el contenido, responde con la seleccion 'none'
    {content_summaries}

    '''+\
    '''
    Esta es la pregunta para tu seleccion de funete de conocimiento:
    {question}
    ''')

none_selection_prompt = (f'''
    Eres un sistema de chat que unicamente funciona para recordarle al usuario que cosas puede preguntarle una vez este haya hecho preguntas fuera de tu conocimiento.

    No respondas ningun tipo de pregunta ni a ningun comentario del usuario, solo recuerdale que solo puedes responder preguntas de lo siguiente:

    {content_summaries}

    '''+\
    '''
    Esta es la pregunta del usuario, aunque la recibas no la respondas:
    {question}
    ''')


possible_categories = list(summaries.keys())

class SourceModel(BaseModel):
    selection: Literal[tuple(possible_categories)] = Field( # type: ignore
            ...,
            description=f"Categoriza la pregunta del usuario en una de las siguientes categorías:\n{categories_description}",
            
        )
    reason: str = Field(
            ...,
            description=f"Razones por las que eliges la seleccion",
        )


def get_rag_prompt(context, question):
    return [

                ModelContent(
                    parts=Part(
                        text="Eres un asistente experto que responde preguntas basándose en el contexto proporcionado.\n"
                            f"Contexto:\n{context}")),
                UserContent(
                    parts=Part(
                        text= f"Pregunta: {question}"
                                    ))
        
            ]


async def get_answer(query):
    selection =  await llm_google_genai.aio.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=selection_prompt.format(question=query),
        config={
            "response_mime_type": "application/json",
            "response_schema": SourceModel,
        },
    )
    selection = selection.parsed 

    embeddings = await embeddings_google_genai.aio.models.embed_content(
        model="gemini-embedding-001",
        contents=query)

    found_docs = await async_qdrant_client.query_points(
        collection_name='qdrantclient_index',
        query= embeddings.embeddings[0].values,
        with_payload=True,
        limit=5,
        query_filter=models.Filter(must=[
            models.FieldCondition(
                key="source",
                match=models.MatchValue(value=selection.selection),
            )
            ]
        )
    )

    context = '\n'.join([doc.payload['content'] for doc in found_docs.points])

    rag_prompt = get_rag_prompt(context,query)

    answer = await llm_google_genai.aio.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=rag_prompt
    )
    return {
        'answer': answer.text,
        'selection': selection.selection,
        'reason': selection.reason,
        'context': found_docs
    }


