
class DataStack:
    def __init__(self):
        self.dStack = []

    def get_d_stack(self):
        return self.dStack

    def d_stack_push(self, type, value):
        self.dStack.append((type, value))

    def d_stack_push(self):
        if len(self.dStack) < 1:
            # TODO: ERROR chybejici hodnota na datovem zasobniku
            exit(56)
        return self.dStack.pop()