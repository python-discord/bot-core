Local Development & Testing
===========================

To test your features locally, there are a few possible approaches:

1. Install your local copy of botcore into a pre-existing project such as bot
2. Use the provided template from the :repo-file:`dev/bot <dev/bot>` folder

See below for more info on both approaches.

What's going to be common between them is you'll need to write code to test your feature.
This might mean adding new commands, modifying existing ones, changing utilities, etc.
The steps below should provide most of the groundwork you need, but the exact requirements will
vary by the feature you're working on.


Option 1
--------
1. Navigate to the project you want to install bot-core in, such as bot or sir-lancebot
2. Run ``pip install /path/to/botcore`` in the project's environment

   - The path provided to install should be the root directory of this project on your machine.
     That is, the folder which contains the ``pyproject.toml`` file.
   - Make sure to install in the correct environment. Most Python Discord projects use
     poetry, so you can run ``poetry run pip install /path/to/botcore``.

3. You can now use features from your local bot-core changes.
   To load new changes, run the install command again.


Option 2
--------
1. Copy the :repo-file:`bot template folder <dev/bot>` to the root of the bot-core project.
   This copy is going to be git-ignored, so you're free to modify it however you like.
2. Run the project

   - Locally: You can run it on your system using ``python -m bot``
   - Docker: You can run on docker using ``docker compose up -d bot``.

3. Configure the environment variables used by the program.
   You can set them in an ``.env`` file in the project root directory. The variables are:

   - ``TOKEN`` (required): Discord bot token, with all intents enabled
   - ``GUILD_ID`` (required): The guild the bot should monitor
   - ``PREFIX``: The prefix to use for invoking bot commands. Defaults to mentions and ``!``
   - ``ALLOWED_ROLES``: A comma seperated list of role IDs which the bot is allowed to mention

4. You can now test your changes. You do not need to do anything to reinstall the
   library if you modify your code.

.. tip::
   The docker-compose included contains services from our other applications
   to help you test out certain features. Use them as needed.
