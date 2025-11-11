import sys; sys.path.append('.')
from dotenv import load_dotenv
load_dotenv()
import asyncio
from src.services.llms import llm_langchain
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
import json 
import os
from tenacity import retry, wait_chain

prompt_template = """
Eres un asistente experto en la creación de resúmenes increibles y muy cortos de documentos. 
Tu objetivo es extraer la información clave pero general y presentarla de manera concisa y facil de entender. 
Piensa en que estos resumenes pueden servirte para entender el contenido de un documento sin leerlo.

Resume el siguiente documento:

{document_text}

Resumen:
"""

prompt = PromptTemplate(template=prompt_template, input_variables=['document_text'])

summarization_chain = prompt | llm_langchain

@retry(wait=wait_chain(5))
async def summarize_document(file_path):

    loader = PyPDFLoader(file_path)
    document = await asyncio.to_thread(loader.load)

    document_text = "\n\n".join(page.page_content for page in document)

    summary = await summarization_chain.ainvoke({"document_text": document_text})

    return summary.content


async def main():

    to_parse_documnents = os.listdir('data\\optimized_chunks')

    tasks = []
    for doc_name in to_parse_documnents:
        if doc_name.endswith(".pdf"):
            file_path = os.path.join('data\\optimized_chunks',doc_name)
            tasks.append(asyncio.create_task(summarize_document(file_path)))

    summaries = await asyncio.gather(*tasks)

    results = {}
    for i, doc_name in enumerate(to_parse_documnents):
        if doc_name.endswith(".pdf"):
            summary = summaries[i]
            if summary:
                results[doc_name.replace(".pdf","")] = summary

    with open('data\\summaries.json','w', encoding='utf-8') as f:
        json.dump(results,f,indent=2)


if __name__ == '__main__':
    asyncio.run(main())