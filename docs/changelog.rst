.. See docs for details on formatting your entries
   https://releases.readthedocs.io/en/latest/concepts.html

Changelog
=========

- :release:`11.3.0 <17th July 2024>`
- :feature:`254` Add a ``py.typed`` file for :literal-url:`PEP 561 <https://peps.python.org/pep-0561/>` compliance.


- :release:`11.2.0 <22nd June 2024>`
- :support:`244` Bump Discord.py to :literal-url:`2.4.0 <https://github.com/Rapptz/discord.py/releases/tag/v2.4.0>`.

- :release:`11.1.0 <30th March 2024>`
- :support:`210` Drop the restriction that meant fakeredis could not be installed on Python 3.12 as lupa now supports 3.12

- :release:`11.0.1 <20th March 2024>`
- :bug:`209` Extract original error from :obj:`discord.ext.commands.errors.CommandInvokeError` before handling it.

- :release:`11.0.0 <18th March 2024>`
- :breaking:`208` Split ``fakeredis`` optional dependency from the ``async-rediscache`` extra. You can now install with ``[fakeredis]`` to just install fakeredis (with lua support), ``[async-rediscache]`` to install just ``async-rediscache``, or use either ``[all]`` or ``[async-rediscache,fakeredis]`` to install both. This allows users who do no rely on fakeredis to install in 3.12 environments.
- :support:`208` Add support for Python 3.12. Be aware, at time of writing, our usage of fakeredis does not currently support 3.12. This is due to :literal-url:`this lupa issue<https://github.com/scoder/lupa/issues/245>`. Lupa is required by async-rediscache for lua script support within fakeredis. As such, fakeredis can not be installed in a Python 3.12 environment.
- :breaking:`208` Drop support for Python 3.10
- :breaking:`208` Drop support for Pydantic 1.X
- :support:`208` Bump ruff to 0.3.0 and target Python 3.11 now that 3.10 isn't supported.
- :breaking:`207` Enable more ruff linting rules. See :literal-url:`GitHub release notes <https://github.com/python-discord/bot-core/releases/tag/v11.0.0>` for breaking changes.
- :support:`206` Bump ruff from 0.1.15 to 0.2.2, using the new lint config namespace, and linting with the new rules.
- :feature:`205` Add :obj:`pydis_core.utils.error_handling.commands.abc.AbstractCommandErrorHandler` and :obj:`pydis_core.utils.error_handling.commands.manager.CommandErrorManager` to implement and register command error handlers independantly.
- :support:`204` Document the instance attributes of :obj:`pydis_core.BotBase`.

- :release:`10.7.0 <30th January 2024>`
- :feature:`158` Add locking utilities for controlling concurrency logic
- :support:`202` Bump various development dependencies and CI workflow action versions
- :feature:`194` Add the :obj:`pydis_core.utils.interactions.user_has_access` helper function, that returns whether the given user is in the allowed_users list, or has a role from allowed_roles.

- :release:`10.6.0 <30th January 2024>`
- :feature:`189` Add :obj:`pydis_core.utils.pagination.LinePaginator` which allows users to paginate over content using Embeds, with emoji reactions facilitating navigation.
- :feature:`189` Add :obj:`pydis_core.utils.messages.reaction_check`, a predicate that dictates whether a user has the right to add a specific set of reactions based on certain criteria.
- :feature:`199` Port common discord.commands checks from other bots to :obj:`pydis_core.utils.checks`.

- :release:`10.5.1 <14th December 2023>`
- :bug:`200` Do not attempt to read response body if the HTTP response code is 204. Previously only :obj:`pydis_core.site_api.APIClient.delete` did this.

- :release:`10.5.0 <10th December 2023>`
- :support:`197` Mark dependencies using tilde version specifiers. This is to allow user of pydis core to use newer versions of these libraries without us having to cut a new release.

- :release:`10.4.0 <26th October 2023>`
- :support:`196` Bump aiodns to :literal-url:`3.1.1 <https://github.com/saghul/aiodns/releases/tag/v3.1.1>`.
- :support:`196` Bump many development dependencies.


