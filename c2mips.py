import sys
import os
from antlr4 import *
from graphviz import Digraph
from C_GrammarLexer import C_GrammarLexer
from C_GrammarParser import C_GrammarParser
from C_GrammarListener import C_GrammarListener
from C_GrammarVisitor import C_GrammarVisitor
from SymbolTable import SymbolTable
from AST import AST, GrammarListener
from MIPSGenerator import MIPSGenerator
from CErrorListener import CErrorListener
from LivenessControl import LivenessControl

def main(argv):
	if not os.path.exists("dotfiles"):
		os.makedirs("dotfiles")

	dropCode = True
	inputFileName = argv[1]
	outputFileName = argv[2]
	dotName = argv[2]
	if len(argv) == 4:
		if argv[1] == "-s":
			dropCode = False
		if argv[3][-2:].upper() == ".C":
			dotName = argv[3][:-2]
		else:
			dotName = argv[3]

		inputFileName = argv[2]
		outputFileName = argv[3]
		

	input = FileStream(inputFileName)
	print("\033[92mCompiling and executing {}\033[0m".format(inputFileName))

	lexer = C_GrammarLexer(input)
	stream = CommonTokenStream(lexer)
	parser = C_GrammarParser(stream)
	parser.addErrorListener(CErrorListener()) 
	tree = parser.start()
	printer = GrammarListener()
	walker = ParseTreeWalker()
	walker.walk(printer, tree)
	printer.AST_Root.to_dot(dotName)

	symbol_table = SymbolTable()
	symbol_table.fill_tree(printer.AST_Root)

	LC = LivenessControl(symbol_table)
	LC.checkLiveness(printer.AST_Root, dropCode)

	CG = MIPSGenerator(printer.AST_Root, symbol_table)
	CG.generate()

	symbol_table.to_dot(dotName)	
	CG.writeToFile(outputFileName)


if __name__ == '__main__':
	main(sys.argv)
