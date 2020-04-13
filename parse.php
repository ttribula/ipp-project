<?php
/*
 * IPP projekt - 1. část 
 *
 *
 * parse.php - Skript typu filtr (PHP 7.4) načte ze standardního vstupu zdrojový kód v IPP-code20,
 *             zkontroluje lexikální a syntaktickou správnost kódu a vypíše na standardní
 *             výstup XML reprezentaci programu. 
 *
 * Autor: Tomáš Tribula (xtribu02@stud.fit.vutbr.cz)
 *
 */


const T_MOVE = 35;
const T_CREATEFRAME = 1;
const T_PUSHFRAME = 2;
const T_POPFRAME = 3;
const T_DEFVAR = 4;
const T_CALL = 5;
const T_RET = 6;
const T_PUSHS = 7;
const T_POPS = 8;
const T_ADD = 9;
const T_SUB = 10;
const T_MUL = 11;
const T_IDIV = 12;
const T_LT = 13;
const T_GT = 14;
const T_EQ = 15;
const T_AND = 16;
const T_OR = 17;
const T_NOT = 18;
const T_INT2CHAR = 19;
const T_STRI2INT = 20;
const T_READ = 21;
const T_WRITE = 22;
const T_CONCAT = 23;
const T_STRLEN = 24;
const T_GETCHAR = 25;
const T_SETCHAR = 26;
const T_TYPE = 27;
const T_LABEL = 28;
const T_JUMP = 29;
const T_JUMPIFEQ = 30;
const T_JUMPIFNEQ = 31;
const T_EX = 32;
const T_DPRINT = 33;
const T_BRK = 34;
const T_ID = 36;
const T_CONSTANT = 37;
const T_EOF = 38;
const T_HEADER = 39;
const T_LABEL_NAME = 40;
const T_VAR_TYPE = 41;

const argsErr = 10;
const missingHeaderErr = 21;
const uknMissOpCodeErr = 22;
const otherLexSynErr = 23;

$instructions = array(
        T_CREATEFRAME => "CREATEFRAME",
        T_PUSHFRAME => "PUSHFRAME",
        T_POPFRAME => "POPFRAME",
        T_DEFVAR => "DEFVAR",
        T_CALL => "CALL",
        T_RET => "RETURN",
        T_PUSHS => "PUSHS",
        T_POPS => "POPS",
        T_ADD => "ADD",
        T_SUB => "SUB",
        T_MUL => "MUL",
        T_IDIV => "IDIV",
        T_LT => "LT",
        T_GT => "GT",
        T_EQ => "EQ",
        T_AND => "AND",
        T_OR => "OR",
        T_NOT => "NOT",
        T_INT2CHAR => "INT2CHAR",
        T_STRI2INT => "STRI2INT",
        T_READ => "READ",
        T_WRITE => "WRITE",
        T_CONCAT => "CONCAT",
        T_STRLEN => "STRLEN",
        T_GETCHAR => "GETCHAR",
        T_SETCHAR => "SETCHAR",
        T_TYPE => "TYPE",
        T_LABEL => "LABEL",
        T_JUMP => "JUMP",
        T_JUMPIFEQ => "JUMPIFEQ",
        T_JUMPIFNEQ => "JUMPIFNEQ",
        T_EX => "EXIT",
        T_DPRINT => "DPRINT",
        T_BRK => "BREAK",
        T_MOVE => "MOVE"
        );

