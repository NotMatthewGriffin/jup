from poetry.utils.env import EnvManager
from poetry.plugins.plugin import Plugin
from poetry.installation.installer import Installer
from poetry.core.masonry.builders.sdist import SdistBuilder

class JupPlugin(Plugin):
    def activate(self, poetry, io):

        # patch install
        original_method = Installer._do_install
        def with_jup(*args, **kwargs):
            result = original_method(*args, **kwargs)
            env_manager = EnvManager(poetry)
            env = env_manager.get(True)
            for dep in poetry.pyproject.data.get('tool', {}).get('jup', {}).get('deps', []):
                io.write_line(f"Just using pip for {dep}")
                pip_result = env.run_pip("install", "-U", dep)
                io.write_line(str(pip_result))
            return result
        Installer._do_install = with_jup

        # patch build
        original_dependencies = SdistBuilder.convert_dependencies
        def dependencies_with_jup(extra_cls, *args, **kwargs):
            result = original_dependencies(*args, **kwargs)
            main_deps, extras = result
            main_deps.extend(poetry.pyproject.data.get('tool', {}).get('jup', {}).get('deps', []))
            return main_deps, extras
        SdistBuilder.convert_dependencies = classmethod(dependencies_with_jup)

        original_files = SdistBuilder.find_files_to_add
        def files_to_add_with_jup(*args, **kwargs):
            result = original_files(*args, **kwargs)
            return set(filter(lambda filename : filename.path.name != 'pyproject.toml', result))
        SdistBuilder.find_files_to_add = files_to_add_with_jup
