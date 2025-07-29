class CronEventError(Exception):
    """
    Exception for cron event errors.
    """


class CronEventSyntaxError(CronEventError):
    """
    Exception for cron event syntax errors.
    """


class CronEventValidationError(CronEventError):
    """
    Exception for cron event validation errors.
    """


class CronEventValueError(CronEventError):
    """
    Exception for cron event value errors.
    """
