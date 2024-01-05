import asyncio
from collections.abc import Sequence
from contextlib import suppress
from functools import partial

import discord
from discord.abc import User
from discord.ext.commands import Context, Paginator
from pydantic import BaseModel

from pydis_core.utils.logging import get_logger
from pydis_core.utils.messages import reaction_check

log = get_logger(__name__)


class PaginationEmojis(BaseModel):
    """The emojis that will be used for pagination."""

    first: str = "\u23EE"
    left: str = "\u2B05"
    right: str = "\u27A1"
    last: str = "\u23ED"
    delete: str = "<:trashcan:637136429717389331>"


class EmptyPaginatorEmbedError(Exception):
    """Raised when attempting to paginate with empty contents."""


class LinePaginator(Paginator):
    """
    A class that aids in paginating code blocks for Discord messages.

    Args:
        pagination_emojis (PaginationEmojis): The emojis used to navigate pages.
        prefix (str): The prefix inserted to every page. e.g. three backticks.
        suffix (str): The suffix appended at the end of every page. e.g. three backticks.
        max_size (int): The maximum amount of codepoints allowed in a page.
        scale_to_size (int): The maximum amount of characters a single line can scale up to.
        max_lines (int): The maximum amount of lines allowed in a page.
    """

    def __init__(
        self,
        prefix: str = "```",
        suffix: str = "```",
        max_size: int = 4000,
        scale_to_size: int = 4000,
        max_lines: int | None = None,
        linesep: str = "\n"
    ) -> None:
        """
        This function overrides the Paginator.__init__ from inside discord.ext.commands.

        It overrides in order to allow us to configure the maximum number of lines per page.
        """
        # Embeds that exceed 4096 characters will result in an HTTPException
        # (Discord API limit), so we've set a limit of 4000
        if max_size > 4000:
            raise ValueError(f"max_size must be <= 4,000 characters. ({max_size} > 4000)")

        super().__init__(
            prefix,
            suffix,
            max_size - len(suffix),
            linesep
        )

        if scale_to_size < max_size:
            raise ValueError(f"scale_to_size must be >= max_size. ({scale_to_size} < {max_size})")

        if scale_to_size > 4000:
            raise ValueError(f"scale_to_size must be <= 4,000 characters. ({scale_to_size} > 4000)")

        self.scale_to_size = scale_to_size - len(suffix)
        self.max_lines = max_lines
        self._current_page = [prefix]
        self._linecount = 0
        self._count = len(prefix) + 1  # prefix + newline
        self._pages = []

    def add_line(self, line: str = "", *, empty: bool = False) -> None:
        """
        Adds a line to the current page.

        If a line on a page exceeds `max_size` characters, then `max_size` will go up to
        `scale_to_size` for a single line before creating a new page for the overflow words. If it
        is still exceeded, the excess characters are stored and placed on the next pages unti
        there are none remaining (by word boundary). The line is truncated if `scale_to_size` is
        still exceeded after attempting to continue onto the next page.

        In the case that the page already contains one or more lines and the new lines would cause
        `max_size` to be exceeded, a new page is created. This is done in order to make a best
        effort to avoid breaking up single lines across pages, while keeping the total length of the
        page at a reasonable size.

        This function overrides the `Paginator.add_line` from inside `discord.ext.commands`.

        It overrides in order to allow us to configure the maximum number of lines per page.

        Args:
            line (str): The line to add to the paginated content.
            empty (bool): Indicates whether an empty line should be added at the end.
        """
        remaining_words = None
        if len(line) > (max_chars := self.max_size - len(self.prefix) - 2):
            if len(line) > self.scale_to_size:
                line, remaining_words = self._split_remaining_words(line, max_chars)
                if len(line) > self.scale_to_size:
                    log.debug("Could not continue to next page, truncating line.")
                    line = line[:self.scale_to_size]

        # Check if we should start a new page or continue the line on the current one
        if self.max_lines is not None and self._linecount >= self.max_lines:
            log.debug("max_lines exceeded, creating new page.")
            self._new_page()
        elif self._count + len(line) + 1 > self.max_size and self._linecount > 0:
            log.debug("max_size exceeded on page with lines, creating new page.")
            self._new_page()

        self._linecount += 1

        self._count += len(line) + 1
        self._current_page.append(line)

        if empty:
            self._current_page.append("")
            self._count += 1

        # Start a new page if there were any overflow words
        if remaining_words:
            self._new_page()
            self.add_line(remaining_words)

    def _new_page(self) -> None:
        """
        Internal: start a new page for the paginator.

        This closes the current page and resets the counters for the new page's line count and
        character count.
        """
        self._linecount = 0
        self._count = len(self.prefix) + 1
        self.close_page()

    def _split_remaining_words(self, line: str, max_chars: int) -> tuple[str, str | None]:
        """
        Internal: split a line into two strings -- reduced_words and remaining_words.

        reduced_words: the remaining words in `line`, after attempting to remove all words that
            exceed `max_chars` (rounding down to the nearest word boundary).

        remaining_words: the words in `line` which exceed `max_chars`. This value is None if
            no words could be split from `line`.

        If there are any remaining_words, an ellipses is appended to reduced_words and a
        continuation header is inserted before remaining_words to visually communicate the line
        continuation.

        Return a tuple in the format (reduced_words, remaining_words).
        """
        reduced_words = []
        remaining_words = []

        # "(Continued)" is used on a line by itself to indicate the continuation of last page
        continuation_header = "(Continued)\n-----------\n"
        reduced_char_count = 0
        is_full = False

        for word in line.split(" "):
            if not is_full:
                if len(word) + reduced_char_count <= max_chars:
                    reduced_words.append(word)
                    reduced_char_count += len(word) + 1
                else:
                    # If reduced_words is empty, we were unable to split the words across pages
                    if not reduced_words:
                        return line, None
                    is_full = True
                    remaining_words.append(word)
            else:
                remaining_words.append(word)

        return (
            " ".join(reduced_words) + "..." if remaining_words else "",
            continuation_header + " ".join(remaining_words) if remaining_words else None
        )

    @classmethod
    async def paginate(
        cls,
        pagination_emojis: PaginationEmojis,
        lines: list[str],
        ctx: Context | discord.Interaction,
        embed: discord.Embed,
        prefix: str = "",
        suffix: str = "",
        max_lines: int | None = None,
        max_size: int = 500,
        scale_to_size: int = 4000,
        empty: bool = True,
        restrict_to_user: User | None = None,
        timeout: int = 300,
        footer_text: str | None = None,
        url: str | None = None,
        exception_on_empty_embed: bool = False,
        reply: bool = False,
        allowed_roles: Sequence[int] | None = None,
    ) -> discord.Message | None:
        """
        Use a paginator and set of reactions to provide pagination over a set of lines.

        The reactions are used to switch page, or to finish with pagination.

        When used, this will send a message using `ctx.send()` and apply a set of reactions to it. These reactions may
        be used to change page, or to remove pagination from the message.

        Pagination will also be removed automatically if no reaction is added for five minutes (300 seconds).

        The interaction will be limited to `restrict_to_user` (ctx.author by default) or
        to any user with a moderation role.

        Args:
            pagination_emojis (PaginationEmojis): The emojis used to navigate pages.
            lines (list[str]): A list of lines to be added to the paginated content.
            ctx (:obj:`discord.ext.commands.Context`): The context in which the pagination is needed.
            embed (:obj:`discord.Embed`): The embed that holds the content, it serves as the page.
            prefix (str): The prefix inserted to every page. e.g. three backticks.
            suffix (str): The suffix appended at the end of every page. e.g. three backticks.
            max_lines (int): The maximum amount of lines allowed in a page.
            max_size (int): The maximum amount of codepoints allowed in a page.
            scale_to_size (int): The maximum amount of characters a single line can scale up to.
            empty (bool): Indicates whether an empty line should be added to each provided line.
            restrict_to_user (:obj:`discord.User`): The user to whom interaction with the pages should be restricted.
            timeout (int): The timeout after which users cannot change pages anymore.
            footer_text (str): Text to be added as a footer for each page.
            url (str): The url to be set for the pagination embed.
            exception_on_empty_embed (bool): Indicates whether to raise an exception when no lines are provided.
            reply (bool): Indicates whether to send the page as a reply to the context's message.
            allowed_roles (Sequence[int]): A list of role ids that are allowed to change pages.

        Example:
        >>> embed = discord.Embed()
        >>> embed.set_author(name="Some Operation", url=url, icon_url=icon)
        >>> await LinePaginator.paginate(pagination_emojis, [line for line in lines], ctx, embed)
        """
        paginator = cls(prefix=prefix, suffix=suffix, max_size=max_size,
                        max_lines=max_lines, scale_to_size=scale_to_size)
        current_page = 0

        if not restrict_to_user:
            if isinstance(ctx, discord.Interaction):
                restrict_to_user = ctx.user
            else:
                restrict_to_user = ctx.author

        if not lines:
            if exception_on_empty_embed:
                log.exception("Pagination asked for empty lines iterable")
                raise EmptyPaginatorEmbedError("No lines to paginate")

            log.debug("No lines to add to paginator, adding '(nothing to display)' message")
            lines.append("*(nothing to display)*")

        for line in lines:
            try:
                paginator.add_line(line, empty=empty)
            except Exception:
                log.exception(f"Failed to add line to paginator: '{line}'")
                raise  # Should propagate
            else:
                log.trace(f"Added line to paginator: '{line}'")

        log.debug(f"Paginator created with {len(paginator.pages)} pages")

        embed.description = paginator.pages[current_page]

        reference = ctx.message if reply else None

        if len(paginator.pages) <= 1:
            if footer_text:
                embed.set_footer(text=footer_text)
                log.trace(f"Setting embed footer to '{footer_text}'")

            if url:
                embed.url = url
                log.trace(f"Setting embed url to '{url}'")

            log.debug("There's less than two pages, so we won't paginate - sending single page on its own")

            if isinstance(ctx, discord.Interaction):
                return await ctx.response.send_message(embed=embed)
            return await ctx.send(embed=embed, reference=reference)

        if footer_text:
            embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
        else:
            embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")
        log.trace(f"Setting embed footer to '{embed.footer.text}'")

        if url:
            embed.url = url
            log.trace(f"Setting embed url to '{url}'")

        log.debug("Sending first page to channel...")

        if isinstance(ctx, discord.Interaction):
            await ctx.response.send_message(embed=embed)
            message = await ctx.original_response()
        else:
            message = await ctx.send(embed=embed, reference=reference)

        log.debug("Adding emoji reactions to message...")

        pagination_emoji = list(pagination_emojis.model_dump().values())

        for emoji in pagination_emoji:
            # Add all the applicable emoji to the message
            log.trace(f"Adding reaction: {emoji!r}")
            await message.add_reaction(emoji)

        check = partial(
            reaction_check,
            message_id=message.id,
            allowed_emoji=pagination_emoji,
            allowed_users=(restrict_to_user.id,),
            allowed_roles=allowed_roles,
        )

        while True:
            try:
                if isinstance(ctx, discord.Interaction):
                    reaction, user = await ctx.client.wait_for("reaction_add", timeout=timeout, check=check)
                else:
                    reaction, user = await ctx.bot.wait_for("reaction_add", timeout=timeout, check=check)
                log.trace(f"Got reaction: {reaction}")
            except asyncio.TimeoutError:
                log.debug("Timed out waiting for a reaction")
                break  # We're done, no reactions for the last 5 minutes

            if str(reaction.emoji) == pagination_emojis.delete:
                log.debug("Got delete reaction")
                return await message.delete()
            if reaction.emoji in pagination_emoji:
                total_pages = len(paginator.pages)
                try:
                    await message.remove_reaction(reaction.emoji, user)
                except discord.HTTPException as e:
                    # Suppress if trying to act on an archived thread.
                    if e.code != 50083:
                        raise e

                if reaction.emoji == pagination_emojis.first:
                    current_page = 0
                    log.debug(f"Got first page reaction - changing to page 1/{total_pages}")
                elif reaction.emoji == pagination_emojis.last:
                    current_page = len(paginator.pages) - 1
                    log.debug(f"Got last page reaction - changing to page {current_page + 1}/{total_pages}")
                elif reaction.emoji == pagination_emojis.left:
                    if current_page <= 0:
                        log.debug("Got previous page reaction, but we're on the first page - ignoring")
                        continue

                    current_page -= 1
                    log.debug(f"Got previous page reaction - changing to page {current_page + 1}/{total_pages}")
                elif reaction.emoji == pagination_emojis.right:
                    if current_page >= len(paginator.pages) - 1:
                        log.debug("Got next page reaction, but we're on the last page - ignoring")
                        continue

                    current_page += 1
                    log.debug(f"Got next page reaction - changing to page {current_page + 1}/{total_pages}")

                embed.description = paginator.pages[current_page]

                if footer_text:
                    embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
                else:
                    embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")

                try:
                    await message.edit(embed=embed)
                except discord.HTTPException as e:
                    if e.code == 50083:
                        # Trying to act on an archived thread, just ignore and abort
                        break
                    raise e

        log.debug("Ending pagination and clearing reactions.")
        with suppress(discord.NotFound):
            try:
                await message.clear_reactions()
            except discord.HTTPException as e:
                # Suppress if trying to act on an archived thread.
                if e.code != 50083:
                    raise e