#---------Lexical analysis-----------
function scanLine() {
    global $instructions;
    $scanOutput = array();
    while(1) {
        if (!($inputLine = fgets(STDIN))) {
            array_push($scanOutput, array(T_EOF));
            return $scanOutput;
        }
        if (preg_match("~^\s+#~", $inputLine)) {
            continue;
        }
        if ($inputLine == "\n") {
            array_push($scanOutput, array("\n"));
            return $scanOutput;
        }
        $line = explode("#", $inputLine);
        $formLine = preg_split("~\s+~", $line[0]);
        break;
    }
    $isName = false; # so program can tell if instruction word is used as label name
#checking input
    foreach ($formLine as $item) {
        if (preg_match("~@~", $item)) { #variable or constant
            if (preg_match("~^(int|string|bool|nil)~", $item)) { # constant
                if (preg_match("~^int@[+-]?[0-9]+$~", $item) ||
                        preg_match("~^string@~", $item) ||
                        preg_match("~^bool@(true|false)$~", $item) ||
                        preg_match("~^nil@nil$~", $item)) {
                   array_push($scanOutput, array_merge(array(T_CONSTANT), explode("@", $item, 2)));
                } else {
                   exit(otherLexSynErr);
                }
            } else { # variable
                if (preg_match("~^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][0-9a-zA-Z_\-$&%*!?]*$~", $item))
                   array_push($scanOutput, array(T_ID, $item));
                else
                   exit(otherLexSynErr);
                }
        } else { # instruction, header, label name or type of variable
            if (($instr = array_search(Strtoupper($item), $instructions)) && !$isName) {
                array_push($scanOutput, array($instr));
                $isName = true;
            } elseif (preg_match("~^\s*\.[Ii][Pp][Pp][Cc][Oo][Dd][Ee]20\s*$~", $item)) {
                array_push($scanOutput, array(T_HEADER, $item));
            } elseif (preg_match("~^(int|string|bool)$~", $item)) {
                array_push($scanOutput, array(T_VAR_TYPE, $item));
            } else {
                if (preg_match("~^[a-zA-Z_\-$&%*!?][0-9a-zA-Z_\-$&%*!?]*$~", $item)) {
                   array_push($scanOutput, array(T_LABEL_NAME, $item));
                }
            }
        }
    }
    return $scanOutput;
}

