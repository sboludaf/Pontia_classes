from pypdf import PdfReader, PdfWriter
from pypdf.generic import Destination
from typing import Dict, List, Any
import os

reader = PdfReader('data\\informe_mercado_de_trabajo_jovenes.pdf')

chunk_level_info = [
'Presentación',
'Índices',
'Objetivos',
'Metodología',
'Fuentes',
'Indicadores de los colectivos de atención prioritaria para el empleo. Comparativa',
'Los jóvenes menores de 30 años en el mercado laboral',
'1. Población y actividad laboral',
'2. El empleo',
'3. El desempleo',
'4. Ocupaciones',
'Glosario de términos'
]

bookmarks = reader.outline

all_bookmark_info: List[Dict[str,Any]] = []

for item in bookmarks:
    if isinstance(item, Destination):
        title = item.title 
        page_number = reader.get_destination_page_number(item)
        all_bookmark_info.append({"title": title, "start_page": page_number })
    elif isinstance(item, list):
        parent_bookmark = item[0]
        title = parent_bookmark.title
        page_number = reader.get_destination_page_number(parent_bookmark)
        all_bookmark_info.append({"title": title, "start_page": page_number })

all_filtered_bookmarks_info: List[Dict[str,Any]] = []
for item in all_bookmark_info:
    if item['title'] in chunk_level_info:
        all_filtered_bookmarks_info.append(item)


final_pages_division_info: List[Dict[str, Any]] = []
final_page: int = len(reader.pages)

for item, next_item in zip(all_filtered_bookmarks_info, all_filtered_bookmarks_info[1:]+[None]):
    if next_item:
        final_pages_division_info.append({
            **item,
            'final_page': next_item['start_page'] -1
        })
    else:
        final_pages_division_info.append({
            **item,
            'final_page': final_page -1
        })

for section in final_pages_division_info:
    writer = PdfWriter()
    name = section['title']
    start_page = section['start_page']
    end_page = section['final_page']

    if end_page > start_page:
        for page_num in range(start_page,end_page):
            writer.add_page(reader.pages[page_num])
    elif end_page == start_page:
        writer.add_page(reader.pages[start_page])

    output_filename = f"{name}.pdf"
    output_path = os.path.join('data\\optimized_chunks',output_filename)

    with open(output_path, 'wb') as output_file:
        writer.write(output_file)