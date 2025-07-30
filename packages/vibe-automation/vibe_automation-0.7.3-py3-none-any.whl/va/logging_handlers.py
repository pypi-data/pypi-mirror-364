import logging

from va.clients.execution_service_client import append_execution_log


class ExecutionLogHandler(logging.Handler):
    """A logging.Handler that forwards log records to the Execution Service.

    The handler is intended to be attached to the
    per-execution logger that is injected into workflow functions.
    """

    def __init__(self, execution_id: str, level: int = logging.INFO):
        super().__init__(level)
        self.execution_id = execution_id

    def emit(self, record: logging.LogRecord):
        """Send a single LogRecord to the ExecutionService.

        Any errors raised while sending the log are swallowed so that logging
        failures never break the workflow execution.
        """
        # Guard against recursive logging (e.g. logs coming from the execution client itself).
        if record.name.startswith("va.clients"):
            return

        try:
            message = self.format(record)
            # Forward the message to the backend.
            append_execution_log(
                execution_id=self.execution_id,
                description=message,
            )
        except Exception:  # pragma: no cover – best-effort logging
            # Do not crash the workflow because of logging issues
            pass
