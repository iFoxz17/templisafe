from typing import Iterable, Iterator, Any
from enum import IntEnum
from dataclasses import dataclass
import copy

from sqltemplater.exceptions.var_error import MissingVarError
from sqltemplater.exceptions.binding_error import MissingBindingError
from sqltemplater.exceptions.parameterization_error import MissingParameterizationError
from sqltemplater.exceptions.compilation_error import CompilationFailureError
from sqltemplater.exceptions.rendering_error import RenderingFailureError

#######################################################################################
# Outcome - Diagnostics
#######################################################################################

class QOutcome(IntEnum):
    SUCCESS = 0
    WARNING = 1
    ERROR = 2

@dataclass(frozen=True, slots=True)
class QDiagnostic:
    """Represents a diagnostic message for a variable in a query."""

    level: QOutcome
    message: str
    name: str | None = None
    index: int | None = None

#######################################################################################
# Query Compilation
#######################################################################################

@dataclass(frozen=True, slots=True)
class QVar:
    """Represents a single query variable and its metadata."""

    index: int
    name: str
    type_: type
    default: Any = None

    @property
    def has_default(self) -> bool:
        return self.default is not None 

@dataclass(frozen=True, slots=True)
class QSchema:
    """Represents a set of query variables (the query schema)."""

    _var_by_name: dict[str, QVar]

    def __init__(self, vars: Iterable[QVar] | None = None) -> None:
        object.__setattr__(
            self, 
            "_var_by_name", 
            {v.name: v for v in vars} if vars else {}
        )

    @property
    def names(self) -> set[str]:
        """Return all parameter names."""
        return set(self._var_by_name.keys())

    @property
    def vars(self) -> list[QVar]:
        """Return all ParamSchema objects."""
        return list(self._var_by_name.values())
    
    @property
    def mapping(self) -> dict[str, QVar]:
        return copy.deepcopy(self._var_by_name)

    def get(self, var_name: str, default: QVar | None = None) -> QVar | None:
        """Return a ParamSchema by name, or default if not found."""
        return self._var_by_name.get(var_name, default)
    
    def __delitem__(self, var_name: str) -> None:
        if var_name not in self._var_by_name:
            raise MissingVarError(var_name)
        del self._var_by_name[var_name]

    def __getitem__(self, var_name: str) -> QVar:
        if var_name not in self._var_by_name:
            raise MissingVarError(var_name)
        return self._var_by_name[var_name]

    def __contains__(self, var_name: str) -> bool:
        return var_name in self._var_by_name

    def __iter__(self) -> Iterator[QVar]:
        return iter(self._var_by_name.values())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(_var_by_name={self._var_by_name!r})"


@dataclass(frozen=True, slots=True)
class QTemplate:
    """Represents a SQL query template and its referenced variables."""

    template: str
    vars: set[str]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(template={self.template!r}, vars={self.vars!r})"

@dataclass(frozen=True, slots=True)
class QCompilationSpec:
    """Represents a compiled query with its template and schema."""

    template: QTemplate
    schema: QSchema

@dataclass(frozen=True, slots=True)
class QCompilation:
    """Contains the result, messages and diagnostics of query compilation."""

    outcome: QOutcome
    message: str
    diagnostics: tuple[QDiagnostic, ...] = tuple()
    _spec: QCompilationSpec | None = None

    @property
    def compiled(self) -> QCompilationSpec:
        if self._spec is None:
            raise CompilationFailureError(self)
        return self._spec

#######################################################################################
# Query Rendering
#######################################################################################

@dataclass(frozen=True, slots=True)
class QBinding:
    """Represents a value binding for a query parameter."""

    index: int
    name: str
    value: Any

