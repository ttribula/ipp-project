import xml.etree.ElementTree as ET
import re
import sys

from intlib.Instructions import Instr

from time import sleep

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
            print('CHYBA: Soubor {} nelze otevrit.'.format(self.source), file=sys.stderr)
            exit(11)
        except Exception:
            print('CHYBA: Spatne formatovany XML soubor.', file=sys.stderr)
            exit(31)

        if self.root.tag != 'program':
            print('CHYBA: Korenovy element nema <program>.', file=sys.stderr)
            exit(31)

        for attr in self.root.attrib:
            if attr not in ['language', 'name', 'description']:
                print('CHYBA: Nepovolene atributy korenoveho elementu <program>.', file=sys.stderr)
                exit(31)

        if 'language' not in self.root.attrib:
            print('CHYBA: Neni definovan jazyk v korenovem elementu <program>.', file=sys.stderr)
            exit(31)
        if str(self.root.attrib['language']).lower() != 'ippcode20':
            print('CHYBA: Jazyk definovany v korenovem elementu <program> neni ippcode20.', file=sys.stderr)
            exit(31)

        instr_order = []
        for instr in self.root:
            if instr.tag != 'instruction':
                print('CHYBA: Spatny nazev elementu instrukce.', file=sys.stderr)
                exit(31)
            if 'opcode' not in instr.attrib:
                print('CHYBA: Atribut opcode chybi v elementu instrukce.', file=sys.stderr)
                exit(31)
            if 'order' not in instr.attrib:
                print('CHYBA: Atribut order chybi v elementu instrukce.', file=sys.stderr)
                exit(31)
            instr_order.append(instr.attrib['order'])

            arg_count = 0
            for arg in instr:
                arg_count += 1
                if arg.tag != 'arg' + str(arg_count):
                    print('CHYBA: Spatne pojmenovani argumentu.', file=sys.stderr)
                    exit(31)
                if 'type' not in arg.attrib:
                    print('CHYBA: Atribut type chybi v elementu instrukce.', file=sys.stderr)
                    exit(31)
                if arg.attrib['type'] not in ['int', 'bool', 'string', 'nil', 'label', 'type', 'var']:
                    print('CHYBA: Spatny datovy typ v atributu argumentu.', file=sys.stderr)
                    exit(31)
            for i in instr_order:
                if int(i) <= 0:
                    print('CHYBA: Zaporny atribut argumentu order.', file=sys.stderr)
                    exit(31)
            if len(set(instr_order)) is not len(instr_order):
                print('CHYBA: Duplicitni hodnota order.', file=sys.stderr)
                exit(31)

        # -----------Kontrola instrukci---------------
        for instr in self.root:
            if instr.attrib['opcode'] in ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK']:
                if len(list(instr)) is not 0:
                    print('CHYBA: Nespravny poceet argumentu instrukce {}. Potreba: {}'.format(instr.attrib['opcode'], 0), file=sys.stderr)
                    exit(31)
                self.instrList.insert_instr(Instr(instr.attrib['opcode']))
            elif instr.attrib['opcode'] in ['DEFVAR', 'POPS']:
                if len(list(instr)) is not 1:
                    print('CHYBA: Nespravny poceet argumentu instrukce {}. Potreba: {}'.format(instr.attrib['opcode'], 1), file=sys.stderr)
                    exit(31)
                self.__check_variable(instr[0])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0]))
            elif instr.attrib['opcode'] in ['CALL', 'LABEL', 'JUMP']:
                if len(list(instr)) is not 1:
                    print('CHYBA: Nespravny poceet argumentu instrukce {}. Potreba: {}'.format(instr.attrib['opcode'], 1), file=sys.stderr)
                    exit(31)
                self.__check_label(instr[0])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0]))
            elif instr.attrib['opcode'] in ['PUSHS', 'WRITE', 'EXIT', 'DPRINT']:
                if len(list(instr)) is not 1:
                    print('CHYBA: Nespravny poceet argumentu instrukce {}. Potreba: {}'.format(instr.attrib['opcode'], 1), file=sys.stderr)
                    exit(31)
                self.__check_symbol(instr[0])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0]))
            elif instr.attrib['opcode'] in ['MOVE', 'INT2CHAR', 'STRLEN', 'TYPE', 'NOT']:
                if len(list(instr)) is not 2:
                    print('CHYBA: Nespravny poceet argumentu instrukce {}. Potreba: {}'.format(instr.attrib['opcode'], 2), file=sys.stderr)
                    exit(31)
                self.__check_variable(instr[0])
                self.__check_symbol(instr[1])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0], arg2=instr[1]))
            elif instr.attrib['opcode'] == 'READ':
                if len(list(instr)) is not 2:
                    print('CHYBA: Nespravny poceet argumentu instrukce {}. Potreba: {}'.format(instr.attrib['opcode'], 2), file=sys.stderr)
                    exit(31)
                self.__check_variable(instr[0])
                self.__check_type(instr[1])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0], arg2=instr[1]))
            elif instr.attrib['opcode'] in ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR',
                                            'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR']:
                if len(list(instr)) is not 3:
                    print('CHYBA: Nespravny poceet argumentu instrukce {}. Potreba: {}'.format(instr.attrib['opcode'], 3), file=sys.stderr)
                    exit(31)
                self.__check_variable(instr[0])
                self.__check_symbol(instr[1])
                self.__check_symbol(instr[2])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0], arg2=instr[1], arg3=instr[2]))
            elif instr.attrib['opcode'] in ['JUMPIFEQ', 'JUMPIFNEQ']:
                if len(list(instr)) is not 3:
                    print('CHYBA: Nespravny poceet argumentu instrukce {}. Potreba: {}'.format(instr.attrib['opcode'], 3), file=sys.stderr)
                    exit(31)
                self.__check_label(instr[0])
                self.__check_symbol(instr[1])
                self.__check_symbol(instr[2])
                self.instrList.insert_instr(Instr(instr.attrib['opcode'], arg1=instr[0], arg2=instr[1], arg3=instr[2]))
            else:
                print('CHYBA: Nepovolena instrukce: {}'.format(instr.attrib['opcode']), file=sys.stderr)
                exit(32)

    def __check_variable(self, variable):
        if variable.attrib['type'] != 'var':
            print('CHYBA: Spatna promenna', file=sys.stderr)
            exit(52)
        if variable.text is None or not re.match('^(GF|LF|TF)@([a-z]|[A-Z]|_|-|$|&|%|\*|!|\?)([0-9]|[a-z]|[A-Z]|_|-|$|&|%|\*|!|\?)*$', variable.text):
            print('CHYBA: Spatna hodnota promenne', file=sys.stderr)
            exit(32)

    def __check_symbol(self, symbol):
        if symbol.attrib['type'] == 'var':
            self.__check_variable(symbol)
        elif symbol.attrib['type'] == 'int':
            if symbol.text is None or not re.match('^([+-]?[1-9][0-9]*|[+-]?(0-9))$', symbol.text):
                print('CHYBA: Zadany int neni typu integer.', file=sys.stderr)
                exit(32)
        elif symbol.attrib['type'] == 'bool':
            if symbol.text is None or symbol.text not in ['true', 'false']:
                print('CHYBA: Zadany bool nema hodnotu true/false.', file=sys.stderr)
                exit(32)
        elif symbol.attrib['type'] == 'nil':
            if symbol.text is None or symbol.text != 'nil':
                print('CHYBA: Typ nil neobsahuje hodnotu nil.', file=sys.stderr)
                exit(32)
        elif symbol.attrib['type'] == 'string':
            if symbol.text is None:
                symbol.text = ''
                return
            if not re.search('^(\\\\[0-9]{3}|[^\s\\\\#])*$', symbol.text):
                print('CHYBA: String neodpovida zadani.', file=sys.stderr)
                exit(32)
            symbol.text = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x.group(1))), symbol.text)
        else:
            print('CHYBA: Symbol nelze poznat.', file=sys.stderr)
            exit(52)

    def __check_label(self, label):
        if label.attrib['type'] != 'label':
            print('CHYBA: Spatny typ label', file=sys.stderr)
            exit(52)
        if label.text is None or not re.match('^[a-zA-Z_\-$&%*!?][\w_\-$&%*!?]*', label.text):
            print('CHYBA: Spatny nazev navesti', file=sys.stderr)
            exit(32)

    def __check_type(self, type):
        if type.attrib['type'] != 'type':
            print('CHYBA: Chybny typ typu.', file=sys.stderr)
            exit(52)
        if type.attrib['type'] is None or not re.match('^(int|bool|nil|string)$', type.text):
            print('CHYBA: Chybny typ typu.', file=sys.stderr)
            exit(32)
