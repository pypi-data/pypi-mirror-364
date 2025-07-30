import logging

from snakestack.logging.contexts import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self: "RequestIdFilter", record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True

class ExcludeLoggerFilter(logging.Filter):
    def __init__(self: "ExcludeLoggerFilter", excluded_name: list[str]) -> None:
        super().__init__()
        self.excluded = set(excluded_name)

    def filter(self: "ExcludeLoggerFilter", record: logging.LogRecord) -> bool:
        return record.name not in self.excluded
