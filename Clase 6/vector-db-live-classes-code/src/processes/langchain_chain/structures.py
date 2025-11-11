
from typing import Literal
from pydantic import BaseModel, Field
from src.processes import summaries

# Crear una descripción para el modelo Pydantic
categories_description = "\n".join(
    [f"- {key}: {value}" for key, value in summaries.items()]
)
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

