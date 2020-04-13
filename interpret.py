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
    print(instruction.opCode)
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
            print('CHYBA: Vytvareni promenne v nedefinovanem ramci.', file=sys.stderr)
            exit(55)
        if name in stack_frame:
            print('CHYBA: Redefinice promenne v ramci.', file=sys.stderr)
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
            print('CHYBA: Vypis neinicializovane promenne.', file=sys.stderr)
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
            print('CHYBA: Operand instrukce {} je spatneho typu. Potreba int.'.format(instruction.opCode), file=sys.stderr)
            exit(53)
        try:
            frames.set_variable(instruction.arg1, 'string', chr(int(value)))
        except ValueError:
            # TODO: Nevalidni hodnota znaku
            exit(58)
    elif instruction.opCode == 'STRLEN':
        is_var, type, value = frames.get_value_of_arg(instruction.arg2)
        if type is not 'string':
            print('CHYBA: Operand instrukce {} je spatneho typu. Potreba string.'.format(instruction.opCode), file=sys.stderr)
            exit(53)
        frames.set_variable(instruction.arg1, 'int', len(value))
    elif instruction.opCode == 'TYPE':
        is_var, type, value = frames.get_value_of_arg(instruction.arg2)
        if type is None:
            type = ''
        frames.set_variable(instruction.arg1, 'string', type)
    elif instruction.opCode == 'NOT':
        is_var, type, value = frames.get_value_of_arg(instruction.arg2)
        if type is not 'bool':
            print('CHYBA: Operand instrukce {} je spatneho typu. Potreba bool.'.format(instruction.opCode),
                  file=sys.stderr)
            exit(53)
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
    elif instruction.opCode in ['ADD', 'SUB', 'MUL', 'IDIV']:
        is_var, type, name = frames.get_value_of_arg(instruction.arg2)
        is_var2, type2, name2 = frames.get_value_of_arg(instruction.arg3)
        if type != 'int' or type2 != 'int':
            print('CHYBA: Operandy instrukce {} ruzneho typu.'.format(instruction.opCode), file=sys.stderr)
            exit(53)
        if instruction.opCode == 'ADD':
            frames.set_variable(instruction.arg1, type, str(int(name) + int(name2)))
        elif instruction.opCode == 'SUB':
            frames.set_variable(instruction.arg1, type, str(int(name) - int(name2)))
        elif instruction.opCode == 'MUL':
            frames.set_variable(instruction.arg1, type, str(int(name) * int(name2)))
        else:
            if name2 == '0':
                print('CHYBA: Deleni nulou.', file=sys.stderr)
                exit(57)
            frames.set_variable(instruction.arg1, type, str(int(name) // int(name2)))
    elif instruction.opCode in ['LT', 'GT']:
        is_var, type, name = frames.get_value_of_arg(instruction.arg2)
        is_var2, type2, name2 = frames.get_value_of_arg(instruction.arg3)
        if type != type2:
            print('CHYBA: Operandy instrukce {} ruzneho typu.'.format(instruction.opCode), file=sys.stderr)
            exit(53)
        if instruction.opCode == 'LT':
            if type == 'int':
                if int(name) < int(name2):
                    frames.set_variable(instruction.arg1, 'bool', 'true')
                else:
                    frames.set_variable(instruction.arg1, 'bool', 'false')
            elif type == 'bool':
                if name == 'false' and name2 == 'true':
                    frames.set_variable(instruction.arg1, 'bool', 'true')
                else:
                    frames.set_variable(instruction.arg1, 'bool', 'false')
            else:
                if name < name2:
                    frames.set_variable(instruction.arg1, 'bool', 'true')
                else:
                    frames.set_variable(instruction.arg1, 'bool', 'false')
        else:
            if type == 'int':
                if int(name) > int(name2):
                    frames.set_variable(instruction.arg1, 'bool', 'true')
                else:
                    frames.set_variable(instruction.arg1, 'bool', 'false')
            elif type == 'bool':
                if name == 'true' and name2 == 'false':
                    frames.set_variable(instruction.arg1, 'bool', 'true')
                else:
                    frames.set_variable(instruction.arg1, 'bool', 'false')
            else:
                if name > name2:
                    frames.set_variable(instruction.arg1, 'bool', 'true')
                else:
                    frames.set_variable(instruction.arg1, 'bool', 'false')
    elif instruction.opCode == 'EQ':
        is_var, type, name = frames.get_value_of_arg(instruction.arg2)
        is_var2, type2, name2 = frames.get_value_of_arg(instruction.arg3)
        if type == 'nil':
            if name == 'nil' and name2 == 'nil':
                frames.set_variable(instruction.arg1, 'bool', 'true')
            else:
                frames.set_variable(instruction.arg1, 'bool', 'false')
        elif type == type2:
            if type == 'int':
                if int(name) == int(name2):
                    frames.set_variable(instruction.arg1, 'bool', 'true')
                else:
                    frames.set_variable(instruction.arg1, 'bool', 'false')
            else:
                if name == name2:
                    frames.set_variable(instruction.arg1, 'bool', 'true')
                else:
                    frames.set_variable(instruction.arg1, 'bool', 'false')
        else:
            print('CHYBA: Operandy instrukce {} ruzneho typu.'.format(instruction.opCode), file=sys.stderr)
            exit(53)
    elif instruction.opCode in ['AND', 'OR']:
        is_var, type, name = frames.get_value_of_arg(instruction.arg2)
        is_var2, type2, name2 = frames.get_value_of_arg(instruction.arg3)
        if type != 'bool' or type2 != 'bool':
            print('CHYBA: Operandy instrukce {} ruzneho typu.'.format(instruction.opCode), file=sys.stderr)
            exit(53)
        if instruction.opCode == 'AND':
            if name == 'true' and name2 == 'true':
                frames.set_variable(instruction.arg1, 'bool', 'true')
            else:
                frames.set_variable(instruction.arg1, 'bool', 'false')
        elif instruction.opCode == 'OR':
            if name == 'true' or name2 == 'true':
                frames.set_variable(instruction.arg1, 'bool', 'true')
            else:
                frames.set_variable(instruction.arg1, 'bool', 'false')
    elif instruction.opCode == 'STRI2INT':
        is_var, type, name = frames.get_value_of_arg(instruction.arg2)
        is_var2, type2, name2 = frames.get_value_of_arg(instruction.arg3)
        if type != 'string' or type2 != 'int':
            print('CHYBA: Operandy instrukce {} ruzneho typu.'.format(instruction.opCode), file=sys.stderr)
            exit(53)
        index = int(name2)
        if index < 0 or index > len(name)-1:
            print('CHYBA: Indexace mimo dany retezec.', file=sys.stderr)
            exit(58)
        frames.set_variable(instruction.arg1, 'int', ord(name[index]))
    elif instruction.opCode == 'CONCAT':
        is_var, type, name = frames.get_value_of_arg(instruction.arg2)
        is_var2, type2, name2 = frames.get_value_of_arg(instruction.arg3)
        if type != 'string' or type2 != 'string':
            print('CHYBA: Operandy instrukce {} ruzneho typu.'.format(instruction.opCode), file=sys.stderr)
            exit(53)
        frames.set_variable(instruction.arg1, 'string', name + name2)
    elif instruction.opCode == 'GETCHAR':
        is_var, type, name = frames.get_value_of_arg(instruction.arg2)
        is_var2, type2, name2 = frames.get_value_of_arg(instruction.arg3)
        if type != 'string' or type2 != 'int':
            print('CHYBA: Operandy instrukce {} ruzneho typu.'.format(instruction.opCode), file=sys.stderr)
            exit(53)
        index = int(name2)
        if index < 0 or index > len(name) - 1:
            print('CHYBA: Indexace mimo dany retezec.', file=sys.stderr)
            exit(58)
        frames.set_variable(instruction.arg1, 'int', name[index])
    elif instruction.opCode == 'SETCHAR':
        is_var, type, name = frames.get_value_of_arg(instruction.arg1)
        is_var2, type2, name2 = frames.get_value_of_arg(instruction.arg2)
        is_var3, type3, name3 = frames.get_value_of_arg(instruction.arg3)
        if type != 'string' or type2 != 'int' or type3 != 'string':
            print('CHYBA: Operandy instrukce {} ruzneho typu.'.format(instruction.opCode), file=sys.stderr)
            exit(53)
        index = int(name2)
        if index < 0 or index > len(name) - 1:
            print('CHYBA: Indexace mimo dany retezec.', file=sys.stderr)
            exit(58)
        if not name3:
            print('CHYBA: Retezec pro nahrazeni charu je prazdny.', file=sys.stderr)
            exit(58)
        name = list(name)
        name[index] = name3[0]
        name = ''.join(name)
        frames.set_variable(instruction.arg1, type, name)
    elif instruction.opCode in ['JUMPIFEQ', 'JUMPIFNEQ']:
        is_var, type, name = frames.get_value_of_arg(instruction.arg2)
        is_var2, type2, name2 = frames.get_value_of_arg(instruction.arg3)
        if (type != type2) or (type != 'nil' or type2 != 'nil'):
            print('CHYBA: Operandy instrukce {} ruzneho typu.'.format(instruction.opCode), file=sys.stderr)
            exit(53)
        if instruction.opCode == 'JUMPIFEQ':
            if name == name2:
                instrList.set_counter_to_label(instruction.arg1)
            else:
                pass
        elif instruction.opCode == 'JUMPIFNEQ':
            if name != name2:
                instrList.set_counter_to_label(instruction.arg1)
            else:
                pass

    instruction = instrList.get_instr()
    sleep(1)
