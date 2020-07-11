import logging
import os
import subprocess
import itertools

from .binder.binder import Binder
from .evaluator import Evaluator
from .syntax.parser import SyntaxTree
from .syntax.syntax_token import SyntaxToken


def main():

    def pretty_print(node, indent='', is_last=True):
        marker = '└──' if is_last else '├──'
        print(indent, end='')
        print(marker, end='')
        print(node.kind.name, end='')
        if type(node) is SyntaxToken:
            if node.value is not None:
                print(':   ' + str(node.value), end='')
            print()
        else:
            print()
            indent += '    ' if is_last else '│   '
            *_, last_child = node.get_children()
            for child in node.get_children():
                pretty_print(child, indent, child == last_child)

    def clear():
        if os.name in ('nt', 'dos'):
            subprocess.call('cls', shell=True)
        elif os.name in ('linux', 'osx', 'posix'):
            subprocess.call("clear")
        else:
            for _ in range(120):
                print('\n')

    def process_input():
        nonlocal show_tree
        if term == '' or term.isspace() or term is None:
            print('You have to enter a valid term\n')
            return
        elif term == '#showtree':
            show_tree = not show_tree
            print('Showing parse trees' if show_tree else 'Hiding parse trees')
            return
        elif term == '#cls' or term == '#clear':
            clear()
            return

        syntax_tree = SyntaxTree.parse(term, logger)
        binder = Binder()
        bound_expression = binder.bind_expression(syntax_tree.root)

        if show_tree:
            pretty_print(syntax_tree.root)

        if syntax_tree.diagnostics or binder.diagnostics:
            for diagnostic, level in itertools.chain(syntax_tree.diagnostics, binder.diagnostics):
                logger.log(level, diagnostic)
        else:
            evaluator = Evaluator(bound_expression)
            result = evaluator.evaluate()
            print(result)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    show_tree = False
    while True:
        term = input('Enter a mathematical term\n')
        process_input()


if __name__ == "__main__":
    main()
