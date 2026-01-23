#---------------------------------------------------------------------------------------------
# Source resolution
#---------------------------------------------------------------------------------------------

SourceOrSettings = Union[Source, SourceSettings]

@dataclass(frozen=True, slots=True)
class ResolvedSources:
    template_source: Source | None = None
    schema_source: Source | None = None
    variants_sources: list[Source] | None = None

    template_engine_settings_source: Source | None = None
    source_executor_settings_source: Source | None = None
    template_parser_settings_source: Source | None = None
    schema_parser_settings_source: Source | None = None
    variant_parser_settings_source: Source | None = None
    compiler_settings_source: Source | None = None
    renderer_settings_source: Source | None = None

    @property
    def resolved(self) -> dict[str, Source | list[Source]]:
        """
        Return a mapping of attribute names to their resolved sources,
        including only attributes whose value is not None.
        """
        return {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if getattr(self, field.name) is not None
        }