- :release:`10.3.0 <19th September 2023>`
- :feature:`195` Add `log_format` to `pydis_core.utils.logging` to allow for standardised logging across all services using pydis_core.
- :feature:`195` Set `discord`, `websockets`, `chardet` & `async_rediscache` loggers to warning level and `asyncio` to info level by default.


- :release:`10.2.0 <28th August 2023>`
- :support:`192` Bump Discord.py to :literal-url:`2.3.2 <https://github.com/Rapptz/discord.py/releases/tag/v2.3.2>`.


- :release:`10.1.0 <25th July 2023>`
- :feature:`190` Overwrite :obj:`discord.ext.commands.Bot.process_commands` to ensure no commands are processed until all extensions are loaded. This only works for clients using :obj:`pydis_core.BotBase.load_extensions`.


- :release:`10.0.0 <14th July 2023>`
- :breaking:`188` Support sending multiple files at once to paste service. All calls to :obj:`pydis_core.utils.paste_service.send_to_paste_service` must now provide a list of :obj:`pydis_core.utils.paste_service.PasteFile`.
- :bug:`187 major` Fix :obj:`pydis_core.utils.channel.get_or_fetch_channel`'s return type to include :obj:`discord.abc.PrivateChannel` and :obj:`discord.Thread`.
- :feature:`184` Remove the message stored in the ``message`` attr of :obj:`pydis_core.utils.interactions.ViewWithUserAndRoleCheck` when the interaction is stopped, in additional to the exist logic for timeout.
- :support:`184` Bump Discord.py to :literal-url:`2.3.1 <https://github.com/Rapptz/discord.py/releases/tag/v2.3.1>`.


- :release:`9.9.2 <2nd July 2023>`
- :bug:`185` Update expiry label from 1 month to 30 days in paste service.


- :release:`9.9.1 <22nd June 2023>`
- :bug:`183` Push the correct changeset to pypi.


- :release:`9.9.0 <18th June 2023>`
- :feature:`182` Default pastebin url to https://paste.pythondiscord.com.
- :feature:`182` Add supported lexer validation to paste service.


- :release:`9.8.0 <13th June 2023>`
- :support:`181` Bump Discord.py to :literal-url:`2.3.0 <https://github.com/Rapptz/discord.py/releases/tag/v2.3.0>`.


- :release:`9.7.0 <10th June 2023>`
- :feature:`179` Add paste service utility to upload text to our paste service.
- :feature:`177` Automatically handle discord.Forbidden 90001 errors in all schedules.
- :feature:`176` Migrate repo to use ruff for linting.


- :release:`9.6.0 <6th May 2023>`
- :feature:`175` Log when waiting for the guild to be available before loading cogs.
- :support:`175` Bump Discord.py to :literal-url:`2.2.3 <https://github.com/Rapptz/discord.py/releases/tag/v2.2.3>`.


- :release:`9.5.1 <2nd March 2023>`
- :bug:`174` Bump Discord.py to :literal-url:`2.2.2 <https://github.com/Rapptz/discord.py/releases/tag/v2.2.2>`.


- :release:`9.5.0 <28th February 2023>`
- :feature:`173` Bump Discord.py to :literal-url:`2.2.0 <https://github.com/Rapptz/discord.py/releases/tag/v2.2.0>`.


- :release:`9.4.1 <9th February 2023>`
- :bug:`172` Bump Discord.py to :literal-url:`2.1.1 <https://github.com/Rapptz/discord.py/releases/tag/v2.1.1>`.


- :release:`9.4.0 <24th December 2022>`
- :feature:`171` Sync all app commands after extensions have been loaded. This release also removes the need to run :obj:`pydis_core.BotBase.load_extensions` in a task.


- :release:`9.3.1 <23rd December 2022>`
- :bug:`170` Save references of newly created tasks in :obj:`pydis_core.utils.scheduling`.

- :release:`9.3.0 <13th December 2022>`
- :feature:`169` Return :obj:`None` upon receiving a bad request from Discord in :obj:`pydis_core.utils.members.get_or_fetch_member`.

- :release:`9.2.0 <17th November 2022>`
- :support:`151` Add support for Python 3.11.

