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


## Layout
The docs folder has a few moving components, here's a brief description of each:

- `_static`: This folder includes extra resources that are copied blindly by sphinx into the result
  making it perfect for resources such as custom CSS or JS.
- `_templates` & `pages`: Both are considered HTML templates, and passed to Sphinx as `templates_path`.
  The difference between them is that `_templates` is only used to provide templates and overrides that
  are used by other pages, while `pages` are full-blown independent pages that will be included in the
  result. Files in `pages` are passed to Sphinx as `html_additional_pages`, and will maintain the same
  structure as the folder. That is to say, a file such as `pages/a/b.html` will create `https://bot-core/a/b.html`.
- `changelog.rst`: This contains a list of all the project's changes. Please refer to [Changelog](#Changelog)
  below for more info.
- `index.rst`: The main content for the project's homepage.
- `conf.py`: Configuration for Sphinx. This includes things such as the project name, version,
  plugins and their configuration.
- `utils.py`: Helpful function used by `conf.py` to properly create the docs.
- `netliy_build.py`: Script which downloads the build output in netlify. Refer to [Static Netlify Build](#static-builds)


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