#---------Syntax  analysis-----------
function syntaxAnalysis() {
    global $instructions;
    global $instrOrder;

    $xmlDOM = new DOMDocument('1.0', 'UTF-8');
    $xmlDOM->formatOutput = true;
    $xmlDoc = $xmlDOM->createElement("program");
    $xmlDoc->setAttribute("language", "IPPcode20");
    $xmlDoc = $xmlDOM->appendChild($xmlDoc);

    $line = scanLine();
    $countLine = count($line); # to save some count() calls
    while (1) {
        if ($countLine > 0 && $line[0][0] != "\n") {
            if (($countLine != 1 && $line[0][0] != T_HEADER) || $line[0][0] == T_EOF)
                exit(missingHeaderErr);
        }
        if ($countLine == 1 && $line[0][0] == T_HEADER)
            break;
        $line = scanLine();
        $countLine = count($line);
    }
    while (1) {
        $line = scanLine();
        $countLine = count($line);
        if ($countLine > 0) {
            if ($line[0][0] == T_EOF) {
                break;
            } elseif ($line[0][0] == "\n") {
                continue;
            } elseif ($line[0][0] < 36) {
                $instrOrder++;

                $xmlInstr = $xmlDOM->createElement("instruction");
                $xmlInstr->setAttribute("order", $instrOrder);
                $xmlInstr->setAttribute("opcode", $instructions[$line[0][0]]);

                switch (Strtoupper($line[0][0])) {
                    case T_CREATEFRAME:
                    case T_PUSHFRAME:
                    case T_POPFRAME:
                    case T_RET:
                    case T_BRK:
                        if ($countLine > 1)
                            exit(uknMissOpCodeErr);
                        break;
                    case T_DEFVAR:
                    case T_POPS:
                        if ($countLine == 2 && $line[1][0] == T_ID) {
                            $xmlInstrArg = $xmlDOM->createElement("arg1", htmlspecialchars($line[1][1]));
                            $xmlInstrArg->setAttribute("type", "var");
                            $xmlInstr->appendChild($xmlInstrArg);
                        } else {
                            exit(uknMissOpCodeErr);
                        }
                        break;
# variable
                    case T_CALL:
                    case T_LABEL:
                    case T_JUMP:
                        if ($countLine == 2 && $line[1][0] == T_LABEL_NAME) {
                            $xmlInstrArg = $xmlDOM->createElement("arg1", htmlspecialchars($line[1][1]));
                            $xmlInstrArg->setAttribute("type", "label");
                            $xmlInstr->appendChild($xmlInstrArg);
                        } else {
                            exit(uknMissOpCodeErr);
                        }
                        break;
# label
                    case T_PUSHS:
                    case T_WRITE:
                    case T_EXIT:
                    case T_DPRINT:
                        if ($countLine == 2 && $line[1][0] == T_CONSTANT) {
                            $xmlInstrArg = $xmlDOM->createElement("arg1", htmlspecialchars($line[1][2]));
                            $xmlInstrArg->setAttribute("type", $line[1][1]);
                        } elseif ($countLine == 2 && $line[1][0] == T_ID) {
                            $xmlInstrArg = $xmlDOM->createElement("arg1", htmlspecialchars($line[1][1]));
                            $xmlInstrArg->setAttribute("type", "var");
                        } else {
                            exit(uknMissOpCodeErr);
                        }
                        $xmlInstr->appendChild($xmlInstrArg);
                        break;
# symb
                    case T_MOVE:
                    case T_INT2CHAR:
                    case T_STRLEN:
                    case T_TYPE:
                    case T_NOT:
                        if ($countLine == 3 && $line[1][0] == T_ID && ($line[2][0] == T_CONSTANT || $line[2][0] == T_ID)){
                            $xmlInstrArg = $xmlDOM->createElement("arg1", htmlspecialchars($line[1][1]));
                            $xmlInstrArg->setAttribute("type", "var");
                            if ($line[2][0] == T_CONSTANT) {
                                $xmlInstrArg1 = $xmlDOM->createElement("arg2", htmlspecialchars($line[2][2]));
                                $xmlInstrArg1->setAttribute("type", $line[2][1]);
                            } else {
                                $xmlInstrArg1 = $xmlDOM->createElement("arg2", htmlspecialchars($line[2][1]));
                                $xmlInstrArg1->setAttribute("type", "var");
                            }
                            $xmlInstr->appendChild($xmlInstrArg);
                            $xmlInstr->appendChild($xmlInstrArg1);
                        } else {
                            exit(uknMissOpCodeErr);
                        }
                        break;
                    case T_READ:
                        if ($countLine == 3 && ($line[1][0] == T_ID && $line[2][0] == T_VAR_TYPE)) {
                            $xmlInstrArg = $xmlDOM->createElement("arg1", htmlspecialchars($line[1][1]));
                            $xmlInstrArg->setAttribute("type", "var");
                            $xmlInstrArg1 = $xmlDOM->createElement("arg2", htmlspecialchars($line[2][1]));
                            $xmlInstrArg1->setAttribute("type", "type");
                            $xmlInstr->appendChild($xmlInstrArg);
                            $xmlInstr->appendChild($xmlInstrArg1);
                        } else {
                            exit(uknMissOpCodeErr);
                        }
                        break;
#var nad type
                    case T_ADD:
                    case T_SUB:
                    case T_MUL:
                    case T_IDIV:
                    case T_LT:
                    case T_GT:
                    case T_EQ:
                    case T_AND:
                    case T_OR:
                    case T_STRI2INT:
                    case T_CONCAT:
                    case T_GETCHAR:
                    case T_SETCHAR:
                        if ($countLine == 4 && ($line[1][0] == T_ID &&
                                    ($line[2][0] == T_CONSTANT || $line[2][0] == T_ID) &&
                                    ($line[3][0] == T_CONSTANT || $line[3][0] == T_ID))) {
                            $xmlInstrArg = $xmlDOM->createElement("arg1", htmlspecialchars($line[1][1]));
                            $xmlInstrArg->setAttribute("type", "var");
                            if ($line[2][0] == T_CONSTANT) {
                                $xmlInstrArg1 = $xmlDOM->createElement("arg2", htmlspecialchars($line[2][2]));
                                $xmlInstrArg1->setAttribute("type", $line[2][1]);
                            } else {
                                $xmlInstrArg1 = $xmlDOM->createElement("arg2", htmlspecialchars($line[2][1]));
                                $xmlInstrArg1->setAttribute("type", "var");
                            }
                            if ($line[2][0] == T_CONSTANT) {
                                $xmlInstrArg2 = $xmlDOM->createElement("arg3", htmlspecialchars($line[3][2]));
                                $xmlInstrArg2->setAttribute("type", $line[3][1]);
                            } else {
                                $xmlInstrArg2 = $xmlDOM->createElement("arg3", htmlspecialchars($line[3][1]));
                                $xmlInstrArg2->setAttribute("type", "var");
                            }
                            $xmlInstr->appendChild($xmlInstrArg);
                            $xmlInstr->appendChild($xmlInstrArg1);
                            $xmlInstr->appendChild($xmlInstrArg2);
                        } else {
                            exit(uknMissOpCodeErr);
                        }
                        break;
                    case T_JUMPIFEQ:
                    case T_JUMPIFNEQ:
                        if ($countLine == 4 && $line[1][0] == T_LABEL_NAME &&
                                ($line[2][0] == T_CONSTANT || $line[2][0] == T_ID) &&
                                ($line[3][0] == T_CONSTANT || $line[3][0] == T_ID)) {
                            $xmlInstrArg = $xmlDOM->createElement("arg1", htmlspecialchars($line[1][1]));
                            $xmlInstrArg->setAttribute("type", "var");
                            if ($line[2][0] == T_CONSTANT) {
                                $xmlInstrArg1 = $xmlDOM->createElement("arg2", htmlspecialchars($line[2][2]));
                                $xmlInstrArg1->setAttribute("type", $line[2][1]);
                            } else {
                                $xmlInstrArg1 = $xmlDOM->createElement("arg2", htmlspecialchars($line[2][1]));
                                $xmlInstrArg1->setAttribute("type", "var");
                            }
                            if ($line[2][0] == T_CONSTANT) {
                                $xmlInstrArg2 = $xmlDOM->createElement("arg3", htmlspecialchars($line[3][2]));
                                $xmlInstrArg2->setAttribute("type", $line[3][1]);
                            } else {
                                $xmlInstrArg2 = $xmlDOM->createElement("arg3", htmlspecialchars($line[3][1]));
                                $xmlInstrArg2->setAttribute("type", "var");
                            }
                            $xmlInstr->appendChild($xmlInstrArg);
                            $xmlInstr->appendChild($xmlInstrArg1);
                            $xmlInstr->appendChild($xmlInstrArg2);
                        } else {
                            exit(uknMissOpCodeErr);
                        }
                        break;
                    default:
                        exit(uknMissOpCodeErr);
                        break;
                }
            } else {
                exit(uknMissOpCodeErr);
            }
        } else {
            continue;
        }
        $xmlDoc->appendChild($xmlInstr);
    }
    return $xmlDOM->saveXML();
}


function printHelp() {
    echo "Skript typu filtr načte ze standardního vstupu zdrojový kód v IPP-code20,\n".
        "zkontroluje lexikální a syntaktickou správnost kódu a vypíše\n".
        "na standardní výstup XML reprezentaci programu.\n";
}


if ($argc == 1) {
    try {
        echo syntaxAnalysis();
    }
    finally {
        exit(0);
    }
} else {
    if ($argv[1] == "--help") {
        if ($argc > 2)
            exit(argsErr);
        printHelp();
        exit(0);
    } else {
        exit(argsErr);
    }
}
exit(0);
