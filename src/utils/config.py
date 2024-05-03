import yaml

from utils import Singleton

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
        
    