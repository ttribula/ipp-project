class Instr:
    def __init__(self, opcode, arg1=None, arg2=None, arg3=None):
        self.opCode = opcode
        self.countArg = 0
        if arg1 is not None:
            self.arg1 = {'type': arg1.attrib['type'], 'value': arg1.text}
            self.countArg = 1
        if arg2 is not None:
            self.arg2 = {'type': arg2.attrib['type'], 'value': arg2.text}
            self.countArg = 2
        if arg3 is not None:
            self.arg3 = {'type': arg3.attrib['type'], 'value': arg3.text}
            self.countArg = 3


class InstrList:
    def __init__(self):
        self.instrDict = {}
        self.instrPos = 0
        self.counter = 1
        self.labelList = {}
        self.callStack = []

    def get_instr(self):
        if self.counter <= self.instrPos:
            self.counter += 1
            return self.instrDict[self.counter - 1]
        return None

    def get_counter(self):
        return self.counter - 1

    def get_label_list(self):
        return self.labelList;

    def insert_instr(self, instr):
        self.instrPos += 1
        self.instrDict[self.instrPos] = instr
        if instr.opCode == 'LABEL':
            if instr.arg1['value'] in self.labelList:
                # TODO: ERROR duplicita navesti
                exit(52)
            self.labelList[instr.arg1['value']] = self.instrPos

    def append_call_stack(self):
        self.callStack.append(self.get_counter() + 1)

    def pop_call_stack(self):
        if len(self.callStack) > 0:
            self.counter = self.callStack.pop()
        else:
            # TODO: ERROR hodnota neni v zasobniku
            exit(56)

    def set_counter_to_label(self, label):
        if label['value'] in self.labelList:
            self.counter = self.labelList[label['value']]
        else:
            # TODO: ERROR label neni v labellistu
            exit(52)
