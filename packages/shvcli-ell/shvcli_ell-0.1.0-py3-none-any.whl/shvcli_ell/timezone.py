"""The builtin to set local time time of NuttX based devices."""

import collections.abc
import pathlib
import zoneinfo

from prompt_toolkit.completion import Completion
from prompt_toolkit.validation import ValidationError
from shvcli import Builtin, Builtins, Client, CliItems, State
from shvcli.file import copy_file
from shvcli.tools.complet import comp_from


class BuiltinTimeSync(Builtin):
    """The builtin for setting local time zone."""

    def __init__(self, builtins: Builtins, state: State) -> None:
        super().__init__(builtins, state)
        builtins["timezone"] = self

    @property
    def description(self) -> tuple[str, str]:  # noqa: D102
        return (
            "[TZ]",
            "Upload the given time zone (or local time zone in default).",
        )

    def completion(  # noqa: PLR6301, D102
        self, items: CliItems, client: Client
    ) -> collections.abc.Iterable[Completion]:
        yield from comp_from(items.param, zoneinfo.available_timezones())

    def validate(self, items: CliItems, client: Client) -> None:  # noqa: D102
        param = items.param
        if param and self._zonefile(items.param) is None:
            raise ValidationError(message=f"No such zoneinfo: {param}")

    async def run(self, items: CliItems, client: Client) -> None:  # noqa: D102
        dest = items.path
        if dest.name != "timeZone":
            dest /= "timeZone"

        param = items.param
        src = self._zonefile(param) if param else pathlib.Path("/etc/localtime")
        if src is not None:
            await copy_file(client, src, dest)
        else:
            print(f"No such zoneinfo: {param}")

    @staticmethod
    def _zonefile(param: str) -> pathlib.Path | None:
        for tzpath in map(pathlib.Path, zoneinfo.TZPATH):
            path = tzpath / param
            if path.is_file():
                return path
        return None
