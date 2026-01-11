from typing import Iterable, Iterator, Any
from enum import IntEnum
from pydantic import BaseModel
from dataclasses import dataclass
import copy

from templisafe.exceptions.binding_error import MissingBindingError
from templisafe.exceptions.parameterization_error import MissingParameterizationError
from templisafe.exceptions.compilation_error import CompilationFailureError
from templisafe.exceptions.rendering_error import RenderingFailureError

#######################################################################################
# Outcome - Diagnostics
#######################################################################################

class Outcome(IntEnum):
    SUCCESS = 0
    WARNING = 1
    ERROR = 2

@dataclass(frozen=True, slots=True)
class Diagnostic:
    """Represents a diagnostic message for a variable in a template."""

    level: Outcome
    message: str
    name: str | None = None
    index: int | None = None

#######################################################################################
# Query Compilation
#######################################################################################

@dataclass(frozen=True, slots=True)
class Schema:
    """Represents the schema of the variables using a pydantic model."""

    model_cls: type[BaseModel]

@dataclass(frozen=True, slots=True)
class Template:
    """Represents a template and its referenced variables."""

    template_str: str
    vars: set[str]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(template_str={self.template_str!r}, vars={self.vars!r})"

@dataclass(frozen=True, slots=True)
class CompilationSpec:
    """Represents a compiled template with its schema."""

    template: Template
    schema: Schema

@dataclass(frozen=True, slots=True)
class Compilation:
    """Contains the result, messages and diagnostics of a compilation."""

    outcome: Outcome
    message: str
    diagnostics: tuple[Diagnostic, ...] = tuple()
    _spec: CompilationSpec | None = None

    @property
    def compiled(self) -> CompilationSpec:
        """Return the compilation specifications object."""
        if self._spec is None:
            raise CompilationFailureError(self)
        return self._spec

#######################################################################################
# Query Rendering
#######################################################################################

@dataclass(frozen=True, slots=True)
class Binding:
    """Represents a value binding for a variable."""

    index: int
    name: str
    value: Any

@dataclass(frozen=True, slots=True)
class Variant:
    """Represents a set of bindings for a template."""

    name: str
    _binding_by_name: dict[str, Binding]

    def __init__(self, name: str, bindings: Iterable[Binding] | None = None) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(
            self, 
            "_binding_by_name", 
            {b.name: b for b in bindings} if bindings else {}
        )

    @property
    def names(self) -> set[str]:
        """Return all bindings names."""
        return set(self._binding_by_name.keys())

    @property
    def bindings(self) -> list[Binding]:
        """Return all bindings objects."""
        return list(self._binding_by_name.values())
    
    @property
    def mapping(self) -> dict[str, Binding]:
        """Return a mapping of the bindings by their name."""
        return copy.deepcopy(self._binding_by_name)

    def get(self, binding_name: str, default: Binding | None = None) -> Binding | None:
        """Return a binding by name or default if not found."""
        return self._binding_by_name.get(binding_name, default)
    
    def __delitem__(self, binding_name: str) -> None:
        if binding_name not in self._binding_by_name:
            raise MissingBindingError(binding_name)
        del self._binding_by_name[binding_name]

    def __getitem__(self, binding_name: str) -> Binding:
        if binding_name not in self._binding_by_name:
            raise MissingBindingError(binding_name)
        return self._binding_by_name[binding_name]

    def __contains__(self, binding_name: str) -> bool:
        return binding_name in self._binding_by_name

    def __iter__(self) -> Iterator[Binding]:
        return iter(self._binding_by_name.values())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(_binding_by_name={self._binding_by_name!r})"
    
@dataclass(frozen=True, slots=True)
class VariantSet:
    """Holds multiple template variants for different parameterizations."""

    variants: list[Variant]

    @property
    def names(self) -> set[str]:
        return set([v.name for v in self.variants])
    
@dataclass(frozen=True, slots=True)
class Parameterization:
    """Holds a variant with its effectively rendered template."""
    variant: Variant
    rendered_str: str

@dataclass(frozen=True, slots=True)
class RenderingSpec:
    """Represents a rendered template with its parameterizations."""

    _param_by_name: dict[str, Parameterization]

    def __init__(self, params: Iterable[Parameterization] | None = None) -> None:
        object.__setattr__(
            self, 
            "_param_by_name", 
            {p.variant.name : p for p in params} if params else {}
        )

    @property
    def names(self) -> set[str]:
        """Return all parameterizations names."""
        return set(self._param_by_name.keys())

    @property
    def parameterizations(self) -> list[Parameterization]:
        """Return all parameterizations objects."""
        return list(self._param_by_name.values())
    
    @property
    def mapping(self) -> dict[str, Parameterization]:
        """Return a mapping of the parameterizations by their name."""
        return copy.deepcopy(self._param_by_name)

    def get(self, binding_name: str, default: Parameterization | None = None) -> Parameterization | None:
        """Return a parameterization by name or default if not found."""
        return self._param_by_name.get(binding_name, default)
    
    def __delitem__(self, binding_name: str) -> None:
        if binding_name not in self._param_by_name:
            raise MissingParameterizationError(binding_name)
        del self._param_by_name[binding_name]

    def __getitem__(self, binding_name: str) -> Parameterization:
        if binding_name not in self._param_by_name:
            raise MissingParameterizationError(binding_name)
        return self._param_by_name[binding_name]

    def __contains__(self, binding_name: str) -> bool:
        return binding_name in self._param_by_name

    def __iter__(self) -> Iterator[Parameterization]:
        return iter(self._param_by_name.values())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(_param_by_name={self._param_by_name!r})"

@dataclass(frozen=True, slots=True)
class Rendering:
    """Contains the outcome, messages and specifications of a template rendering."""

    outcome: Outcome
    message: str
    diagnostics: tuple[Diagnostic, ...] = tuple()
    _spec: RenderingSpec | None = None

    @property
    def rendered(self) -> RenderingSpec:
        """Return the rendering specifications object."""
        if self._spec is None:
            raise RenderingFailureError(self)
        return self._spec


#######################################################################################
# Query Build
#######################################################################################

@dataclass(frozen=True, slots=True)
class Build:
    """Represents the full template build including compilation and rendering results."""

    compilation: Compilation
    rendering: Rendering

    @property
    def outcome(self) -> Outcome:
        """Return the outcome of the build."""
        return max(self.compilation.outcome, self.rendering.outcome)
