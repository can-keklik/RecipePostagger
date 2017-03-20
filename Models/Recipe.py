class Recipe:
    actions = []
    ingredients = []
    tools = []
    titleArray = []

    def __init__(self, title, category):
        self.title = title
        self.category = category

    def addAction(self, action):
        self.actions.append(action)

    def addIngeredient(self, ingredient):
        self.ingredients.append(ingredient)

    def addTools(self, tool):
        self.tools.append(tool)

    def addTitleArray(self, titlewords):
        self.titleArray.append(titlewords)
