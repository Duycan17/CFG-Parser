"""Java source code parser using javalang library."""

from dataclasses import dataclass, field
from typing import Any

import javalang
from javalang.tree import (
    Node,
    CompilationUnit,
    ClassDeclaration,
    MethodDeclaration,
    ConstructorDeclaration,
    Statement,
    IfStatement,
    WhileStatement,
    ForStatement,
    DoStatement,
    SwitchStatement,
    TryStatement,
    ReturnStatement,
    ThrowStatement,
    BreakStatement,
    ContinueStatement,
    BlockStatement,
    StatementExpression,
    LocalVariableDeclaration,
    VariableDeclarator,
    Assignment,
    MemberReference,
    MethodInvocation,
    BinaryOperation,
    TernaryExpression,
    ArraySelector,
    FieldDeclaration,
    FormalParameter,
    CatchClause,
    SwitchStatementCase,
    ForControl,
    EnhancedForControl,
)

from app.core.exceptions import JavaParseError, InvalidJavaCodeError


@dataclass
class ParsedVariable:
    """Represents a parsed variable reference."""

    name: str
    is_definition: bool
    line: int | None = None
    column: int | None = None


@dataclass
class ParsedStatement:
    """Represents a parsed statement with metadata."""

    node: Node
    statement_type: str
    code: str
    line_number: int | None
    column: int | None
    variables_defined: list[str] = field(default_factory=list)
    variables_used: list[str] = field(default_factory=list)
    children: list["ParsedStatement"] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedMethod:
    """Represents a parsed method with its body statements."""

    name: str
    class_name: str
    return_type: str
    parameters: list[str]
    parameter_types: list[str]
    statements: list[ParsedStatement]
    line_start: int | None
    line_end: int | None
    is_constructor: bool = False


@dataclass
class ParsedClass:
    """Represents a parsed class with its methods."""

    name: str
    methods: list[ParsedMethod]
    fields: list[str]
    line_start: int | None
    line_end: int | None


