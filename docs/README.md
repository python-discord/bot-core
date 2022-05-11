# Docs
Meta information about this project's documentation.

Table of contents:
- [Building the docs](#Building)
- [Docs Layout](#Layout)
- [Building all versions](#Versions)
- [Writing docstrings](#Docstrings)
- [Writing a changelog](#Changelog)


## Building
To build the docs, you can use the following task:
```shell
poetry run task docs
```

The output will be in the [`/docs/build`](.) directory.


## Versions
The project supports building all different versions at once using [sphinx-multiversion][multiversion]
after version `v7.1.0`. You can run the following command to achieve that:

```shell
poetry run sphinx_multiversion -v docs docs/build -n -j auto -n
```

This will build all tags, as well as the main branch. To build branches besides the main one
(such as the one you are currently working on), set the `BUILD_DOCS_FOR_HEAD` environment variable
to True.

When using multi-version, keep the following in mind:
1. This command will not fail on warnings, unlike the docs task. Make sure that passes first
   before using this one.
2. Make sure to clear the build directory before running this script to avoid conflicts.


[multiversion]: https://holzhaus.github.io/sphinx-multiversion/master/index.html


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
