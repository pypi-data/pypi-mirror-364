from os import PathLike, path


class NoFilesSelected(UserWarning):
    def __init__(self, folder, message="No file found in folder"):
        self.message = f"{message}: {folder}"
        super().__init__(self.message)

    def __str__(self):
        return repr(self.message)


class FolderNotFound(UserWarning):
    def __init__(self, folder, message="Folder not found"):
        self.message = f"{message}: {folder}"
        super().__init__(self.message)

    def __str__(self):
        return repr(self.message)


class TemporalMisalignment(UserWarning):
    def __init__(
        self,
        folder: str | PathLike,
        list_of_files: list[PathLike],
        message="Possibile temporal misalignment between files",
    ):
        self.message = (
            f"{message} in {folder}: {[path.basename(file) for file in list_of_files]}"
        )
        super().__init__(self.message)

    def __str__(self):
        return repr(self.message)


class SectionNotFound(UserWarning):
    def __init__(self, section: str, sections: list[str]):
        self.message = f"{section} not available. Valid sections: {sections}"
        super().__init__(self.message)

    def __str__(self):
        return repr(self.message)


class DataTypeNotAvailable(UserWarning):
    def __init__(self, requested_type: str, available_types: list[str]):
        self.message = (
            f"'{requested_type}' not available. Valid types: {available_types}"
        )
        super().__init__(self.message)

    def __str__(self):
        return repr(self.message)
