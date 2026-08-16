from templisafe.service.component_service import ComponentService
from templisafe.service.config_service import ConfigService
from templisafe.service.data_service import DataService
from templisafe.service.resource_service import ResourceService
from templisafe.service.settings_service import SettingsService
from templisafe.service.source_service import SourceService
from templisafe.source.source import Source
from templisafe.task.task import BuildBundle, CompilationBundle, RenderingBundle, Task, TaskBundle, TaskType
from templisafe.template.template_model import Build, Compilation, Rendering


class ServiceOrchestrator:
    """Execute validated tasks through the service pipeline."""

    __slots__: tuple[str, ...] = (
        "_source_service",
        "_data_service",
        "_config_service",
        "_settings_service",
        "_component_service",
        "_resource_service",
    )

    def __init__(
        self,
        *,
        source_service: SourceService,
        data_service: DataService,
        config_service: ConfigService,
        settings_service: SettingsService,
        component_service: ComponentService,
        resource_service: ResourceService,
    ) -> None:
        self._source_service = source_service
        self._data_service = data_service
        self._config_service = config_service
        self._settings_service = settings_service
        self._component_service = component_service
        self._resource_service = resource_service

    def process(self, task: Task) -> Compilation | Rendering | Build:
        if task.type is TaskType.BUILD:
            if not isinstance(task.bundle, BuildBundle):
                raise TypeError("Build tasks must contain a BuildBundle")
            return self._build(task.bundle)

        return self._run_single(task.bundle)

    def _run_single(self, bundle: TaskBundle) -> Compilation | Rendering:
        source_bundle = self._source_service.process(bundle)
        source_bundle = self._bootstrap_source_executor_settings(source_bundle)
        data_bundle = self._data_service.process(source_bundle)
        config_bundle = self._config_service.process(data_bundle)
        settings_bundle = self._settings_service.process(config_bundle)
        component_bundle = self._component_service.process(settings_bundle)
        return self._resource_service.process(component_bundle)

    def _bootstrap_source_executor_settings(self, source_bundle: TaskBundle) -> TaskBundle:
        if not isinstance(source_bundle.source_executor_settings, Source):
            return source_bundle

        bootstrap_bundle = CompilationBundle(
            template="",
            source_executor_settings=source_bundle.source_executor_settings,
        )
        data_bundle = self._data_service.process(bootstrap_bundle)
        config_bundle = self._config_service.process(data_bundle)
        settings_bundle = self._settings_service.process(config_bundle)
        return source_bundle.model_copy(update={"source_executor_settings": settings_bundle.source_executor_settings})

    def _build(self, bundle: BuildBundle) -> Build:
        compilation = self._run_single(
            CompilationBundle(
                template=bundle.template,
                schema_=bundle.schema_,
                template_engine=bundle.template_engine,
                source_executor_settings=bundle.source_executor_settings,
                template_parser_settings=bundle.template_parser_settings,
                schema_parser_settings=bundle.schema_parser_settings,
                compiler_settings=bundle.compiler_settings,
            )
        )
        if not isinstance(compilation, Compilation):
            raise TypeError("Build compilation subtask did not return Compilation")

        rendering = self._run_single(
            RenderingBundle(
                compiled=compilation.compiled,
                variants=bundle.variants,
                template_engine=bundle.template_engine,
                source_executor_settings=bundle.source_executor_settings,
                variant_parser_settings=bundle.variant_parser_settings,
                renderer_settings=bundle.renderer_settings,
            )
        )
        if not isinstance(rendering, Rendering):
            raise TypeError("Build rendering subtask did not return Rendering")

        return Build(compilation=compilation, rendering=rendering)
