from unittest.mock import Mock

from templisafe.content.content import Content, ContentType
from templisafe.service.service_orchestrator import ServiceOrchestrator
from templisafe.settings.source.inline_source_settings import InlineSourceSettings
from templisafe.settings.source_executor_settings import SourceExecutorSettings, SourceExecutorStrategy
from templisafe.source.inline_source import InlineSource
from templisafe.task.task import CompilationBundle, Task
from templisafe.template.template_model import Compilation, Outcome


def test_service_orchestrator_runs_single_task_pipeline_in_order() -> None:
    bundle = CompilationBundle(template="hello")
    expected = Compilation(outcome=Outcome.SUCCESS, message="ok")
    order: list[str] = []

    def stage(name: str):
        service = Mock()

        def process(value):
            order.append(name)
            return value

        service.process.side_effect = process
        return service

    resource_service = Mock()

    def process_resource(value):
        order.append("resource")
        return expected

    resource_service.process.side_effect = process_resource

    orchestrator = ServiceOrchestrator(
        source_service=stage("source"),
        data_service=stage("data"),
        config_service=stage("config"),
        settings_service=stage("settings"),
        component_service=stage("component"),
        resource_service=resource_service,
    )

    result = orchestrator.process(Task(bundle=bundle))

    assert result is expected
    assert order == ["source", "data", "config", "settings", "component", "resource"]


def test_service_orchestrator_bootstraps_source_executor_settings_before_main_data_stage() -> None:
    executor_source = InlineSource(InlineSourceSettings(content_type=ContentType.YAML, content="strategy: sequential"))
    bundle = CompilationBundle(template="hello", source_executor_settings=executor_source)
    executor_settings = SourceExecutorSettings(strategy=SourceExecutorStrategy.SEQUENTIAL)
    expected = Compilation(outcome=Outcome.SUCCESS, message="ok")

    source_service = Mock()
    source_service.process.return_value = bundle

    data_service = Mock()
    data_service.process.side_effect = [
        CompilationBundle.model_construct(
            template="",
            source_executor_settings=Content("strategy: sequential", ContentType.YAML),
        ),
        bundle.model_copy(update={"source_executor_settings": executor_settings}),
    ]

    config_service = Mock()
    config_service.process.side_effect = [
        CompilationBundle(template="", source_executor_settings={"strategy": "sequential"}),
        bundle.model_copy(update={"source_executor_settings": executor_settings}),
    ]

    settings_service = Mock()
    settings_service.process.side_effect = [
        CompilationBundle(template="", source_executor_settings=executor_settings),
        bundle.model_copy(update={"source_executor_settings": executor_settings}),
    ]

    component_service = Mock()
    component_service.process.side_effect = lambda value: value

    resource_service = Mock()
    resource_service.process.return_value = expected

    orchestrator = ServiceOrchestrator(
        source_service=source_service,
        data_service=data_service,
        config_service=config_service,
        settings_service=settings_service,
        component_service=component_service,
        resource_service=resource_service,
    )

    result = orchestrator.process(Task(bundle=bundle))

    assert result is expected
    assert data_service.process.call_args_list[0].args[0].template == ""
    assert component_service.process.call_args.args[0].source_executor_settings == executor_settings
