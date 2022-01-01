# JUP

This is a plugin for poetry to just use pip. It is intended to provide a quick way to add dependencies to a poetry package when poetry itself won't add the package but `pip install <needed-package>` works.

## How to use

To use this plugin, use a version of poetry that supports plugins then add it like:

```
poetry plugin add git+https://github.com/NotMatthewGriffin/jup@main
```

Now you can add a dependency to your pyproject.toml that uses poetry by adding a section:

```toml
[tool.jup]
deps = [
    "more-itertools @ git+https://github.com/more-itertools/more-itertools@master"
]
```

After the above steps are complete use normal poetry commands like `poetry install`, `poetry update`, and `poetry build`.
The plugin will install the specified dependencies into the same venv as poetry installs the other dependencies specified normally.
In the case of a `poetry build` the plugin will add a `Requires-Dist` to the METADATA of wheels for each dependency specified with jup and for SDISTs it will add all of the specified dependencies to the `install_requires` list in setup.py.
