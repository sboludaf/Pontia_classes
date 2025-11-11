import json 

with open("data\\summaries.json", "r",encoding='utf-8') as f: # windows stuff
    summaries = json.load(f)

summaries['none'] = 'Este resumen se utiliza para conversaciones que no tengan que ver con el resto de las tematicas, sean saludos, deseos o cualquier pregunta fuera del contexto del estado de empleabilidad de los jovenes'

__all__ = ['summaries']