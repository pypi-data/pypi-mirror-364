from openrouter_manager.adapter.variable import Variable
from jinja2 import Environment, DictLoader, select_autoescape


class Prompt():
    content: str
    variables: list = []
    env = None

    def __init__(self, content: str):
        loader = DictLoader({'prompt': content})
        self.env = Environment(loader=loader, autoescape=select_autoescape())
        self.clean()

    def set_variable(self, variable: Variable):
        self.variables.append(variable)

    def clean(self):
        self.variables.clear()

    def __str__(self):
        variables_dict = None
        variables_dict = {var.name: var.value for var in self.variables}
        template = self.env.get_template("prompt")
        return template.render(variables_dict)
