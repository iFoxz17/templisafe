from templisafe.engine.template_engine import TemplateEngine
from templisafe.template.renderer.renderer import Renderer, Rendering
from templisafe.template.template_model import CompilationSpec, VariantSet


class RenderingProvider:
    """Provides `Rendering` instances by delegating to a `Renderer`."""

    __slots__: tuple[str, ...] = ()

    def __init__(self) -> None:
        pass

    def provide_validation(
        self,
        compiled: CompilationSpec,
        variant_set: VariantSet,
        renderer: Renderer,
    ) -> Rendering:
        """
        Perform validation of a compiled template against a set of variants.

        Parameters
        ----------
        compiled : CompilationSpec
            The compiled template to validate.
        variant_set : VariantSet
            The set of variants for parameterization.
        renderer : Renderer
            The renderer responsible for performing validation.

        Returns
        -------
        Rendering
            The result of validation containing diagnostics and outcome.
        """
        return renderer.validate(compiled, variant_set)

    def provide_rendering(
        self,
        compiled: CompilationSpec,
        variant_set: VariantSet,
        engine: TemplateEngine,
        renderer: Renderer,
    ) -> Rendering:
        """
        Render a compiled template against a set of variants using a `TemplateEngine`.

        Parameters
        ----------
        compiled: CompilationSpec
            The compiled template to render.
        variant_set: VariantSet
            The set of variants for parameterization.
        engine: TemplateEngine
            The engine used to process template variables.
        renderer: Renderer
            The renderer responsible for producing the rendered output.

        Returns
        -------
        Rendering
            The fully rendered template, including parameterizations and outcome.
        """
        return renderer.render(compiled, variant_set, engine)
