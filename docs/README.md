# Docs
Meta information about this project's documentation.

Table of contents:
- [Building the docs](#Building)
- [Writing docstrings](#Docstrings)
- [Writing a changelog](#Changelog)


## Building
To build the docs, you can use the following task:
```shell
poetry run task docs
```

The output will be in the [`/docs/build`](.) directory.

Additionally, there are two helper tasks: `apidoc` and `builddoc`.
`apidoc` is responsible for calling autodoc and generating docs from docstrings.
`builddoc` generates the HTML site, and should be called after apidoc.

Neither of these two tasks needs to be manually called, as the `docs` task calls both.


## Docstrings
To have your code properly added to the generated docs, you need to do a couple of things:
1. Write your code with annotations.
2. [Write your docstring, using the Google docstring format][google]

Refer to the [sphinx documentation][docstring-sections] for more information.


[google]: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
[docstring-sections]: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#docstring-sections


## Changelog
Each change requires an entry in the [Changelog](./changelog.rst).

Refer to the [Releases][releases] documentation for more information on the exact format and content of entries
You can use [this site][next] to get the PR number that'll be assigned for your entry.


[releases]: https://releases.readthedocs.io/en/latest/concepts.html
[next]: https://ichard26.github.io/next-pr-number/?owner=python-discord&name=bot-core

## Static Builds
We deploy our docs to netlify to power static previews on PRs.
Check out [python-discord/site][STATIC_BUILD_DOCS] for more info on the system.

[STATIC_BUILD_DOCS]: https://github.com/python-discord/site/tree/main/static-builds