class JavaParser:
    """Parser for Java source code using javalang library."""

    def __init__(self) -> None:
        self._source_lines: list[str] = []

    def parse(self, source_code: str) -> list[ParsedClass]:
        """Parse Java source code and return structured representation.

        Args:
            source_code: Java source code string.

        Returns:
            List of parsed classes with their methods and statements.

        Raises:
            JavaParseError: If parsing fails.
            InvalidJavaCodeError: If code is not valid Java.
        """
        self._source_lines = source_code.split("\n")

        try:
            tree = javalang.parse.parse(source_code)
        except javalang.parser.JavaSyntaxError as e:
            raise JavaParseError(f"Java syntax error: {e}", details=str(e))
        except Exception as e:
            raise InvalidJavaCodeError(f"Failed to parse Java code: {e}", details=str(e))

        return self._extract_classes(tree)

    def _extract_classes(self, tree: CompilationUnit) -> list[ParsedClass]:
        """Extract all classes from the compilation unit."""
        classes = []

        for path, node in tree.filter(ClassDeclaration):
            parsed_class = self._parse_class(node)
            classes.append(parsed_class)

        return classes

    def _parse_class(self, class_node: ClassDeclaration) -> ParsedClass:
        """Parse a class declaration."""
        methods = []
        fields = []

        # Extract fields
        for field_decl in class_node.fields or []:
            for declarator in field_decl.declarators or []:
                fields.append(declarator.name)

        # Extract methods
        for method in class_node.methods or []:
            parsed_method = self._parse_method(method, class_node.name)
            methods.append(parsed_method)

        # Extract constructors
        for constructor in class_node.constructors or []:
            parsed_constructor = self._parse_constructor(constructor, class_node.name)
            methods.append(parsed_constructor)

        return ParsedClass(
            name=class_node.name,
            methods=methods,
            fields=fields,
            line_start=class_node.position.line if class_node.position else None,
            line_end=None,  # javalang doesn't provide end position
        )

    def _parse_method(self, method: MethodDeclaration, class_name: str) -> ParsedMethod:
        """Parse a method declaration."""
        parameters = []
        parameter_types = []

        for param in method.parameters or []:
            parameters.append(param.name)
            param_type = self._get_type_name(param.type)
            parameter_types.append(param_type)

        statements = []
        if method.body:
            statements = self._parse_statements(method.body)

        return ParsedMethod(
            name=method.name,
            class_name=class_name,
            return_type=self._get_type_name(method.return_type) if method.return_type else "void",
            parameters=parameters,
            parameter_types=parameter_types,
            statements=statements,
            line_start=method.position.line if method.position else None,
            line_end=None,
            is_constructor=False,
        )

    def _parse_constructor(self, constructor: ConstructorDeclaration, class_name: str) -> ParsedMethod:
        """Parse a constructor declaration."""
        parameters = []
        parameter_types = []

        for param in constructor.parameters or []:
            parameters.append(param.name)
            param_type = self._get_type_name(param.type)
            parameter_types.append(param_type)

        statements = []
        if constructor.body:
            statements = self._parse_statements(constructor.body)

        return ParsedMethod(
            name=constructor.name,
            class_name=class_name,
            return_type="void",
            parameters=parameters,
            parameter_types=parameter_types,
            statements=statements,
            line_start=constructor.position.line if constructor.position else None,
            line_end=None,
            is_constructor=True,
        )

    def _parse_statements(self, statements: list[Statement]) -> list[ParsedStatement]:
        """Parse a list of statements."""
        parsed = []
        for stmt in statements or []:
            parsed_stmt = self._parse_statement(stmt)
            if parsed_stmt:
                parsed.append(parsed_stmt)
        return parsed

    def _parse_statement(self, stmt: Node) -> ParsedStatement | None:
        """Parse a single statement and extract its structure."""
        if stmt is None:
            return None

        line_num = stmt.position.line if hasattr(stmt, "position") and stmt.position else None
        col_num = stmt.position.column if hasattr(stmt, "position") and stmt.position else None
        code = self._get_code_snippet(line_num) if line_num else ""

        # Extract variables
        vars_defined, vars_used = self._extract_variables(stmt)

        # Determine statement type and parse children
        if isinstance(stmt, IfStatement):
            return self._parse_if_statement(stmt, code, line_num, col_num, vars_defined, vars_used)
        elif isinstance(stmt, WhileStatement):
            return self._parse_while_statement(stmt, code, line_num, col_num, vars_defined, vars_used)
        elif isinstance(stmt, ForStatement):
            return self._parse_for_statement(stmt, code, line_num, col_num, vars_defined, vars_used)
        elif isinstance(stmt, DoStatement):
            return self._parse_do_statement(stmt, code, line_num, col_num, vars_defined, vars_used)
        elif isinstance(stmt, SwitchStatement):
            return self._parse_switch_statement(stmt, code, line_num, col_num, vars_defined, vars_used)
        elif isinstance(stmt, TryStatement):
            return self._parse_try_statement(stmt, code, line_num, col_num, vars_defined, vars_used)
        elif isinstance(stmt, ReturnStatement):
            return ParsedStatement(
                node=stmt,
                statement_type="RETURN",
                code=code,
                line_number=line_num,
                column=col_num,
                variables_defined=vars_defined,
                variables_used=vars_used,
            )
        elif isinstance(stmt, ThrowStatement):
            return ParsedStatement(
                node=stmt,
                statement_type="THROW",
                code=code,
                line_number=line_num,
                column=col_num,
                variables_defined=vars_defined,
                variables_used=vars_used,
            )
        elif isinstance(stmt, BreakStatement):
            return ParsedStatement(
                node=stmt,
                statement_type="BREAK",
                code=code,
                line_number=line_num,
                column=col_num,
                variables_defined=vars_defined,
                variables_used=vars_used,
            )
        elif isinstance(stmt, ContinueStatement):
            return ParsedStatement(
                node=stmt,
                statement_type="CONTINUE",
                code=code,
                line_number=line_num,
                column=col_num,
                variables_defined=vars_defined,
                variables_used=vars_used,
            )
        elif isinstance(stmt, BlockStatement):
            children = self._parse_statements(stmt.statements)
            return ParsedStatement(
                node=stmt,
                statement_type="BLOCK",
                code=code,
                line_number=line_num,
                column=col_num,
                variables_defined=vars_defined,
                variables_used=vars_used,
                children=children,
            )
        elif isinstance(stmt, LocalVariableDeclaration):
            return ParsedStatement(
                node=stmt,
                statement_type="DECLARATION",
                code=code,
                line_number=line_num,
                column=col_num,
                variables_defined=vars_defined,
                variables_used=vars_used,
            )
        elif isinstance(stmt, StatementExpression):
            expr_type = self._get_expression_type(stmt.expression)
            return ParsedStatement(
                node=stmt,
                statement_type=expr_type,
                code=code,
                line_number=line_num,
                column=col_num,
                variables_defined=vars_defined,
                variables_used=vars_used,
            )
        else:
            return ParsedStatement(
                node=stmt,
                statement_type="STATEMENT",
                code=code,
                line_number=line_num,
                column=col_num,
                variables_defined=vars_defined,
                variables_used=vars_used,
            )

    def _parse_if_statement(
        self, stmt: IfStatement, code: str, line_num: int | None,
        col_num: int | None, vars_def: list[str], vars_use: list[str]
    ) -> ParsedStatement:
        """Parse an if statement with its branches."""
        children = []

        # Parse then branch
        if stmt.then_statement:
            if isinstance(stmt.then_statement, BlockStatement):
                children.extend(self._parse_statements(stmt.then_statement.statements))
            else:
                then_parsed = self._parse_statement(stmt.then_statement)
                if then_parsed:
                    children.append(then_parsed)

        # Parse else branch
        if stmt.else_statement:
            if isinstance(stmt.else_statement, BlockStatement):
                children.extend(self._parse_statements(stmt.else_statement.statements))
            else:
                else_parsed = self._parse_statement(stmt.else_statement)
                if else_parsed:
                    children.append(else_parsed)

        return ParsedStatement(
            node=stmt,
            statement_type="IF",
            code=code,
            line_number=line_num,
            column=col_num,
            variables_defined=vars_def,
            variables_used=vars_use,
            children=children,
            metadata={
                "has_else": stmt.else_statement is not None,
                "condition": self._node_to_string(stmt.condition),
            },
        )

    def _parse_while_statement(
        self, stmt: WhileStatement, code: str, line_num: int | None,
        col_num: int | None, vars_def: list[str], vars_use: list[str]
    ) -> ParsedStatement:
        """Parse a while statement."""
        children = []
        if stmt.body:
            if isinstance(stmt.body, BlockStatement):
                children = self._parse_statements(stmt.body.statements)
            else:
                body_parsed = self._parse_statement(stmt.body)
                if body_parsed:
                    children.append(body_parsed)

        return ParsedStatement(
            node=stmt,
            statement_type="WHILE",
            code=code,
            line_number=line_num,
            column=col_num,
            variables_defined=vars_def,
            variables_used=vars_use,
            children=children,
            metadata={"condition": self._node_to_string(stmt.condition)},
        )

    def _parse_for_statement(
        self, stmt: ForStatement, code: str, line_num: int | None,
        col_num: int | None, vars_def: list[str], vars_use: list[str]
    ) -> ParsedStatement:
        """Parse a for statement."""
        children = []
        if stmt.body:
            if isinstance(stmt.body, BlockStatement):
                children = self._parse_statements(stmt.body.statements)
            else:
                body_parsed = self._parse_statement(stmt.body)
                if body_parsed:
                    children.append(body_parsed)

        metadata: dict[str, Any] = {}
        if isinstance(stmt.control, ForControl):
            if stmt.control.condition:
                metadata["condition"] = self._node_to_string(stmt.control.condition)
        elif isinstance(stmt.control, EnhancedForControl):
            metadata["is_enhanced"] = True
            metadata["variable"] = stmt.control.var.name if stmt.control.var else ""

        return ParsedStatement(
            node=stmt,
            statement_type="FOR",
            code=code,
            line_number=line_num,
            column=col_num,
            variables_defined=vars_def,
            variables_used=vars_use,
            children=children,
            metadata=metadata,
        )

    def _parse_do_statement(
        self, stmt: DoStatement, code: str, line_num: int | None,
        col_num: int | None, vars_def: list[str], vars_use: list[str]
    ) -> ParsedStatement:
        """Parse a do-while statement."""
        children = []
        if stmt.body:
            if isinstance(stmt.body, BlockStatement):
                children = self._parse_statements(stmt.body.statements)
            else:
                body_parsed = self._parse_statement(stmt.body)
                if body_parsed:
                    children.append(body_parsed)

        return ParsedStatement(
            node=stmt,
            statement_type="DO_WHILE",
            code=code,
            line_number=line_num,
            column=col_num,
            variables_defined=vars_def,
            variables_used=vars_use,
            children=children,
            metadata={"condition": self._node_to_string(stmt.condition)},
        )

    def _parse_switch_statement(
        self, stmt: SwitchStatement, code: str, line_num: int | None,
        col_num: int | None, vars_def: list[str], vars_use: list[str]
    ) -> ParsedStatement:
        """Parse a switch statement."""
        children = []
        for case in stmt.cases or []:
            case_children = self._parse_statements(case.statements)
            case_stmt = ParsedStatement(
                node=case,
                statement_type="CASE" if case.case else "DEFAULT",
                code=self._node_to_string(case.case) if case.case else "default",
                line_number=case.position.line if case.position else None,
                column=case.position.column if case.position else None,
                variables_defined=[],
                variables_used=[],
                children=case_children,
            )
            children.append(case_stmt)

        return ParsedStatement(
            node=stmt,
            statement_type="SWITCH",
            code=code,
            line_number=line_num,
            column=col_num,
            variables_defined=vars_def,
            variables_used=vars_use,
            children=children,
            metadata={"expression": self._node_to_string(stmt.expression)},
        )

    def _parse_try_statement(
        self, stmt: TryStatement, code: str, line_num: int | None,
        col_num: int | None, vars_def: list[str], vars_use: list[str]
    ) -> ParsedStatement:
        """Parse a try statement."""
        children = []

        # Try block
        if stmt.block:
            try_children = self._parse_statements(stmt.block)
            try_stmt = ParsedStatement(
                node=stmt,
                statement_type="TRY_BLOCK",
                code="try",
                line_number=line_num,
                column=col_num,
                variables_defined=[],
                variables_used=[],
                children=try_children,
            )
            children.append(try_stmt)

        # Catch blocks
        for catch in stmt.catches or []:
            catch_children = self._parse_statements(catch.block)
            catch_vars_def, catch_vars_use = self._extract_variables(catch)
            catch_stmt = ParsedStatement(
                node=catch,
                statement_type="CATCH",
                code=f"catch ({catch.parameter.name})" if catch.parameter else "catch",
                line_number=catch.position.line if catch.position else None,
                column=catch.position.column if catch.position else None,
                variables_defined=catch_vars_def,
                variables_used=catch_vars_use,
                children=catch_children,
            )
            children.append(catch_stmt)

        # Finally block
        if stmt.finally_block:
            finally_children = self._parse_statements(stmt.finally_block)
            finally_stmt = ParsedStatement(
                node=stmt,
                statement_type="FINALLY",
                code="finally",
                line_number=None,
                column=None,
                variables_defined=[],
                variables_used=[],
                children=finally_children,
            )
            children.append(finally_stmt)

        return ParsedStatement(
            node=stmt,
            statement_type="TRY",
            code=code,
            line_number=line_num,
            column=col_num,
            variables_defined=vars_def,
            variables_used=vars_use,
            children=children,
        )

    def _extract_variables(self, node: Node) -> tuple[list[str], list[str]]:
        """Extract defined and used variables from a node."""
        defined: list[str] = []
        used: list[str] = []

        self._extract_variables_recursive(node, defined, used, is_lhs=False)

        return list(set(defined)), list(set(used))

    def _extract_variables_recursive(
        self, node: Node, defined: list[str], used: list[str], is_lhs: bool
    ) -> None:
        """Recursively extract variables from AST nodes."""
        if node is None:
            return

        if isinstance(node, LocalVariableDeclaration):
            for declarator in node.declarators or []:
                defined.append(declarator.name)
                if declarator.initializer:
                    self._extract_variables_recursive(declarator.initializer, defined, used, False)

        elif isinstance(node, Assignment):
            # Left side is a definition
            self._extract_variables_recursive(node.expressionl, defined, used, True)
            # Right side is usage
            self._extract_variables_recursive(node.value, defined, used, False)

        elif isinstance(node, MemberReference):
            if is_lhs:
                defined.append(node.member)
            else:
                used.append(node.member)
            if node.qualifier:
                self._extract_variables_recursive(node.qualifier, defined, used, False)

        elif isinstance(node, MethodInvocation):
            for arg in node.arguments or []:
                self._extract_variables_recursive(arg, defined, used, False)
            if node.qualifier:
                self._extract_variables_recursive(node.qualifier, defined, used, False)

        elif isinstance(node, BinaryOperation):
            self._extract_variables_recursive(node.operandl, defined, used, False)
            self._extract_variables_recursive(node.operandr, defined, used, False)

        elif isinstance(node, TernaryExpression):
            self._extract_variables_recursive(node.condition, defined, used, False)
            self._extract_variables_recursive(node.if_true, defined, used, False)
            self._extract_variables_recursive(node.if_false, defined, used, False)

        elif isinstance(node, ArraySelector):
            self._extract_variables_recursive(node.index, defined, used, False)

        elif isinstance(node, (IfStatement, WhileStatement, DoStatement)):
            self._extract_variables_recursive(node.condition, defined, used, False)

        elif isinstance(node, ForStatement):
            if isinstance(node.control, ForControl):
                if node.control.init:
                    self._extract_variables_recursive(node.control.init, defined, used, False)
                if node.control.condition:
                    self._extract_variables_recursive(node.control.condition, defined, used, False)
                for update in node.control.update or []:
                    self._extract_variables_recursive(update, defined, used, False)
            elif isinstance(node.control, EnhancedForControl):
                if node.control.var:
                    defined.append(node.control.var.name)
                self._extract_variables_recursive(node.control.iterable, defined, used, False)

        elif isinstance(node, ReturnStatement):
            if node.expression:
                self._extract_variables_recursive(node.expression, defined, used, False)

        elif isinstance(node, StatementExpression):
            self._extract_variables_recursive(node.expression, defined, used, False)

        elif isinstance(node, CatchClause):
            if node.parameter:
                defined.append(node.parameter.name)

    def _get_expression_type(self, expr: Node) -> str:
        """Determine the type of an expression."""
        if isinstance(expr, Assignment):
            return "ASSIGNMENT"
        elif isinstance(expr, MethodInvocation):
            return "METHOD_CALL"
        else:
            return "EXPRESSION"

    def _get_type_name(self, type_node: Node) -> str:
        """Get the string representation of a type."""
        if type_node is None:
            return "void"
        if hasattr(type_node, "name"):
            return type_node.name
        return str(type_node)

    def _get_code_snippet(self, line_num: int) -> str:
        """Get code snippet for a line number."""
        if line_num and 0 < line_num <= len(self._source_lines):
            return self._source_lines[line_num - 1].strip()
        return ""

    def _node_to_string(self, node: Node) -> str:
        """Convert a node to a simple string representation."""
        if node is None:
            return ""
        if isinstance(node, MemberReference):
            return node.member
        if isinstance(node, BinaryOperation):
            left = self._node_to_string(node.operandl)
            right = self._node_to_string(node.operandr)
            return f"{left} {node.operator} {right}"
        if hasattr(node, "value"):
            return str(node.value)
        if hasattr(node, "name"):
            return node.name
        return type(node).__name__
