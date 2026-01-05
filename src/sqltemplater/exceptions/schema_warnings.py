class DefaultParamTypeMismatchWarning(Warning):
    """Warning when a parameter's default value type does not match the expected type."""
    __slots__ = ("p_index", "p_name", "p_type", "default_type")

    def __init__(self, p_index: int, p_name: str, p_type: type, default_type: type) -> None:
        self.p_index = p_index
        self.p_name = p_name
        self.p_type = p_type
        self.default_type = default_type
        message = (
            f"Wrong type for parameter {p_index} ('{p_name}'): "
            f"expecting '{p_type.__name__}', got '{default_type.__name__}'"
        )
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(p_index={self.p_index}, p_name={self.p_name!r}, "
            f"p_type={self.p_type.__name__!r}, default_type={self.default_type.__name__!r})"
        )