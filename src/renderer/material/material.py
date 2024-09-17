from dataclasses import dataclass, field


@dataclass
class Material:
    name: str
    ambient: list[float, float, float] = field(default_factory=lambda: [0.5, 0.5, 0.5])
    diffuse: list[float, float, float] = field(default_factory=lambda: [0.8, 0.8, 0.8])
    specular: list[float, float, float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    shininess: float = field(default=128)
    roughness: float = field(default=0.5)
    metallic: float = field(default=0.5)
    models: list = field(default_factory=lambda: [])

    def add_model(self, model) -> None:
        self.models.append(model)

    def set_ambient(self, r, g, b) -> None:
        self.ambient = [r, g, b]

    def set_diffuse(self, r, g, b) -> None:
        self.diffuse = [r, g, b]

    def set_specular(self, r, g, b) -> None:
        self.specular = [r, g, b]

    def set_shininess(self, s) -> None:
        self.shininess = s

    def set_roughness(self, r) -> None:
        self.roughness = r

    def set_metallic(self, m) -> None:
        self.metallic = m
