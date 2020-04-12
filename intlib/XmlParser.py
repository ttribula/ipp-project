import xml.etree.ElementTree as ET
import re

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
            # TODO: ERROR soubor nenalezen
            exit(11)
        except Exception:
            # TODO: ERROR spatna struktura XML
            exit(31)

        if self.root.tag is not 'program':
            # TODO: ERROR root element nema program
            exit(31)

        for attr in self.root.attr:
            if attr not in ['language', 'name', 'description']:
                # TODO: ERROR nepovolene atributy <program>
                exit(31)

        if 'language' not in self.root.attr:
            # TODO: ERROR neni language v <program>
            exit(31)
        if str(self.root.attr['language']).lower() is not 'ippcode20':
            # TODO: ERROR language neni ippcode20
            exit(31)

        instr_order = []
        for instr in self.root:
            if instr.tag is not 'instruction':
                # TODO: ERROR spatny nazev elementu instr
                exit(31)
            if 'opcode' not in instr.attr:
                # TODO: ERROR opcode neni v elementu instr
                exit(31)
            if 'order' not in instr.attr:
                # TODO: ERROR order neni v elementu instr
                exit(31)
            instr_order.append(instr.attr['order'])

            arg_count = 0
            for arg in instr:
                arg_count += 1
                if arg.tag is not 'arg' + str(arg_count):
                    # TODO: ERROR arg bad name
                    exit(31)
                if 'type' not in arg.attr:
                    # TODO: ERROR type neni
                    exit(31)
                if arg.attr['type'] not in ['int', 'bool', 'string', 'nil', 'label', 'type', 'var']:
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
            pass
        if instr.attr['opcode'] in ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', "BREAK"]:
            if len(list(instr)) is not 0:
                # TODO: ERROR nespravny pocet argumentu instrukce
                exit(31)
            self.instrList.insert_instr(Instr(instr.attr['opcode'], arg1=instr[0]))
        elif instr.attr['opcode'] in ['DEFVAR', 'POPS']:
            if len(list(instr)) is not 1:
                # TODO: ERROR nespravny pocet argumentu instrukce
                exit(31)
            self.check_variable(instr[0])
            self.instrList.insert_instr(Instr(instr.attr['opcode'], arg1=instr[0]))
        elif instr.attr['opcode'] in ['CALL', 'LABEL', 'JUMP']:
            if len(list(instr)) is not 1:
                # TODO: ERROR nespravny pocet argumentu instrukce
                exit(31)
            self.check_label(instr[0])
            self.instrList.insert_instr(Instr(instr.attr['opcode'], arg1=instr[0]))
        elif instr.attr['opcode'] in ['PUSHS', 'WRITE', 'EXIT', 'DPRINT']:
            if len(list(instr)) is not 1:
                # TODO: ERROR nespravny pocet argumentu instrukce
                exit(31)
            self.check_symbol(instr[0])
            self.instrList.insert_instr(Instr(instr.attr['opcode'], arg1=instr[0]))
        elif instr.attr['opcode'] in ['MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'NOT']:
            if len(list(instr)) is not 2:
                # TODO: ERROR nespravny pocet argumentu instrukce
                exit(31)
            self.check_variable(instr[0])
            self.check_symbol(instr[1])
            self.instrList.insert_instr(Instr(instr.attr['opcode'], arg1=instr[0], arg2=instr[1]))
        elif instr.attr['opcode'] is 'READ':
            if len(list(instr)) is not 2:
                # TODO: ERROR nespravny pocet argumentu instrukce
                exit(31)
            self.check_variable(instr[0])
            self.check_type(instr[1])
            self.instrList.insert_instr(Instr(instr.attr['opcode'], arg1=instr[0], arg2=instr[1]))
        elif instr.attr['opcode'] in ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR',
                                      'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR']:
            if len(list(instr)) is not 3:
                # TODO: ERROR nespravny pocet argumentu instrukce
                exit(31)
            self.check_variable(instr[0])
            self.check_symbol(instr[1])
            self.check_symbol(instr[2])
            self.instrList.insert_instr(Instr(instr.attr['opcode'], arg1=instr[0], arg2=instr[1], arg3=instr[2]))
        elif instr.attr['opcode'] in ['JUMPIFEQ', 'JUMPIFNEQ']:
            if len(list(instr)) is not 3:
                # TODO: ERROR nespravny pocet argumentu instrukce
                exit(31)
            self.check_label(instr[0])
            self.check_symbol(instr[1])
            self.check_symbol(instr[2])
            self.instrList.insert_instr(Instr(instr.attr['opcode'], arg1=instr[0], arg2=instr[1], arg3=instr[2]))
        else:
            # TODO: ERROR nepovolena instrukce
            exit(32)

    def check_variable(self, variable):
        if variable.attr['type'] is not 'var':
            # TODO: ERROR wrong atribut promenne
            exit(52)
        if variable.value is None or not re.match('^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][\w_\-$&%*!?]*$', variable.value):
            # TODO: ERROR bad value of var
            exit(32)

    def check_symbol(self, symbol):
        if symbol.attr['type'] is 'var':
            self.check_variable(symbol)
        elif symbol.attr['type'] is 'int':
            if symbol.value is None or not re.match('^([+-]?[1-9][0-9]*|[+-]?(0-9))$', symbol.value):
                # TODO: ERROR int neni cislo
                exit(32)
        elif symbol.attr['type'] is 'bool':
            if symbol.value is None or symbol.value in ['true', 'false']:
                # TODO: ERROR bool neni true/false
                exit(32)
        elif symbol.attr['type'] is 'nil':
            if symbol.value is None or symbol.value is not 'nil':
                # TODO: ERROR nil nema nil
                exit(32)
        elif symbol.attr['type'] is 'string':
            if symbol.value is None:
                symbol.value = ''
                return
            if not re.search('^(\\\\[0-9]{3}|[^\s\\\\#])*$', symbol.value):
                # TODO: ERROR bad string
                exit(32)
            # TODO: STRING escape sequence
        else:
            # TODO: ERROR symbol neni var/int/bool/nil/string
            exit(52)

    def check_label(self, label):
        if label.attr['type'] is not 'label':
            # TODO: ERROR typ neni label
            exit(52)
        if label.value is None or not re.match('^[a-zA-Z_\-$&%*!?][\w_\-$&%*!?]*', label.value):
            # TODO: ERROR bad label
            exit(32)

    def check_type(self, type):
        if type.attr['type'] is not 'type':
            # TODO: ERROR chybny atribut type
            exit(52)
        if type.attr['type'] is None or not re.match('^(int|bool|nil|string)$', type.value):
            # TODO: ERROR chybny typ
            exit(32)
