from typing import Any
from abc import ABC, abstractmethod
from pydantic import BaseModel, model_validator, Field

from sqltemplater.loader.parser import Parser
from sqltemplater.settings.parser.params_parser_settings import ParamsParserSettings
from sqltemplater.settings.parser.parser_settings import ParserSettings
from sqltemplater.query.query_model import QueryParameterization, QueryParams, QueryParam
from sqltemplater.exceptions.params_error import IllegalParamsError, DuplicatedParamError

class ParameterizationsModel(BaseModel):
    """Accepts either a single parameterization or multiple ones."""
    parameterizations: dict[str, dict[str, Any]] = Field(default_factory=dict)
    default_name: str

    @model_validator(mode="before")
    def normalize_parameterizations(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            raise TypeError("No dict provided")
        
        input_data = values.get("parameterizations", {})
        default_name = values.get("default_name", "default")

        if not isinstance(input_data, dict):
            raise TypeError("parameterizations must be a dict")

        # Detect if it's a single parameterization (values are not dicts)
        if all(not isinstance(v, dict) for v in input_data.values()):
            values["parameterizations"] = {default_name: input_data}
        # If it's already dict of dicts, leave as is
        elif all(isinstance(v, dict) for v in input_data.values()):
            values["parameterizations"] = input_data
        else:
            raise TypeError("Mixed types in parameterizations dict are not allowed")

        return values

class ParamsParser(Parser, ABC):
    """
    Abstract base class for parsing and validating parameters.
    """

    __slots__ = ('_settings')
    
    def __init__(self, settings: ParamsParserSettings) -> None:
        super().__init__(settings)
       
    def _parse(self, p_index: int, p_name: str, p_value: Any) -> QueryParam:
        return QueryParam(index=p_index, name=p_name, value=p_value)
        
    def _parse_params(self, params_def_dict: dict[str, Any]) -> QueryParameterization:
        settings: ParserSettings = self._settings
        assert isinstance(settings, ParamsParserSettings)
        
        params_key: str = settings.params_key
        if params_key not in params_def_dict:
            raise IllegalParamsError(f"Missing top-level params key '{params_key}'")
        
        params_context_dict: Any = params_def_dict[params_key]
        if not isinstance(params_context_dict, dict):
            raise IllegalParamsError(f'Illegal params definition')
        
        parameterization_models: ParameterizationsModel
        try:
            parameterization_models = ParameterizationsModel(
                parameterizations=params_context_dict,
                default_name=settings.default_parameterization_name
            )
        except Exception as e:
            raise IllegalParamsError(f'Illegal params definition') from e 

        parameterizations: dict[str, QueryParams] = {}

        for (name, params_dict) in parameterization_models.parameterizations.items():
            params: dict[str, QueryParam] = {}

            for i, (p_name, p_value) in enumerate(params_dict.items()):
                if not isinstance(p_name, str):
                    raise IllegalParamsError(f'Illegal definition of parameter {i}: {p_name} is not a string')
                query_param: QueryParam = self._parse(i, p_name, p_value)
                
                if p_name in params:        # This should never happen since dict cannot have duplicated keys
                    raise DuplicatedParamError(p_name, params[p_name].index, i)
                params[p_name] = query_param

            parameterizations[name] = QueryParams(params.values())

        return QueryParameterization(parameterizations)
    
    @abstractmethod
    def _parse_raw(self, params: str) -> dict[str, Any]:
        pass

    def parse(self, params: str) -> QueryParameterization:
        return self._parse_params(self._parse_raw(params))
        
