from openrouter_manager.adapter.prompt import Prompt

__author__ = "Lenin Lozano"
__copyright__ = "Lenin Lozano"
__license__ = "MIT"

prompt_string = '''Eres un asistente de QA que genera casos de prueba a
    partir de la informacion de incidencias de Jira.
    A continuacion se proporciona la informacion de una incidencia:
    Incidencia actual:
    Título: {{ titulo }}
    Descripcion: {{ descripcion }}
    Genera casos de prueba en lenguaje Gherkin con palabras claves en español
    para la incidencia actual.'''


def test_generate_no_variables():
    """Main Function Tests"""

    prompt = Prompt(prompt_string)
    prompt.clean()
    assert prompt.__str__() == '''Eres un asistente de QA que genera casos de prueba a
    partir de la informacion de incidencias de Jira.
    A continuacion se proporciona la informacion de una incidencia:
    Incidencia actual:
    Título: 
    Descripcion: 
    Genera casos de prueba en lenguaje Gherkin con palabras claves en español
    para la incidencia actual.'''
