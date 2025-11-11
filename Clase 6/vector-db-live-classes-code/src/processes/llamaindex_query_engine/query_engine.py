from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import PydanticSingleSelector, LLMSingleSelector
from llama_index.core.tools import QueryEngineTool
from src.processes import summaries
from src.services.vector_store import qdrant_llama_index
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
from services.llms import llm_llama_index

# Create query engine tools for each summary
query_engine_tools = []
for category, summary in summaries.items():
    query_engine = qdrant_llama_index.as_query_engine(llm=llm_llama_index,**{
            "filters": MetadataFilters(
                filters=[ExactMatchFilter(key="source", value=category)]
            ),"similarity_top_k": 3
        })
    tool = QueryEngineTool.from_defaults(
        query_engine=query_engine,
        description=summary,
    )
    query_engine_tools.append(tool)

# Create RouterQueryEngine
router_query_engine = RouterQueryEngine(
    selector=PydanticSingleSelector.from_defaults(llm=llm_llama_index),
    query_engine_tools=query_engine_tools,
    llm=llm_llama_index
)



