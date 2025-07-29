from copy import deepcopy
from typing import Optional

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin import hookimpl


class ExternalDependenciesBuilder(BuildHookInterface):
    PLUGIN_NAME = 'external-dependencies'

    def initialize(self, version: str, build_data: dict[str, any]) -> None:
        self._default_constructor = self.build_config.core_metadata_constructor

        def metadata_constructor_extended(
            local_self, metadata: ProjectMetadata, extra_dependencies: Optional[tuple[str]] = None
        ) -> str:
            metadata_file = self._default_constructor(metadata, extra_dependencies)

            external_dependencies = None
            if 'external-dependencies' in metadata.core.config:
                # This syntax feels logical but is undocumented
                # under [project] put a key 'external-dependencies' with a list of strings
                external_dependencies = deepcopy(metadata.core.config['external-dependencies'])

            elif 'external' in metadata.config and 'dependencies' in metadata.config['external']:
                # This syntax is proposed here (current stage: draft) : https://peps.python.org/pep-0725/
                # under [external] put a key 'dependencies' with a list of strings
                external_dependencies = deepcopy(metadata.config['external']['dependencies'])

            if external_dependencies:
                header_section = metadata_file
                content_section = ''
                if 'Description-Content-Type' in metadata_file:
                    split_file = metadata_file.split('Description-Content-Type')
                    header_section = split_file[0]
                    content_section = split_file[1]

                print(f'  - {ExternalDependenciesBuilder.PLUGIN_NAME}')
                for dependency in external_dependencies:
                    print(f'    - Requires-External: {dependency}')
                    header_section += f'Requires-External: {dependency}\n'
                metadata_file = header_section + 'Description-Content-Type' + content_section

            return metadata_file

        type(self.build_config).core_metadata_constructor = metadata_constructor_extended

@hookimpl
def hatch_register_build_hook():
    return ExternalDependenciesBuilder