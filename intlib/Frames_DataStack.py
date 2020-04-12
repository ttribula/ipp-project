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

class Frames:
    def __init__(self):
        self.globalFrame = {}
        self.frameStack = []
        self.tmpFrame = None

    def create_tmp_frame(self):
        self.tmpFrame = {}

    def get_tmp_frame(self):
        if self.tmpFrame is None:
            # TODO: nedefinovany ramec
            exit(55)
        return self.tmpFrame

    def push_tmp_frame(self):
        if self.tmpFrame is None:
            # TODO: nedefinovany ramec
            exit(55)
        self.frameStack.append(self.tmpFrame)

    def pop_to_tmp_frame(self):
        if len(self.frameStack) < 1:
            # TODO: ERROR pop z prazdneho frame stacku
            exit(55)
        self.tmpFrame = self.frameStack.pop()

    def get_frame(self, frame):
        if frame is 'GF':
            return self.globalFrame
        elif frame is 'LF':
            if len(self.frameStack) < 1:
                return None
            return self.frameStack[len(self.frameStack) - 1]
        elif frame is 'TF':
            return self.tmpFrame
