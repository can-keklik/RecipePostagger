class Tool:
    actions = []

    def __init__(self, name):
        self.name = name

    def addAction(self, action):
        self.actions.append(action)
