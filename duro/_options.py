from dataclasses import dataclass

import duro


@dataclass
class Options:
    renderer: duro.Renderer = duro.renderer.tty()


# TODO(pcattori): multiple renderers
# TODO(pcattori): redirect stdout/stderr


# intentionally mutable, global
options = Options()
