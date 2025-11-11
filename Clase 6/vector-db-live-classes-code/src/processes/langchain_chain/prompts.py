from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from src.processes import summaries

content_summaries = '\n'.join([f'{source}: {content}' for source, content in summaries.items()])

source_selection_prompt = PromptTemplate.from_template(
    f'''
    Eres un sistema experto encargado de seleccionar la mejor fuente conocimiento para responder una pregunta.
    Aca estan las posibilidades de conocimientos que posees.
    Si la pregunta no tiene nada que ver con el contenido, responde con la seleccion 'none'
    {content_summaries}

    '''+\
    '''
    Esta es la pregunta para tu seleccion de funete de conocimiento:
    {question}
    '''
)

none_selection_prompt = PromptTemplate.from_template(
    f'''
    Eres un sistema de chat que unicamente funciona para recordarle al usuario que cosas puede preguntarle una vez este haya hecho preguntas fuera de tu conocimiento.

    No respondas ningun tipo de pregunta ni a ningun comentario del usuario, solo recuerdale que solo puedes responder preguntas de lo siguiente:

    {content_summaries}

    '''+\
    '''
    Esta es la pregunta del usuario, aunque la recibas no la respondas:
    {question}
    '''
)


rag_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                "Eres un asistente experto que responde preguntas basándose en el contexto proporcionado.\n"
                "Contexto:\n{context}",
            ),
            HumanMessagePromptTemplate.from_template(
                "Pregunta: {question}"
            )
        ]
    )