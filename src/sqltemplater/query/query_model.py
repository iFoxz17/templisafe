from typing import Iterable, Iterator, Any
from enum import IntEnum
from dataclasses import dataclass
import copy

from sqltemplater.exceptions.param_error import MissingParamError


@dataclass(frozen=True, slots=True)
class ParamSchema:
    """Represents a single parameter in a query schema."""
    index: int
    name: str
    type_: type
    default: Any = None

    @property
    def has_default(self) -> bool:
        return self.default is not None 

@dataclass(frozen=True, slots=True)
class QuerySchema:
    """Represents a schema for query parameters with fast lookup by name."""
    _params: dict[str, ParamSchema]

    def __init__(self, params: Iterable[ParamSchema] | None = None) -> None:
        object.__setattr__(
            self, 
            "_params", 
            {p.name: p for p in params} if params else {}
        )

    @property
    def names(self) -> set[str]:
        """Return all parameter names."""
        return set(self._params.keys())

    @property
    def params(self) -> list[ParamSchema]:
        """Return all ParamSchema objects."""
        return list(self._params.values())
    
    @property
    def params_map(self) -> dict[str, ParamSchema]:
        return copy.deepcopy(self._params)

    def param(self, name: str, default: ParamSchema | None = None) -> ParamSchema | None:
        """Return a ParamSchema by name, or default if not found."""
        return self._params.get(name, default)
    
    def add_param(self, param: ParamSchema) -> None:
        """Add a new ParamSchema to the schema."""
        self._params[param.name] = param

    def __delitem__(self, name: str) -> None:
        if name not in self._params:
            raise MissingParamError(name)
        del self._params[name]

    def __getitem__(self, name: str) -> ParamSchema:
        if name not in self._params:
            raise MissingParamError(name)
        return self._params[name]

    def __contains__(self, name: str) -> bool:
        return name in self._params

    def __iter__(self) -> Iterator[ParamSchema]:
        return iter(self._params.values())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(params={self.params!r})"


@dataclass(frozen=True, slots=True)
class QueryTemplate:
    """Wrapper for a Jinja SQL template."""
    template: str
    params: set[str]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(template={self.template!r}, params={self.params!r})"

@dataclass(frozen=True, slots=True)
class CompiledQuery:
    """Represents a compiled query with its template and optional schema."""
    template: QueryTemplate
    schema: QuerySchema

@dataclass(frozen=True, slots=True)
class QueryParam:
    """Holds the actual value of parameter."""
    index: int
    name: str
    value: Any

@dataclass(frozen=True, slots=True)
class QueryParams:
    """Holds the actual parameter values for a query."""

    def __init__(self, params: Iterable[QueryParam] | None = None) -> None:
        object.__setattr__(
            self, 
            "params", 
            [p for p in params] if params else []
        )

    params: list[QueryParam]

    @property
    def params_map(self) -> dict[str, Any]:
        return {p.name: p.value for p in self.params}
    
    def __iter__(self) -> Iterator[QueryParam]:
        return iter(self.params)
    
@dataclass(frozen=True, slots=True)
class QueryParameterization:
    """Holds multiple QueryParams for different query parameterizations."""
    parameterizations: dict[str, QueryParams]

    @property
    def names(self) -> set[str]:
        return set(self.parameterizations.keys())
    
    @property
    def parameters(self) -> set[QueryParams]:
        return set(self.parameterizations.values())

class BuildOutcome(IntEnum):
    SUCCESS = 0
    WARNING = 1
    ERROR = 2

@dataclass(frozen=True, slots=True)
class BuildDiagnostic:
    level: BuildOutcome
    message: str
    param: str | None = None
    index: int | None = None

@dataclass(frozen=True, slots=True)
class RenderedQuery:
    compiled: CompiledQuery
    parameterization: QueryParameterization
    rendered: list[str]
    diagnostics: tuple[BuildDiagnostic, ...] = tuple()

@dataclass(frozen=True, slots=True)
class CompilationResult:
    outcome: BuildOutcome
    message: str
    compiled_query: CompiledQuery | None = None
    diagnostics: tuple[BuildDiagnostic, ...] = tuple()

@dataclass(frozen=True, slots=True)
class RenderingResult:
    outcome: BuildOutcome
    message: str
    rendered_query: RenderedQuery | None = None

@dataclass(frozen=True, slots=True)
class BuildResult:
    compilation: CompilationResult
    rendering: RenderingResult

    @property
    def outcome(self) -> BuildOutcome:
        return max(self.compilation.outcome, self.rendering.outcome)
