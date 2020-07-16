import logging

from .bound_binary_expression import BoundBinaryExpression
from .bound_binary_operator import BoundBinaryOperator
from .bound_literal_expression import BoundLiteralExpression
from .bound_unary_expression import BoundUnaryExpression
from .bound_unary_operator import BoundUnaryOperator
from ..diagnostic import DiagnosticBag
from ..syntax.syntax_kind import SyntaxKind


class Binder:

    def __init__(self):
        self.diagnostic_bag = DiagnosticBag()

    def bind_expression(self, syntax):
        if syntax.kind is SyntaxKind.LITERAL_EXPRESSION:
            return self._bind_literal_expression(syntax)
        elif syntax.kind is SyntaxKind.UNARY_EXPRESSION:
            return self._bind_unary_expression(syntax)
        elif syntax.kind is SyntaxKind.BINARY_EXPRESSION:
            return self._bind_binary_expression(syntax)
        elif syntax.kind is SyntaxKind.PARENTHESIZED_EXPRESSION:
            return self.bind_expression(syntax.expression)
        else:
            raise Exception(f'Unexpected syntax {syntax.kind}')

    def _bind_literal_expression(self, syntax):
        value = 0 if syntax.value is None else syntax.value
        return BoundLiteralExpression(value)

    def _bind_unary_expression(self, syntax):
        bound_operand = self.bind_expression(syntax.operand)
        bound_operator = BoundUnaryOperator.bind(syntax.operator_token.kind, bound_operand.type)
        if bound_operator is None:
            self.diagnostic_bag.report_undefined_unary_operator(
                syntax.operator_token.text_span,
                syntax.operator_token.string,
                syntax.operator_token.type,
                logging.ERROR
            )
            return bound_operand
        else:
            return BoundUnaryExpression(bound_operator, bound_operand)

    def _bind_binary_expression(self, syntax):
        bound_left = self.bind_expression(syntax.left)
        bound_right = self.bind_expression(syntax.right)
        bound_operator = BoundBinaryOperator.bind(
            syntax.operator_token.kind,
            bound_left.type,
            bound_right.type
        )

        if bound_operator is None:
            self.diagnostic_bag.report_undefined_binary_operator(
                syntax.operator_token.text_span,
                syntax.operator_token.text,
                bound_left.type,
                bound_right.type,
                logging.ERROR
            )
            return bound_left
        else:
            return BoundBinaryExpression(bound_left, bound_operator, bound_right)
