import yaml

from utils import Singleton

from icecream import ic

class Config(metaclass=Singleton):
    """Singleton class to retrieve the configuration information

    Args:
        metaclass (_type_, optional): _description_. Defaults to Singleton.
    """
    
    def __init__(self) -> None:
        """Constructor method, gets all the configuration YAML files from ./assets/config
        """
        
        self._setup: dict
             
        with open('./assets/config/setup.yml', 'r') as file:
            self._setup = yaml.safe_load(file)
    
    
    @property
    def setup(self) -> dict:
        return(self._setup)
    
    @setup.setter
    def setup(self, setup: dict) -> None:
        self._setup = setup
  

    def initialize_parameters(self, obj: any, config_location: str, default_config: dict, **kwargs):
        """method to set the parameters of the incoming object with the incoming values, or the values of the config file, or the default values, in that priority

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
            setattr(obj, key, value if value is not None else (config.get(key) if config.get(key) is not None else default_config.get(key)))
    