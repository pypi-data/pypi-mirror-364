from dataclasses import dataclass
from typing import override

from quark.core import Core, Data, Result
from quark.interface_types import Other

from quark_plugin_qrisp.utils import run


@dataclass
class QiroStatevectorSimulatorQrisp(Core):
    qiro_reps: int = 3
    depth: int = 5
    shots: int = 1000
    iterations: int = 20

    @override
    def preprocess(self, data: Other) -> Result:
        self._result = run(
            data.data[0],
            data.data[1],
            self.depth,
            self.qiro_reps,
            self.shots,
            self.iterations,
        )
        return Data(None)

    @override
    def postprocess(self, data: None) -> Result:
        return Data(Other(self._result))