- :release:`9.1.1 <14th November 2022>`
- :bug:`162` Handle not being able to delete the interaction message on button press/timeout.


- :release:`9.1.0 <13th November 2022>`
- :feature:`158` Bump Discord.py to :literal-url:`2.1.0 <https://github.com/Rapptz/discord.py/releases/tag/v2.1.0>`.
- :feature:`88` Add a decorator that stops successive duplicate invocations of commands.


- :release:`9.0.0 <5th November 2022>`
- :breaking:`157` Rename project to pydis_core to allow for publishing to pypi.


- :release:`8.2.1 <18th September 2022>`
- :bug:`138` Bump Discord.py to :literal-url:`2.0.1 <https://discordpy.readthedocs.io/en/latest/whats_new.html#v2-0-1>`.


- :release:`8.2.0 <18th August 2022>`
- :support:`125` Bump Discord.py to the stable :literal-url:`2.0 release <https://discordpy.readthedocs.io/en/latest/migrating.html>`.


- :release:`8.1.0 <16th August 2022>`
- :support:`124` Updated :obj:`pydis_core.utils.regex.DISCORD_INVITE` regex to optionally match leading "http[s]" and "www".


- :release:`8.0.0 <27th July 2022>`
- :breaking:`110` Bump async-rediscache to v1.0.0-rc2.
- :support:`108` Bump Python version to 3.10.*.
- :bug:`107 major` Declare aiodns as a project dependency.
- :support:`107` Add a sample project with boilerplate and documentation explaining how to develop for bot-core.


- :release:`7.5.0 <23rd July 2022>`
- :feature:`101` Add a utility to clean a string or referenced message's content.


- :release:`7.4.0 <17th July 2022>`
- :feature:`106` Add an optional ``message`` attr to :obj:`pydis_core.utils.interactions.ViewWithUserAndRoleCheck`. On view timeout, this message has its view removed if set.


- :release:`7.3.1 <16th July 2022>`
- :bug:`104` Fix :obj:`pydis_core.utils.interactions.DeleteMessageButton` not working due to using wrong delete method.


- :release:`7.3.0 <16th July 2022>`
- :feature:`103` Add a generic view :obj:`pydis_core.utils.interactions.ViewWithUserAndRoleCheck` that only allows specified users and roles to interaction with it.
- :feature:`103` Add a button :obj:`pydis_core.utils.interactions.DeleteMessageButton` that deletes the message attached to its parent view.


- :release:`7.2.2 <9th July 2022>`
- :bug:`98` Only close ``BotBase.stats._transport`` if ``BotBase.stats`` was created.


- :release:`7.2.1 <30th June 2022>`
- :bug:`96` Fix attempts to connect to ``BotBase.statsd_url`` when it is None.
- :bug:`91` Fix incorrect docstring for ``pydis_core.utils.member.handle_role_change``.
- :bug:`91` Pass missing self parameter to ``BotBase.ping_services``.
- :bug:`91` Add missing await to ``BotBase.ping_services`` in some cases.


- :release:`7.2.0 <28th June 2022>`
- :support:`93` Bump Discord.py to :literal-url:`0eb3d26 <https://github.com/Rapptz/discord.py/commit/0eb3d26343969a25ffc43ba72eca42538d2e7e7a>`:

  - Adds support for auto mod, of which the new auto_mod MESSAGE_TYPE is needed for our filter system.


- :release:`7.1.3 <30th May 2022>` 79
- :support:`79` Add `sphinx-multiversion <https://pypi.org/project/sphinx-multiversion/>`_ to make available older doc versions.
- :support:`79` Restore on-site changelog.


- :release:`7.1.0 <24th May 2022>`
- :feature:`78` Bump Discord.py to :literal-url:`4cbe8f5 <https://github.com/Rapptz/discord.py/tree/4cbe8f58e16f6a76371ce45a69e0832130d6d24f>`:

  - This fixes a bug with permission resolution when dealing with timed out members.


- :release:`7.0.0 <10th May 2022>`
- :bug:`75 major` Capture all characters up to a whitespace in the Discord Invite regex.
- :breaking:`75` Discord invite regex no longer returns a URL safe result, refer to documentation for safely handling it.


