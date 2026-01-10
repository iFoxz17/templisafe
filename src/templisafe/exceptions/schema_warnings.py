class DefaultVarTypeMismatchWarning(Warning):
    """Warning when a variable's default value type does not match the expected type."""
    
    __slots__: tuple[str, ...] = ("v_index", "v_name", "v_type", "default_type")

    def __init__(self, v_index: int, v_name: str, v_type: type, default_type: type) -> None:
        self.v_index = v_index
        self.v_name = v_name
        self.v_type = v_type
        self.default_type = default_type
        message = (
            f"Wrong type for variable {v_name}: "
            f"expecting '{v_type.__name__}', got '{default_type.__name__}'"
        )
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(v_index={self.v_index}, v_name={self.v_name!r}, "
            f"v_type={self.v_type.__name__!r}, default_type={self.default_type.__name__!r})"
        )