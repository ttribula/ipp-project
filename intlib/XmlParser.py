import xml.etree.ElementTree as ET
import re
import sys

from intlib.Instructions import Instr


class XmlParser:
    def __init__(self, source, instr_list):
        self.source = source
        self.instrList = instr_list

    def parse(self):
        # -----------XML Syntax---------------
        try:
            tree = ET.parse(self.source)
            self.root = tree.getroot()
        except FileNotFoundError:
            print('Soubor {} nelze otevrit.'.format(self.source), file=sys.stderr)
            exit(11)
        except Exception:
            print('Spatne formatovany XML soubor.', file=sys.stderr)
            exit(31)

        if self.root.tag != 'program':
            print('Korenovy element nema <program>.', file=sys.stderr)
            exit(31)

        for attr in self.root.attrib:
            if attr not in ['language', 'name', 'description']:
                print('Nepovolene atributy korenoveho elementu <program>.', file=sys.stderr)
                exit(31)

        if 'language' not in self.root.attrib:
            print('Neni definovan jazyk v korenovem elementu <program>.', file=sys.stderr)
            exit(31)
        if str(self.root.attrib['language']).lower() != 'ippcode20':
            print('Jazyk definovany v korenovem elementu <program> neni ippcode20.', file=sys.stderr)
            exit(31)

        instr_order = []
        for instr in self.root:
            if instr.tag != 'instruction':
                # TODO: ERROR spatny nazev elementu instr
                exit(31)
            if 'opcode' not in instr.attrib:
                # TODO: ERROR opcode neni v elementu instr
                exit(31)
            if 'order' not in instr.attrib:
                # TODO: ERROR order neni v elementu instr
                exit(31)
            instr_order.append(instr.attrib['order'])

            arg_count = 0
            for arg in instr:
                arg_count += 1
                if arg.tag != 'arg' + str(arg_count):
                    # TODO: ERROR arg bad name
                    exit(31)
                if 'type' not in arg.attrib:
                    # TODO: ERROR type neni
                    exit(31)
                if arg.attrib['type'] not in ['int', 'bool', 'string', 'nil', 'label', 'type', 'var']:
                    # TODO: ERROR bad type
                    exit(31)
            for i in instr_order:
                if int(i) <= 0:
                    # TODO: ERROR negativni order num
                    exit(31)
            if len(set(instr_order)) is not len(instr_order):
                # TODO: ERROR duplicitni order number
                exit(31)

        # -----------Kontrola instrukci---------------
        for instr in self.root:
            if instr.attrib['opcode'] in ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK']:
                if len(list(instr)) is not 0:
                    # TODO: ERROR nespravny pocet argumentu instrukce
                    exit(31)
                self.instrList.insert_instr(Instr(instr.attrib['opcode']))
            elif instr.attrib['opcode'] in ['DEFVAR', 'POPS']:
                if len(list(instr)) is not 1:
                    # TODO: ERROR nespravny pocet argumentu instrukce
                    exit(31)
                self.__check_variable(instr[0])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0]))
            elif instr.attrib['opcode'] in ['CALL', 'LABEL', 'JUMP']:
                if len(list(instr)) is not 1:
                    # TODO: ERROR nespravny pocet argumentu instrukce
                    exit(31)
                self.__check_label(instr[0])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0]))
            elif instr.attrib['opcode'] in ['PUSHS', 'WRITE', 'EXIT', 'DPRINT']:
                if len(list(instr)) is not 1:
                    # TODO: ERROR nespravny pocet argumentu instrukce
                    exit(31)
                self.__check_symbol(instr[0])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0]))
            elif instr.attrib['opcode'] in ['MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'NOT']:
                if len(list(instr)) is not 2:
                    # TODO: ERROR nespravny pocet argumentu instrukce
                    exit(31)
                self.__check_variable(instr[0])
                self.__check_symbol(instr[1])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0], arg2=instr[1]))
            elif instr.attrib['opcode'] == 'READ':
                if len(list(instr)) is not 2:
                    # TODO: ERROR nespravny pocet argumentu instrukce
                    exit(31)
                self.__check_variable(instr[0])
                self.__check_type(instr[1])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0], arg2=instr[1]))
            elif instr.attrib['opcode'] in ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR',
                                            'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR']:
                if len(list(instr)) is not 3:
                    # TODO: ERROR nespravny pocet argumentu instrukce
                    exit(31)
                self.__check_variable(instr[0])
                self.__check_symbol(instr[1])
                self.__check_symbol(instr[2])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0], arg2=instr[1], arg3=instr[2]))
            elif instr.attrib['opcode'] in ['JUMPIFEQ', 'JUMPIFNEQ']:
                if len(list(instr)) is not 3:
                    # TODO: ERROR nespravny pocet argumentu instrukce
                    exit(31)
                self.__check_label(instr[0])
                self.__check_symbol(instr[1])
                self.__check_symbol(instr[2])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0], arg2=instr[1], arg3=instr[2]))
            else:
                # TODO: ERROR nepovolena instrukce
                exit(32)

    def __check_variable(self, variable):
        if variable.attrib['type'] != 'var':
            # TODO: ERROR wrong atribut promenne
            exit(52)
        if variable.text is None or not re.match('^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][\w_\-$&%*!?]*$', variable.text):
            # TODO: ERROR bad value of var
            exit(32)

    def __check_symbol(self, symbol):
        if symbol.attrib['type'] == 'var':
            self.__check_variable(symbol)
        elif symbol.attrib['type'] == 'int':
            if symbol.text is None or not re.match('^([+-]?[1-9][0-9]*|[+-]?(0-9))$', symbol.text):
                print('Zadany int neni typu integer.', file=sys.stderr)
                exit(32)
        elif symbol.attrib['type'] == 'bool':
            if symbol.text is None or symbol.text not in ['true', 'false']:
                print('Zadany bool nema hodnotu true/false.', file=sys.stderr)
                exit(32)
        elif symbol.attrib['type'] == 'nil':
            if symbol.text is None or symbol.text != 'nil':
                # TODO: ERROR nil nema nil
                exit(32)
        elif symbol.attrib['type'] == 'string':
            if symbol.text is None:
                symbol.text = ''
                return
            if not re.search('^(\\\\[0-9]{3}|[^\s\\\\#])*$', symbol.text):
                # TODO: ERROR bad string
                exit(32)
            # TODO: STRING escape sequence
        else:
            # TODO: ERROR symbol neni var/int/bool/nil/string
            exit(52)

    def __check_label(self, label):
        if label.attrib['type'] != 'label':
            # TODO: ERROR typ neni label
            exit(52)
        if label.text is None or not re.match('^[a-zA-Z_\-$&%*!?][\w_\-$&%*!?]*', label.text):
            # TODO: ERROR bad label
            exit(32)

    def __check_type(self, type):
        if type.attrib['type'] != 'type':
            # TODO: ERROR chybny atribut type
            exit(52)
        if type.attrib['type'] is None or not re.match('^(int|bool|nil|string)$', type.text):
            # TODO: ERROR chybny typ
            exit(32)
