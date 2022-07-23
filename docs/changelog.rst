.. See docs for details on formatting your entries
   https://releases.readthedocs.io/en/latest/concepts.html

Changelog
=========

- :release:`7.5.0 <23rd July 2022>`
- :feature:`101` Add a utility to clean a string or referenced message's content


- :release:`7.4.0 <17th July 2022>`
- :feature:`106` Add an optional ``message`` attr to :obj:`botcore.utils.interactions.ViewWithUserAndRoleCheck`. On view timeout, this message has its view removed if set.


- :release:`7.3.1 <16th July 2022>`
- :bug:`104` Fix :obj:`botcore.utils.interactions.DeleteMessageButton` not working due to using wrong delete method.


- :release:`7.3.0 <16th July 2022>`
- :feature:`103` Add a generic view :obj:`botcore.utils.interactions.ViewWithUserAndRoleCheck` that only allows specified users and roles to interaction with it
- :feature:`103` Add a button :obj:`botcore.utils.interactions.DeleteMessageButton` that deletes the message attached to its parent view.


- :release:`7.2.2 <9th July 2022>`
- :bug:`98` Only close ``BotBase.stats._transport`` if ``BotBase.stats`` was created


- :release:`7.2.1 <30th June 2022>`
- :bug:`96` Fix attempts to connect to ``BotBase.statsd_url`` when it is None.
- :bug:`91` Fix incorrect docstring for ``botcore.utils.member.handle_role_change``.
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
- :feature:`65` Add ``unqualify`` to the ``botcore.utils`` namespace for use in bots that manipulate extensions.


- :release:`6.0.0 <19th April 2022>`
- :breaking:`64` Bump discord.py to :literal-url:`987235d <https://github.com/Rapptz/discord.py/tree/987235d5649e7c2b1a927637bab6547244ecb2cf>`:

  - This reverts a change to help command behaviour that broke our custom pagination
  - This also adds basic forum channel support to discord.py


- :release:`5.0.4 <18th April 2022>` 63

   ..
      Feature 63 Needs to be explicitly included above because it was improperly released within a bugfix version
      instead of a minor release

- :feature:`63` Allow passing an ``api_client`` to ``BotBase.__init__`` to specify the ``botcore.site_api.APIClient`` instance to use.


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
- :bug:`37` Setup log tracing when ``botcore.utils.logging`` is imported so that it can be used within botcore functions.


- :release:`3.0.0 <3rd March 2022>`
- :breaking:`35` Move ``apply_monkey_patches()`` directly to `botcore.utils` namespace.


- :release:`2.1.0 <24th February 2022>`
- :feature:`34` Port the Site API wrapper from the bot repo.


- :release:`2.0.0 <22nd February 2022>`
- :breaking:`35` Moved regex to ``botcore.utils`` namespace
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
