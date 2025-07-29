class ProjectIncorrectVersionError(Exception):
    pass


class ItemNotFoundError(Exception):
    pass


class NonUniqueNameError(ValueError):
    pass


class NonUniqueUuidError(ValueError):
    pass


class NonUniqueScriptRefError(ValueError):
    pass


class InvalidReferenceError(ValueError):
    pass


class NoRemoteDefined(ValueError):
    pass


class MergeConflict(Exception):
    pass


class NoChangesToCommitError(Exception):
    pass


class ChangesNotCommitedError(Exception):
    pass


class ProjectValidationError(Exception):
    def __init__(self, errors: list[str]):
        Exception.__init__(
            self, "%s errors occurred during load of project" % len(errors)
        )
        self.errors: list[str] = errors
