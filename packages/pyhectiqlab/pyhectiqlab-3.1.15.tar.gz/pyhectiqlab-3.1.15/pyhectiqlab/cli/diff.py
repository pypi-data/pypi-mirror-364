import difflib
import typing

import click

"""Source: https://github.com/click-contrib/click-didyoumean/tree/master?tab=MIT-1-ov-file

Under MIT License:

Copyright (c) 2016 Timo Furrer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

class DidYouMean:
    """
    Mixin class for click MultiCommand inherited classes
    to provide git-like *did-you-mean* functionality when
    a certain command is not registered.
    """

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:  # noqa: ANN401
        self.max_suggestions = kwargs.pop("max_suggestions", 4)
        self.cutoff = kwargs.pop("cutoff", 0.5)
        super().__init__(*args, **kwargs)  # type: ignore[call-arg]

    def resolve_command(
        self, ctx: click.Context, args: typing.List[str]
    ) -> typing.Tuple[
        typing.Optional[str], typing.Optional[click.Command], typing.List[str]
    ]:
        """
        Overrides clicks ``resolve_command`` method
        and appends *Did you mean ...* suggestions
        to the raised exception message.
        """
        try:
            return super().resolve_command(ctx, args)  # type: ignore[misc]
        except click.exceptions.UsageError as error:
            error_msg = "‼️  " + str(error)
            original_cmd_name = click.utils.make_str(args[0])
            matches = difflib.get_close_matches(
                original_cmd_name,
                self.list_commands(ctx),  # type: ignore[attr-defined]
                self.max_suggestions,
                self.cutoff,
            )
            if matches:
                fmt_matches = "\n    ".join(matches)
                error_msg += "\n\n"
                error_msg += f"🔍 Did you mean one of these?\n    {fmt_matches}"

            # raise "No such command '%s'." % original_cmd_name
            raise click.exceptions.UsageError(error_msg, error.ctx) from error

class DYMCommandCollection(DidYouMean, click.CommandCollection):
    """
    click CommandCollection to provide git-like
    *did-you-mean* functionality when a certain
    command is not found in the group.
    """