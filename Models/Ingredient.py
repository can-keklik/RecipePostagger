class Ingredient:
    actions = []
    attr = []

    def __init__(self, name):
        self.name = name

    def addAction(self, action):
        self.actions.append(action)

    def addAttr(self, attr):
        self.attr.append(attr)
