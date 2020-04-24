from dataclasses import dataclass

import duro


@dataclass
class Options:
    renderer: duro.Renderer = duro.renderers.tty()


# intentionally mutable, global
options = Options()
