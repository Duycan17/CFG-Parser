"""API routes for Java code analysis."""

from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.dependencies import (
    SettingsDep,
    JavaParserDep,
    CFGBuilderDep,
    DDGBuilderDep,
    GraphConverterDep,
)
from app.core.exceptions import (
    JavaParseError,
    InvalidJavaCodeError,
    CFGBuildError,
    DDGBuildError,
    FileTooLargeError,
)
from app.models.schemas import (
    AnalyzeCodeRequest,
    AnalyzeResponse,
    MethodGraph,
    ClassGraph,
    ErrorResponse,
    HealthResponse,
)
from app.models.graph_models import GraphOutput


router = APIRouter(tags=["analysis"])


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: SettingsDep) -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=settings.api_version)


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid Java code"},
        422: {"model": ErrorResponse, "description": "Parsing error"},
    },
)
async def analyze_code(
    request: AnalyzeCodeRequest,
    parser: JavaParserDep,
    cfg_builder: CFGBuilderDep,
    ddg_builder: DDGBuilderDep,
    converter: GraphConverterDep,
    settings: SettingsDep,
) -> AnalyzeResponse:
    """Analyze Java code string and generate CFG/DDG.

    Returns control flow graphs and data dependence graphs for each method,
    plus optional class-level combined graphs. Output is formatted for
    transformer model input.
    """
    # Validate code length
    if len(request.code) > settings.max_code_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Code exceeds maximum length of {settings.max_code_length} characters",
        )

    return await _analyze_java_code(
        code=request.code,
        include_method_graphs=request.include_method_graphs,
        include_class_graph=request.include_class_graph,
        parser=parser,
        cfg_builder=cfg_builder,
        ddg_builder=ddg_builder,
        converter=converter,
    )


@router.post(
    "/analyze/file",
    response_model=AnalyzeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file or code"},
        413: {"model": ErrorResponse, "description": "File too large"},
        422: {"model": ErrorResponse, "description": "Parsing error"},
    },
)
async def analyze_file(
    file: Annotated[UploadFile, File(description="Java source file to analyze")],
    parser: JavaParserDep,
    cfg_builder: CFGBuilderDep,
    ddg_builder: DDGBuilderDep,
    converter: GraphConverterDep,
    settings: SettingsDep,
    include_class_graph: Annotated[bool, Form()] = True,
    include_method_graphs: Annotated[bool, Form()] = True,
) -> AnalyzeResponse:
    """Analyze uploaded Java file and generate CFG/DDG.

    Accepts a .java file upload and returns control flow graphs and
    data dependence graphs in transformer-ready formats.
    """
    # Validate file type
    if not file.filename or not file.filename.endswith(".java"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a Java source file (.java)",
        )

    # Read file content
    content = await file.read()

    # Check file size
    max_size = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_file_size_mb}MB",
        )

    try:
        code = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be UTF-8 encoded",
        )

    response = await _analyze_java_code(
        code=code,
        include_method_graphs=include_method_graphs,
        include_class_graph=include_class_graph,
        parser=parser,
        cfg_builder=cfg_builder,
        ddg_builder=ddg_builder,
        converter=converter,
    )

    response.source_file = file.filename
    return response


async def _analyze_java_code(
    code: str,
    include_method_graphs: bool,
    include_class_graph: bool,
    parser: JavaParserDep,
    cfg_builder: CFGBuilderDep,
    ddg_builder: DDGBuilderDep,
    converter: GraphConverterDep,
) -> AnalyzeResponse:
    """Internal function to analyze Java code."""
    errors: list[str] = []
    warnings: list[str] = []
    method_graphs: list[MethodGraph] = []
    class_graph: ClassGraph | None = None
    class_name = ""

    try:
        # Parse Java code
        parsed_classes = parser.parse(code)

        if not parsed_classes:
            raise InvalidJavaCodeError("No classes found in the provided code")

        # Process each class
        for parsed_class in parsed_classes:
            class_name = parsed_class.name

            # Build method-level graphs
            if include_method_graphs:
                for method in parsed_class.methods:
                    try:
                        method_graph = _build_method_graph(
                            method=method,
                            class_name=parsed_class.name,
                            cfg_builder=cfg_builder,
                            ddg_builder=ddg_builder,
                            converter=converter,
                        )
                        method_graphs.append(method_graph)
                    except (CFGBuildError, DDGBuildError) as e:
                        errors.append(f"Error processing method {method.name}: {e.message}")

            # Build class-level graph
            if include_class_graph:
                try:
                    class_graph = _build_class_graph(
                        parsed_class=parsed_class,
                        cfg_builder=cfg_builder,
                        ddg_builder=ddg_builder,
                        converter=converter,
                    )
                except (CFGBuildError, DDGBuildError) as e:
                    errors.append(f"Error building class graph: {e.message}")

        return AnalyzeResponse(
            success=True,
            class_name=class_name,
            method_count=len(method_graphs),
            method_graphs=method_graphs,
            class_graph=class_graph,
            errors=errors,
            warnings=warnings,
        )

    except JavaParseError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Java parsing error: {e.message}",
        )
    except InvalidJavaCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Java code: {e.message}",
        )


def _build_method_graph(
    method,
    class_name: str,
    cfg_builder: CFGBuilderDep,
    ddg_builder: DDGBuilderDep,
    converter: GraphConverterDep,
) -> MethodGraph:
    """Build CFG and DDG for a single method."""
    # Build CFG
    cfg_graph, cfg_nodes, cfg_edges = cfg_builder.build_method_cfg(method)
    cfg_output = converter.convert(cfg_graph, cfg_nodes, cfg_edges)

    # Build DDG
    ddg_graph, ddg_nodes, ddg_edges = ddg_builder.build_method_ddg(method, cfg_nodes)
    ddg_output = converter.convert(ddg_graph, ddg_nodes, ddg_edges)

    return MethodGraph(
        method_name=method.name,
        class_name=class_name,
        parameters=method.parameters,
        return_type=method.return_type,
        line_start=method.line_start,
        line_end=method.line_end,
        cfg=cfg_output,
        ddg=ddg_output,
    )


def _build_class_graph(
    parsed_class,
    cfg_builder: CFGBuilderDep,
    ddg_builder: DDGBuilderDep,
    converter: GraphConverterDep,
) -> ClassGraph:
    """Build combined CFG and DDG for a class."""
    # Build class-level CFG
    cfg_graph, cfg_nodes, cfg_edges = cfg_builder.build_class_cfg(parsed_class)
    cfg_output = converter.convert(cfg_graph, cfg_nodes, cfg_edges)

    # Build class-level DDG
    ddg_graph, ddg_nodes, ddg_edges = ddg_builder.build_class_ddg(parsed_class, cfg_nodes)
    ddg_output = converter.convert(ddg_graph, ddg_nodes, ddg_edges)

    return ClassGraph(
        class_name=parsed_class.name,
        cfg=cfg_output,
        ddg=ddg_output,
    )
