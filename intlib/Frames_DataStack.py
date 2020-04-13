class DataStack:
    def __init__(self):
        self.dStack = []

    def get_d_stack(self):
        return self.dStack

    def d_stack_push(self, type, value):
        self.dStack.append((type, value))

    def d_stack_pop(self):
        if len(self.dStack) < 1:
            # TODO: ERROR chybejici hodnota na datovem zasobniku
            exit(56)
        return self.dStack.pop()

class Frames:
    def __init__(self):
        self.globalFrame = {}
        self.frameStack = []
        self.tmpFrame = None

    def get_frame_stack(self):
        return self.frameStack

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
        if frame == 'GF':
            return self.globalFrame
        elif frame == 'LF':
            if len(self.frameStack) < 1:
                return None
            return self.frameStack[len(self.frameStack) - 1]
        elif frame == 'TF':
            return self.tmpFrame

    def get_value_of_arg(self, arg):
        if arg['type'] == 'var':
            frame, name = arg['value'].split('@', 1)
            stack_frame = self.get_frame(frame)
            if stack_frame is None:
                # TODO: ERROR cteni promenne z nedefinovaneho ramce
                exit(55)
            if name not in stack_frame:
                # TODO: ERROR promenna neni v ramci
                exit(54)
            # fce vraci 1, kdyz je argument promenna, typ a hodnotu
            return 1, stack_frame['type'], stack_frame['value']
        if arg['type'] in ['int', 'bool', 'nil', 'string', 'type']:
            return 0, arg['type'], arg['value']

    def set_variable(self, arg, type, value):
        frame, name = arg['value'].split('@', 1)
        stack_frame = self.get_frame(frame)
        if stack_frame is None:
            # TODO: ERROR cteni promenne z nedefinovaneho ramce
            exit(55)
        if name not in stack_frame:
            # TODO: ERROR promenna neni v ramci
            exit(54)
        stack_frame['type'] = type
        stack_frame['value'] = value
