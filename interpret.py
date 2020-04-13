from intlib.ArgCheck import ArgCheck
from intlib.Frames_DataStack import Frames
from intlib.Frames_DataStack import DataStack
from intlib.Instructions import InstrList
from intlib.XmlParser import XmlParser
import sys


from time import sleep

argCheck = ArgCheck()
argCheck.check()
frames = Frames()
dataStack = DataStack()
instrList = InstrList()
xmlParser = XmlParser(argCheck.get_source(), instrList)
xmlParser.parse()

instruction = instrList.get_instr()
while instruction is not None:
    if instruction.opCode == 'CREATEFRAME':
        frames.create_tmp_frame()
    elif instruction.opCode == 'PUSHFRAME':
        frames.push_tmp_frame()
    elif instruction.opCode == 'POPFRAME':
        frames.pop_to_tmp_frame()
    elif instruction.opCode == 'RETURN':
        instrList.pop_call_stack()
    elif instruction.opCode == 'BREAK':
        print('Pozice v kodu:   {}'.format(instrList.get_counter()), file=sys.stderr)
        print('Datovy zásobnik: {}'.format(dataStack.get_d_stack()), file=sys.stderr)
        print('Zasobnik ramcu:  {}'.format(frames.get_frame_stack()), file=sys.stderr)
        print('Globalni ramec:  {}'.format(frames.get_frame('GF')), file=sys.stderr)
        print('Lokalni ramec:   {}'.format(frames.get_frame('LF')), file=sys.stderr)
        print('Docasny ramec:   {}'.format(frames.get_frame('TF')), file=sys.stderr)
    elif instruction.opCode == 'DEFVAR':
        frame, name = instruction.arg1['value'].split('@', 1)
        stack_frame = frames.get_frame(frame)
        if stack_frame is None:
            # TODO: ERROR vytvoreni promenne na nedefinovanem ramci
            exit(55)
        if name in stack_frame:
            # TODO: ERROR promenna v ramci uz existuje(redefinice)
            exit(58)
        stack_frame[name] = {'type': None, 'value': None}
    elif instruction.opCode == 'POPS':
        type, value = dataStack.d_stack_pop()
        frames.set_variable(instruction.arg1, type, value)
    elif instruction.opCode == 'CALL':
        instrList.append_call_stack()
        instrList.set_counter_to_label(instruction.arg1)
    elif instruction.opCode == 'LABEL':
        # SLOVNIK JIZ NAPLNENY
        continue
    elif instruction.opCode == 'JUMP':
        instrList.set_counter_to_label()
    elif instruction.opCode == 'PUSHS':
        is_var, type, value = frames.get_value_of_arg(instruction.arg1)
        dataStack.d_stack_push(type, value)
    elif instruction.opCode == 'WRITE':
        is_var, type, value = frames.get_value_of_arg(instruction.arg1)
        if value is None:
            # TODO: ERROR vypis neincializovane promenne
            exit(56)
        print(value)
    elif instruction.opCode == 'DPRINT':
        print(value, file=sys.stderr)
    elif instruction.opCode == 'MOVE':
        is_var, type, value = frames.get_value_of_arg(instruction.arg2)
        frames.set_variable(instruction.arg1, type, value)
    elif instruction.opCode == 'INT2CHAR':
        is_var, type, value = frames.get_value_of_arg(instruction.arg2)
        if type is not 'int':
            if is_var:
                # TODO: ERROR bad type of var
                exit(53)
            # TODO: ERROR bad type of operand
            exit(52)
        try:
            frames.set_variable(instruction.arg1, 'string', chr(int(value)))
        except ValueError:
            # TODO: Nevalidni hodnota znaku
            exit(58)
    elif instruction.opCode == 'STRLEN':
        is_var, type, value = frames.get_value_of_arg(instruction.arg2)
        if type is not 'string':
            if is_var:
                # TODO: ERROR bad type of var
                exit(53)
            # TODO: ERROR bad type of operand
            exit(52)
        frames.set_variable(instruction.arg1, 'int', len(value))
    elif instruction.opCode == 'TYPE':
        is_var, type, value = frames.get_value_of_arg(instruction.arg2)
        if type is None:
            type = ''
        frames.set_variable(instruction.arg1, 'string', type)
    elif instruction.opCode == 'NOT':
        is_var, type, value = frames.get_value_of_arg(instruction.arg2)
        if type is not 'bool':
            if is_var:
                # TODO: ERROR bad type of var
                exit(53)
            # TODO: ERROR bad type of operand
            exit(52)
        if value == 'true':
            frames.set_variable(instruction.arg1, 'bool', 'false')
        elif value == 'false':
            frames.set_variable(instruction.arg1, 'bool', 'true')
    elif instruction.opCode == 'READ':
        is_var, type, value = frames.get_value_of_arg(instruction.arg2)
        if argCheck.get_input():
            input = argCheck.get_input()
        else:
            input = input()
        if value == 'int':
            try:
                input = int(input)
            except Exception:
                input = 0
            frames.set_variable(instruction.arg1, 'int', input)
        elif value == 'bool':
            if input.lower() == 'true':
                input = 'true'
            else:
                input = 'false'
            frames.set_variable(instruction.arg1, 'bool', input)
        else:
            try:
                input = str(input)
            except Exception:
                input = ''
            frames.set_variable(instruction.arg1, 'string', input)
    instruction = instrList.get_instr()
    sleep(1)
