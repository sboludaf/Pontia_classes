from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableBranch
from qdrant_client.http import models

from src.services.llms import llm_langchain
from src.services.vector_store import qdrant_langchain
from src.processes.langchain_chain.prompts import source_selection_prompt, rag_prompt, none_selection_prompt
from src.processes.langchain_chain.structures import SourceModel

classifier_chain = source_selection_prompt | llm_langchain.with_structured_output(SourceModel)

answer_generation_chain = rag_prompt | llm_langchain | StrOutputParser()

def format_docs(input_dict) -> str:
        docs = input_dict['source_context']
        """Formatea los documentos recuperados en una sola cadena."""
        return "\n\n".join(doc.page_content for doc in docs)



def get_context(input_dict):
    question = input_dict['question']
    source = input_dict['source'].selection
    source_context = qdrant_langchain.similarity_search(
    question, k=4,
    filter=models.Filter(
                        should=[
                            models.FieldCondition(
                                key="metadata.source",
                                match=models.MatchValue(value=source),
                            )
                        ]
                    )
                )
    return source_context

def check_if_source_exists(input_dict):
    if input_dict["source"].selection == 'none':
        return False
    return True

rag_with_source_chain = (
    RunnablePassthrough.assign(source_context=RunnableLambda(get_context))
    .assign(context=RunnableLambda(format_docs))
    .assign(answer=answer_generation_chain)
)

no_source_found_chain =  RunnablePassthrough.assign(
     answer= none_selection_prompt | llm_langchain | StrOutputParser()
     )

rag_chain = (
    RunnablePassthrough.assign(
        source=(itemgetter("question") | classifier_chain)
    )
    | RunnableBranch(
        (check_if_source_exists, rag_with_source_chain),
        no_source_found_chain,
    )
).with_types(input_type=dict, output_type=dict)