@dataclass(frozen=True, slots=True)
class QVariant:
    """Represents a set of bindings for a query variant."""

    name: str
    _binding_by_name: dict[str, QBinding]

    def __init__(self, bindings: Iterable[QBinding] | None = None) -> None:
        object.__setattr__(
            self, 
            "_binding_by_name", 
            {b.name: b for b in bindings} if bindings else {}
        )

    @property
    def names(self) -> set[str]:
        """Return all parameter names."""
        return set(self._binding_by_name.keys())

    @property
    def bindings(self) -> list[QBinding]:
        """Return all ParamSchema objects."""
        return list(self._binding_by_name.values())
    
    @property
    def mapping(self) -> dict[str, QBinding]:
        return copy.deepcopy(self._binding_by_name)

    def get(self, binding_name: str, default: QBinding | None = None) -> QBinding | None:
        """Return a ParamSchema by name, or default if not found."""
        return self._binding_by_name.get(binding_name, default)
    
    def __delitem__(self, binding_name: str) -> None:
        if binding_name not in self._binding_by_name:
            raise MissingBindingError(binding_name)
        del self._binding_by_name[binding_name]

    def __getitem__(self, binding_name: str) -> QBinding:
        if binding_name not in self._binding_by_name:
            raise MissingBindingError(binding_name)
        return self._binding_by_name[binding_name]

    def __contains__(self, binding_name: str) -> bool:
        return binding_name in self._binding_by_name

    def __iter__(self) -> Iterator[QBinding]:
        return iter(self._binding_by_name.values())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(_binding_by_name={self._binding_by_name!r})"
    
@dataclass(frozen=True, slots=True)
class QVariantSet:
    """Holds multiple query variants for different parameterizations."""

    variants: list[QVariant]

    @property
    def names(self) -> set[str]:
        return set([v.name for v in self.variants])
    
@dataclass(frozen=True, slots=True)
class QParameterization:
    """Holds all parameterizations of a rendered query."""
    variant: QVariant
    rendered: str

@dataclass(frozen=True, slots=True)
class QRenderingSpec:
    """Contains the result, messages and diagnostics of query rendering."""

    _param_by_name: dict[str, QParameterization]

    def __init__(self, params: Iterable[QParameterization] | None = None) -> None:
        object.__setattr__(
            self, 
            "_param_by_name", 
            {p.variant.name : p for p in params} if params else {}
        )

    @property
    def names(self) -> set[str]:
        """Return all parameter names."""
        return set(self._param_by_name.keys())

    @property
    def parameterizations(self) -> list[QParameterization]:
        """Return all ParamSchema objects."""
        return list(self._param_by_name.values())
    
    @property
    def mapping(self) -> dict[str, QParameterization]:
        return copy.deepcopy(self._param_by_name)

    def get(self, binding_name: str, default: QParameterization | None = None) -> QParameterization | None:
        """Return a ParamSchema by name, or default if not found."""
        return self._param_by_name.get(binding_name, default)
    
    def __delitem__(self, binding_name: str) -> None:
        if binding_name not in self._param_by_name:
            raise MissingParameterizationError(binding_name)
        del self._param_by_name[binding_name]

    def __getitem__(self, binding_name: str) -> QParameterization:
        if binding_name not in self._param_by_name:
            raise MissingParameterizationError(binding_name)
        return self._param_by_name[binding_name]

    def __contains__(self, binding_name: str) -> bool:
        return binding_name in self._param_by_name

    def __iter__(self) -> Iterator[QParameterization]:
        return iter(self._param_by_name.values())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(_param_by_name={self._param_by_name!r})"

@dataclass(frozen=True, slots=True)
class QRendering:
    """Contains the outcome, messages and specifications of a query rendering."""

    outcome: QOutcome
    message: str
    diagnostics: tuple[QDiagnostic, ...] = tuple()
    _spec: QRenderingSpec | None = None

    @property
    def rendered(self) -> QRenderingSpec:
        if self._spec is None:
            raise RenderingFailureError(self)
        return self._spec


#######################################################################################
# Query Build
#######################################################################################

@dataclass(frozen=True, slots=True)
class QBuild:
    """Represents the full query build including compilation and rendering results."""

    compilation: QCompilation
    rendering: QRendering

    @property
    def outcome(self) -> QOutcome:
        return max(self.compilation.outcome, self.rendering.outcome)
