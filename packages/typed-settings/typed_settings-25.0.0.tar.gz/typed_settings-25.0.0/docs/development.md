# Development

% skip: start

Typed Settings uses:

- [uv] for packaging and virtual env management
- [Hatch(ling)][hatch] as build backend
- [nox] as task manager, e.g. to run the linters and
  tests against a matrix of different dependency and Python versions.
  Nox is similar to [tox] but uses Python to describe all tasks.
- [pre-commit] to lint the code you're going to commit.

[uv] and [pre-commit] need to be installed globally via your favorite package manager.
`uv` will handle everything else.


## Setting up a Development Environment

1. Clone the project and change into its directory:

   ```console
   $ git clone git@gitlab.com:sscherfke/typed-settings.git
   $ cd typed-settings
   ```

2. Create a virtual environment and install all development dependencies:

   ```console
   $ uv sync
   $ source .venv/bin/activate
   ```

   ```{note}
   If you don't like activating venvs, prepend `uv run` to all invocations of `nox`, `pytest` or other tools,
   e.g.: `uv run nox` or `uv run pytest`.
   ```

3. Install the pre-commit hooks:

   ```console
   $ pre-commit install --install-hooks
   ```

Done. :-)

## Linting

Typed Settings uses [ruff] and [mypy] for linting.
You can run these tools directly but it's easier to use {program}`nox`:

```console
(.venv)$ nox -e lint mypy
```

[Ruff] is also used for code formatting and auto-fixing linting issues.
You should use {program}`nox` to run it:

```console
(.venv)$ nox -e fix
```

[Pre-commit] also runs all linters and formatters with all changed files every time you want to commit something.


## Testing

You run the tests with [pytest].
It is configured to also run doctests in {file}`src/` and {file}`docs/` and
to test the examples in that directory,
so do not only run it on {file}`tests/`.

```console
(.venv)$ pytest
```

You can also use [nox] to run tests for all supported Python versions at the same time.
This will also calculate the combined test coverage and run the linters.

```console
(.venv)$ nox
```

## Docs

[Sphinx] is used to build the documentation.
The documentation is formatted with Markdown using [MyST]
(with the exception of the API docs, which are formatted with [ReStructuredText]).
There's a {file}`Makefile` that you can invoke to build the documentation:

```console
(.venv)$ make -C docs html
(.venv)$ make -C docs clean html  # Clean rebuild
(.venv)$ open docs/_build/html/index.html  # Use "xdg-open" on Linux
```

You can also use nox:

```console
(.venv)$ nox -e docs  # Just build changed pages
(.venv)$ nox -e docs -- clean  # Clean build
(.venv)$ nox -e docs -- open  # open docs in browser
(.venv)$ nox -e docs -- clean open  # Clean build and open
```


## Commits

When you commit something, take your time to write a [precise, meaningful commit message][commit-message].
In short:

- Use the imperative: *Fix issue with XY*.
- If your change is non-trivial, describe why your change was needed and how it works.
  Separate this from the title with an empty line.
- Add references to issues, e.g. `See: #123` or `Fixes: #123`.

When any of the linters run by Pre-commit finds an issue or if a formatter changes a file, the commit is aborted.
In that case, you need to review the changes, add the files and try again:

```console
(.venv)$ git status
(.venv)$ git diff
(.venv)$ git add src/typed_settings/...
```

## Releasing New Versions

Releases are created and uploaded by the CI/CD pipeline.
The release steps are only executed in tag pipelines.

To prepare a release:

1. Add missing entries to the {file}`CHANGELOG.md`.
   Use an emoji for each line.
   The changelog contains a legend at the bottom where you can look-up the proper emoji.
2. Add the current date as release date to the latest `(unreleased)` section in {file}`CHANGELOG.md`.
3. Commit using the message {samp}`Bump version from {a.b.c} to {x.y.z}`.
4. Push the changes and make sure the CI pipeline succeeds.
5. Check the results on the [testing PyPI].
6. Create an annotated tag: {samp}`git tag -am 'Release {x.y.z}' {x.y.z}`.
7. Push the tag: {samp}`git push origin {x.y.z}`.
8. Approve the upload step in the [CI/CD pipeline][cicd-pipeline].
   This will then create a release on [PyPI].
9. Check the release on [PyPI].
10. Toot something about it using `#TypedSettings`. :-)

[cicd-pipeline]: https://gitlab.com/sscherfke/typed-settings/-/pipelines
[commit-message]: https://cbea.ms/git-commit/
[hatch]: https://hatch.pypa.io/latest/
[mypy]: https://pypi.org/project/mypy/
[myst]: https://myst-parser.readthedocs.io/en/latest/
[nox]: https://pypi.org/project/nox/
[pre-commit]: https://pypi.org/project/pre-commit/
[pytest]: https://pypi.org/project/pytest/
[restructuredtext]: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[ruff]: https://pypi.org/project/ruff/
[sphinx]: https://pypi.org/project/sphinx/
[tox]: https://pypi.org/project/tox/
[uv]: https://pypi.org/project/uv/
[venv]: https://docs.python.org/3/library/venv.html
[testing pypi]: https://test.pypi.org/project/typed-settings/
[pypi]: https://pypi.org/project/typed-settings/
