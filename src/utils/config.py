from dataclasses import dataclass, field

import yaml

from utils import Singleton


@dataclass
class Config(metaclass=Singleton):
    """Singleton class to retrieve the configuration information

    Args:
        metaclass (_type_, optional): _description_. Defaults to Singleton.

    """

    setup: dict = field(default_factory=lambda: {})
    scene: dict = field(default_factory=lambda: {})

    def __post_init__(self) -> None:
        with open('./assets/config/setup.yml') as file:
            self.setup = yaml.safe_load(file)

        with open('./assets/scenes/scene.yml') as file:
            self.scene = yaml.safe_load(file)

    def initialize_parameters(self, obj: any, config_location: str, default_config: dict, **kwargs):
        """Method to set the parameters of the incoming object with the incoming values, or the values of the config file, or the default values, in that priority

        Args:
            obj (any): object to set the parameters to
            config_location (str): string defining the location of the configuration in the config file
            default_config (dict): default fallback values in case neither the user nor the config file settings were found

        """
        components: list[str] = config_location.split('.')

        config: dict = self.setup

        for component in components:
            config = config.get(component)

        for key, value in kwargs.items():
            setattr(
                obj,
                key,
                (
                    value
                    if value is not None
                    else (config.get(key) if config.get(key) is not None else default_config.get(key))
                ),
            )
