import xml.etree.ElementTree as ET
import re

from intlib.Instructions import Instr


class XmlParser:
    def __init__(self, source, instr_list):
        self.source = source
        self.instrList = instr_list

    def xml_check(self):
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

        for attrib in self.root.attrib:
            if attrib not in ['language', 'name', 'description']:
                # TODO: ERROR nepovolene atributy <program>
                exit(31)

        if 'language' not in self.root.attrib:
            # TODO: ERROR neni language v <program>
            exit(31)
        if str(self.root.attrib['language']).lower() is not 'ippcode20':
            # TODO: ERROR language neni ippcode20
            exit(31)

        instr_order = []
        for instr in self.root:
            if instr.tag is not 'instruction':
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
                if arg.tag is not 'arg'+str(arg_count):
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