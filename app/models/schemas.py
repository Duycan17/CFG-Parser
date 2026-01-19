"""Pydantic schemas for API request and response models."""

from pydantic import BaseModel, Field

from app.models.graph_models import GraphOutput


class AnalyzeCodeRequest(BaseModel):
    """Request model for analyzing Java code string."""

    code: str = Field(
        ...,
        min_length=1,
        description="Java source code to analyze",
        json_schema_extra={"example": "public class Example { public int add(int a, int b) { return a + b; } }"},
    )
    include_class_graph: bool = Field(
        default=True,
        description="Whether to include class-level graph",
    )
    include_method_graphs: bool = Field(
        default=True,
        description="Whether to include method-level graphs",
    )


class MethodGraph(BaseModel):
    """Graph output for a single method."""

    method_name: str = Field(..., description="Name of the method")
    class_name: str = Field(default="", description="Name of the containing class")
    parameters: list[str] = Field(default_factory=list, description="Method parameters")
    return_type: str = Field(default="void", description="Method return type")
    line_start: int | None = Field(default=None, description="Starting line number")
    line_end: int | None = Field(default=None, description="Ending line number")
    cfg: GraphOutput = Field(default_factory=GraphOutput, description="Control Flow Graph")
    ddg: GraphOutput = Field(default_factory=GraphOutput, description="Data Dependence Graph")


class ClassGraph(BaseModel):
    """Graph output for a class (combined methods)."""

    class_name: str = Field(..., description="Name of the class")
    cfg: GraphOutput = Field(default_factory=GraphOutput, description="Combined Control Flow Graph")
    ddg: GraphOutput = Field(default_factory=GraphOutput, description="Combined Data Dependence Graph")


class AnalyzeResponse(BaseModel):
    """Response model for code analysis."""

    success: bool = Field(default=True, description="Whether analysis was successful")
    source_file: str | None = Field(default=None, description="Source file name if provided")
    class_name: str = Field(default="", description="Main class name")
    method_count: int = Field(default=0, description="Number of methods analyzed")
    method_graphs: list[MethodGraph] = Field(
        default_factory=list, description="Per-method graph outputs"
    )
    class_graph: ClassGraph | None = Field(default=None, description="Class-level graph output")
    errors: list[str] = Field(default_factory=list, description="Any parsing errors encountered")
    warnings: list[str] = Field(default_factory=list, description="Any warnings during analysis")


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    details: str | None = Field(default=None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy")
    version: str = Field(default="1.0.0")
