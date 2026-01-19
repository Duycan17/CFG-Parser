"""API dependencies for dependency injection."""

from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.java_parser import JavaParser
from app.services.cfg_builder import CFGBuilder
from app.services.ddg_builder import DDGBuilder
from app.services.graph_converter import GraphConverter


def get_java_parser() -> JavaParser:
    """Get Java parser instance."""
    return JavaParser()


def get_cfg_builder() -> CFGBuilder:
    """Get CFG builder instance."""
    return CFGBuilder()


def get_ddg_builder() -> DDGBuilder:
    """Get DDG builder instance."""
    return DDGBuilder()


def get_graph_converter() -> GraphConverter:
    """Get graph converter instance."""
    return GraphConverter()


# Type aliases for dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
JavaParserDep = Annotated[JavaParser, Depends(get_java_parser)]
CFGBuilderDep = Annotated[CFGBuilder, Depends(get_cfg_builder)]
DDGBuilderDep = Annotated[DDGBuilder, Depends(get_ddg_builder)]
GraphConverterDep = Annotated[GraphConverter, Depends(get_graph_converter)]
