"""Tests for Java parser."""

import pytest

from app.services.java_parser import JavaParser, ParsedClass, ParsedMethod
from app.core.exceptions import JavaParseError, InvalidJavaCodeError


class TestJavaParser:
    """Test cases for JavaParser."""

    def test_parse_simple_class(self, java_parser: JavaParser, simple_java_method: str):
        """Test parsing a simple Java class."""
        classes = java_parser.parse(simple_java_method)

        assert len(classes) == 1
        assert classes[0].name == "Simple"
        assert len(classes[0].methods) == 1

        method = classes[0].methods[0]
        assert method.name == "sum"
        assert method.parameters == ["x", "y"]
        assert method.return_type == "int"

    def test_parse_multiple_methods(self, java_parser: JavaParser, sample_java_code: str):
        """Test parsing class with multiple methods."""
        classes = java_parser.parse(sample_java_code)

        assert len(classes) == 1
        calc_class = classes[0]
        assert calc_class.name == "Calculator"
        assert len(calc_class.methods) == 3

        method_names = [m.name for m in calc_class.methods]
        assert "add" in method_names
        assert "factorial" in method_names
        assert "divide" in method_names

    def test_parse_field_extraction(self, java_parser: JavaParser, sample_java_code: str):
        """Test extracting class fields."""
        classes = java_parser.parse(sample_java_code)

        assert len(classes[0].fields) == 1
        assert "result" in classes[0].fields

    def test_parse_method_parameters(self, java_parser: JavaParser, sample_java_code: str):
        """Test extracting method parameters."""
        classes = java_parser.parse(sample_java_code)

        add_method = next(m for m in classes[0].methods if m.name == "add")
        assert add_method.parameters == ["a", "b"]
        assert add_method.parameter_types == ["int", "int"]

    def test_parse_statements(self, java_parser: JavaParser, simple_java_method: str):
        """Test parsing method statements."""
        classes = java_parser.parse(simple_java_method)
        method = classes[0].methods[0]

        assert len(method.statements) >= 2  # declaration and return

    def test_parse_if_statement(self, java_parser: JavaParser, conditional_java_code: str):
        """Test parsing if statements."""
        classes = java_parser.parse(conditional_java_code)
        abs_method = next(m for m in classes[0].methods if m.name == "abs")

        # Should have if statement
        assert any(s.statement_type == "IF" for s in abs_method.statements)

    def test_parse_for_loop(self, java_parser: JavaParser, loop_java_code: str):
        """Test parsing for loops."""
        classes = java_parser.parse(loop_java_code)
        sum_method = next(m for m in classes[0].methods if m.name == "sumArray")

        # Should have for statement
        has_for = any(s.statement_type == "FOR" for s in sum_method.statements)
        assert has_for

    def test_parse_while_loop(self, java_parser: JavaParser, loop_java_code: str):
        """Test parsing while loops."""
        classes = java_parser.parse(loop_java_code)
        while_method = next(m for m in classes[0].methods if m.name == "whileExample")

        # Should have while statement
        has_while = any(s.statement_type == "WHILE" for s in while_method.statements)
        assert has_while

    def test_parse_try_catch(self, java_parser: JavaParser, sample_java_code: str):
        """Test parsing try-catch blocks."""
        classes = java_parser.parse(sample_java_code)
        divide_method = next(m for m in classes[0].methods if m.name == "divide")

        # Should have try statement
        has_try = any(s.statement_type == "TRY" for s in divide_method.statements)
        assert has_try

    def test_variable_extraction(self, java_parser: JavaParser, simple_java_method: str):
        """Test variable definition and use extraction."""
        classes = java_parser.parse(simple_java_method)
        method = classes[0].methods[0]

        # Find statements with variables
        all_defined = []
        all_used = []
        for stmt in method.statements:
            all_defined.extend(stmt.variables_defined)
            all_used.extend(stmt.variables_used)

        # Should have 'result' as defined
        assert "result" in all_defined

    def test_parse_invalid_java(self, java_parser: JavaParser):
        """Test parsing invalid Java code raises error."""
        invalid_code = "this is not java code {"

        with pytest.raises((JavaParseError, InvalidJavaCodeError)):
            java_parser.parse(invalid_code)

    def test_parse_empty_class(self, java_parser: JavaParser):
        """Test parsing empty class."""
        empty_class = "public class Empty {}"
        classes = java_parser.parse(empty_class)

        assert len(classes) == 1
        assert classes[0].name == "Empty"
        assert len(classes[0].methods) == 0

    def test_parse_constructor(self, java_parser: JavaParser):
        """Test parsing constructor."""
        code = '''
        public class Person {
            private String name;

            public Person(String name) {
                this.name = name;
            }
        }
        '''
        classes = java_parser.parse(code)

        assert len(classes[0].methods) == 1
        constructor = classes[0].methods[0]
        assert constructor.is_constructor
        assert constructor.name == "Person"
