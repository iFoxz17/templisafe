from templisafe.settings.compiler_settings import CompilerSettings
from templisafe.settings.renderer_settings import RendererSettings
from templisafe.settings.template_engine_settings import TemplateEngineSettings


class DefaultHandler:
    __slots__: tuple[str, ...] = (
        "_template_engine_default_settings",
        "_compiler_default_settings",
        "_renderer_default_settings",
    )

    def __init__(
        self,
        template_engine_default_settings: TemplateEngineSettings,
        compiler_default_settings: CompilerSettings,
        renderer_default_settings: RendererSettings,
    ) -> None:
        self._template_engine_default_settings: TemplateEngineSettings = template_engine_default_settings
        self._compiler_default_settings: CompilerSettings = compiler_default_settings
        self._renderer_default_settings: RendererSettings = renderer_default_settings

    def template_engine_settings_or_default(
        self, template_engine_settings: TemplateEngineSettings | None
    ) -> TemplateEngineSettings:
        return template_engine_settings or self._template_engine_default_settings

    def compiler_settings_or_default(self, compiler_settings: CompilerSettings | None) -> CompilerSettings:
        return compiler_settings or self._compiler_default_settings

    def renderer_settings_or_default(self, renderer_settings: RendererSettings | None) -> RendererSettings:
        return renderer_settings or self._renderer_default_settings