- :release:`6.4.0 <26th April 2022>`
- :feature:`72` Bump discord.py to :literal-url:`5a06fa5 <https://github.com/Rapptz/discord.py/tree/5a06fa5f3e28d2b7191722e1a84c541560008aea>`:

  - Notably, one of the commits in this bump dynamically extends the timeout of ``Guild.chunk()`` based on the number or members, so it should actually work on our guild now.


- :release:`6.3.2 <25th April 2022>`
- :bug:`69` Actually use ``statsd_url`` when it gets passed to ``BotBase``.


- :release:`6.3.1 <21st April 2022>`
- :bug:`68` Correct version number in pyproject.toml.


- :release:`6.3.0 <21st April 2022>`
- :feature:`-` (Committed directly to main) Don't load modules starting with ``_``.


- :release:`6.2.0 <21st April 2022>`
- :feature:`66` Load each cog in it's own task to avoid a single cog crashing entire load process.


- :release:`6.1.0 <20th April 2022>`
- :feature:`65` Add ``unqualify`` to the ``pydis_core.utils`` namespace for use in bots that manipulate extensions.


- :release:`6.0.0 <19th April 2022>`
- :breaking:`64` Bump discord.py to :literal-url:`987235d <https://github.com/Rapptz/discord.py/tree/987235d5649e7c2b1a927637bab6547244ecb2cf>`:

  - This reverts a change to help command behaviour that broke our custom pagination.
  - This also adds basic forum channel support to discord.py.


- :release:`5.0.4 <18th April 2022>` 63

   ..
      Feature 63 Needs to be explicitly included above because it was improperly released within a bugfix version
      instead of a minor release

- :feature:`63` Allow passing an ``api_client`` to ``BotBase.__init__`` to specify the ``pydis_core.site_api.APIClient`` instance to use.


- :release:`5.0.3 <18th April 2022>`
- :bug:`61` Reconnect to redis session on setup if it is closed.


- :release:`5.0.2 <5th April 2022>`
- :bug:`56` Create a dummy ``AsyncstatsdClient`` before connecting to real url, in case a connection cannot be made on init.
- :bug:`56` Move the creation of the ``asyncio.Event``, ``BotBase._guild_available`` to within the setup hook, to avoid a deprecation notice.


- :release:`5.0.1 <2nd April 2022>`
- :bug:`54` Move creation of BotBase's ``aiohttp.AsyncResolver`` to the async setup hook, to avoid deprecation notice.


- :release:`5.0.0 <2nd April 2022>`
- :breaking:`42` Remove public extensions util.
- :feature:`42` Add ``BotBase``, a ``discord.ext.commands.Bot`` sub-class, which abstracts a lot of logic shared between our bots.
- :feature:`42` Add async statsd client.
- :support:`42` Bump Discord.py to latest alpha commit.


- :release:`4.0.0 <14th March 2022>`
- :breaking:`39` Migrate back to Discord.py 2.0.


- :release:`3.0.1 <5th March 2022>`
- :bug:`37` Setup log tracing when ``pydis_core.utils.logging`` is imported so that it can be used within pydis_core functions.


- :release:`3.0.0 <3rd March 2022>`
- :breaking:`35` Move ``apply_monkey_patches()`` directly to `pydis_core.utils` namespace.


- :release:`2.1.0 <24th February 2022>`
- :feature:`34` Port the Site API wrapper from the bot repo.


- :release:`2.0.0 <22nd February 2022>`
- :breaking:`35` Moved regex to ``pydis_core.utils`` namespace.
- :breaking:`32` Migrate from discord.py 2.0a0 to disnake.
- :feature:`32` Add common monkey patches.
- :feature:`29` Port many common utilities from our bots:

  - caching
  - channel
  - extensions
  - loggers
  - members
  - scheduling
- :support:`2` Added intersphinx to docs.


- :release:`1.2.0 <9th January 2022>`
- :feature:`12` Code block detection regex.


- :release:`1.1.0 <2nd December 2021>`
- :support:`2` Autogenerated docs.
- :feature:`2` Regex utility.


- :release:`1.0.0 <17th November 2021>`
- :feature:`1` Core package, poetry, and linting CI.
