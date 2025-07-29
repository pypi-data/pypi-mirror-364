"""Module with errors related to dependency management."""


class DependencyError(Exception):
    """Base error for dependencies."""


class InstallError(DependencyError):
    """Can't install package."""

    def __init__(self, packages: list[str]) -> None:
        """Initialize InstallError.

        Args:
            packages: Packages that failed to be installed
        """
        self.packages = packages
        self.message = (
            f"Error installing package {packages[0]}"
            if len(packages) == 1
            else ("One or more packages failed to install")
        )
        super().__init__(self.message)


class AddError(InstallError):
    """Can't add package to project."""


class SyncError(DependencyError):
    """Can't sync dependencies."""

    def __init__(self) -> None:
        """Initialize SyncError."""
        super().__init__("Could not sync dependencies")


class ResolveError(DependencyError):
    """Can't resolve dependencies."""

    def __init__(self) -> None:
        """Initialize SyncError."""
        super().__init__("Error resolving dependencies")
