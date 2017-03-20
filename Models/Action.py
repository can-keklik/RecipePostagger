class Action:
    tools = []
    ingredients = []

    def __init__(self, name):
        self.name = name

    def addTools(self, tool):
        self.tools.append(tool)

    def addIngredient(self, ingredient):
        self.ingredients.append(ingredient)


