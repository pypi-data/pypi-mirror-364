"""The builtin to sync time of NuttX based devices."""

import collections.abc
import datetime

from prompt_toolkit.completion import Completion
from shvcli import Builtin, Builtins, Client, CliItems, State, Tree
from shvcli.tools.complet import comp_path


class BuiltinTimeSync(Builtin):
    """The builtin for time synchronization of ``utcTime`` with local one."""

    def __init__(self, builtins: Builtins, state: State) -> None:
        super().__init__(builtins, state)
        builtins["timesync"] = self

    @property
    def description(self) -> tuple[str, str]:  # noqa: D102
        return "[PATH]", "Synchronize the time of the board with the local time."

    def completion(  # noqa: D102
        self, items: CliItems, client: Client
    ) -> collections.abc.Iterable[Completion]:
        yield from comp_path(items.param, self.state.path, Tree(self.state), "")

    async def completion_async(  # noqa: D102
        self, items: CliItems, client: Client
    ) -> collections.abc.AsyncGenerator[Completion, None]:
        await client.probe(
            items.path_param if items.param.endswith("/") else items.path_param.parent
        )

        async for res in super().completion_async(items, client):
            yield res

    async def run(self, items: CliItems, client: Client) -> None:  # noqa: PLR6301, D102
        path = items.path_param
        if path.name != "utcTime":
            path /= "utcTime"
        got = await client.call(str(path), "get")
        if not isinstance(got, datetime.datetime):
            print(f"Unexpected result of {path}:get: {got}")
            return

        now = datetime.datetime.now(datetime.UTC)
        diff = now - got
        drift = datetime.timedelta(milliseconds=500)
        if not (-drift <= diff <= drift):
            await client.call(str(path), "set", now)
            print(f"Time synchronized. The difference: {diff}")
        else:
            print(
                "Time is syncrhonized withing half a second tolerance. "
                f"The difference: {diff}"
            )
