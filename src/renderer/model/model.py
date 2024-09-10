# class that represents the model to be rendered
from dataclasses import dataclass, field


@dataclass
class Model:
    name: str
    mesh: str = field(default='default')
    texture: str = field(default='default')
    shader: str = field(default='default')
    material: str = field(default='default')
    in_instance: str = field(default='')
