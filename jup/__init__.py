from poetry.utils.env import EnvManager
from poetry.plugins.plugin import Plugin
from poetry.installation.installer import Installer
from poetry.core.masonry.builders.sdist import Builder, SdistBuilder


class JupPlugin(Plugin):
    def activate(self, poetry, io):
        def get_jup_dependencies():
            return poetry.pyproject.data.get("tool", {}).get("jup", {}).get("deps", [])

        # patch install
        original_method = Installer._do_install
        def with_jup(*args, **kwargs):
            result = original_method(*args, **kwargs)
            env_manager = EnvManager(poetry)
            env = env_manager.get(True)
            for dep in get_jup_dependencies():
                io.write_line(f"Just using pip for {dep}")
                pip_result = env.run_pip("install", "-U", *dep.split(' '))
                io.write_line(str(pip_result))
            return result
        Installer._do_install = with_jup

        # patch sdist build
        original_dependencies = SdistBuilder.convert_dependencies
        def dependencies_with_jup(extra_cls, *args, **kwargs):
            result = original_dependencies(*args, **kwargs)
            main_deps, extras = result
            main_deps.extend(get_jup_dependencies())
            return main_deps, extras
        SdistBuilder.convert_dependencies = classmethod(dependencies_with_jup)

        original_files = SdistBuilder.find_files_to_add
        def files_to_add_with_jup(*args, **kwargs):
            result = original_files(*args, **kwargs)
            return set(
                filter(lambda filename: filename.path.name != "pyproject.toml", result)
            )
        SdistBuilder.find_files_to_add = files_to_add_with_jup

        # patch metadata for wheel build
        original_metadata = Builder.get_metadata_content
        def metadata_content_with_jup(*args, **kwargs):
            result = original_metadata(*args, **kwargs)
            jup_deps = "\n".join(
                map(lambda dep: f"Requires-Dist: {dep}", get_jup_dependencies())
            )
            return (result + jup_deps).strip()
        Builder.get_metadata_content = metadata_content_with_jup
