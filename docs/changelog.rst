.. See docs for details on formatting your entries
   https://releases.readthedocs.io/en/latest/concepts.html

Changelog
=========
- :release:`9.7.0 <10th June 2023>`
- :feature:`179` Add paste service utility to upload text to our paste service.
- :feature:`177` Automatically handle discord.Forbidden 90001 errors in all schedules
- :feature:`176` Migrate repo to use ruff for linting


- :release:`9.6.0 <6th May 2023>`
- :feature:`175` Log when waiting for the guild to be available before loading cogs
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
- :bug:`170` Save references of newly created tasks in :obj:`pydis_core.utils.scheduling`

- :release:`9.3.0 <13th December 2022>`
- :feature:`169` Return :obj:`None` upon receiving a bad request from Discord in :obj:`pydis_core.utils.members.get_or_fetch_member`

- :release:`9.2.0 <17th November 2022>`
- :support:`151` Add support for Python 3.11

- :release:`9.1.1 <14th November 2022>`
- :bug:`162` Handle not being able to delete the interaction message on button press/timeout.


- :release:`9.1.0 <13th November 2022>`
- :feature:`158` Bump Discord.py to :literal-url:`2.1.0 <https://github.com/Rapptz/discord.py/releases/tag/v2.1.0>`.
- :feature:`88` Add a decorator that stops successive duplicate invocations of commands


- :release:`9.0.0 <5th November 2022>`
- :breaking:`157` Rename project to pydis_core to allow for publishing to pypi.


- :release:`8.2.1 <18th September 2022>`
- :bug:`138` Bump Discord.py to :literal-url:`2.0.1 <https://discordpy.readthedocs.io/en/latest/whats_new.html#v2-0-1>`.


- :release:`8.2.0 <18th August 2022>`
- :support:`125` Bump Discord.py to the stable :literal-url:`2.0 release <https://discordpy.readthedocs.io/en/latest/migrating.html>`.


- :release:`8.1.0 <16th August 2022>`
- :support:`124` Updated :obj:`pydis_core.utils.regex.DISCORD_INVITE` regex to optionally match leading "http[s]" and "www".


- :release:`8.0.0 <27th July 2022>`
- :breaking:`110` Bump async-rediscache to v1.0.0-rc2
- :support:`108` Bump Python version to 3.10.*
- :bug:`107 major` Declare aiodns as a project dependency.
- :support:`107` Add a sample project with boilerplate and documentation explaining how to develop for bot-core.


- :release:`7.5.0 <23rd July 2022>`
- :feature:`101` Add a utility to clean a string or referenced message's content


- :release:`7.4.0 <17th July 2022>`
- :feature:`106` Add an optional ``message`` attr to :obj:`pydis_core.utils.interactions.ViewWithUserAndRoleCheck`. On view timeout, this message has its view removed if set.


- :release:`7.3.1 <16th July 2022>`
- :bug:`104` Fix :obj:`pydis_core.utils.interactions.DeleteMessageButton` not working due to using wrong delete method.


- :release:`7.3.0 <16th July 2022>`
- :feature:`103` Add a generic view :obj:`pydis_core.utils.interactions.ViewWithUserAndRoleCheck` that only allows specified users and roles to interaction with it
- :feature:`103` Add a button :obj:`pydis_core.utils.interactions.DeleteMessageButton` that deletes the message attached to its parent view.


- :release:`7.2.2 <9th July 2022>`
- :bug:`98` Only close ``BotBase.stats._transport`` if ``BotBase.stats`` was created


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
- :bug:`68` Correct version number in pyproject.toml


- :release:`6.3.0 <21st April 2022>`
- :feature:`-` (Committed directly to main) Don't load modules starting with ``_``


- :release:`6.2.0 <21st April 2022>`
- :feature:`66` Load each cog in it's own task to avoid a single cog crashing entire load process.


- :release:`6.1.0 <20th April 2022>`
- :feature:`65` Add ``unqualify`` to the ``pydis_core.utils`` namespace for use in bots that manipulate extensions.


- :release:`6.0.0 <19th April 2022>`
- :breaking:`64` Bump discord.py to :literal-url:`987235d <https://github.com/Rapptz/discord.py/tree/987235d5649e7c2b1a927637bab6547244ecb2cf>`:

  - This reverts a change to help command behaviour that broke our custom pagination
  - This also adds basic forum channel support to discord.py


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
- :bug:`54` Move creation of BotBase's ``aiohttp.AsyncResolver`` to the async setup hook, to avoid deprecation notice


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
- :breaking:`35` Moved regex to ``pydis_core.utils`` namespace
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
