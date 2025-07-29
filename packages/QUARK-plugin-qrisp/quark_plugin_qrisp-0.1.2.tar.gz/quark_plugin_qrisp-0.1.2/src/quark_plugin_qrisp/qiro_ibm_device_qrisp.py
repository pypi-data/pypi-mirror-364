from dataclasses import dataclass
from typing import override
import logging

from qrisp.interface import QiskitRuntimeBackend
from quark.core import Core, Data, Result
from quark.interface_types import Other

from quark_plugin_qrisp.utils import run

@dataclass
class QiroIbmDeviceQrisp(Core):
    qiro_reps: int = 3
    depth: int = 5
    shots: int = 1000
    iterations: int = 20
    # Be aware that an IBM api_token is required to run this module.
    # Be also aware that the default configuration generates quantum circuits of considerable size and
    # that you are responsible for the costs incurred by running this module on an IBM device.

    @override
    def preprocess(self, data: Other) -> Result:
        backend = QiskitRuntimeBackend(api_token="", mode= "session")
        logging.info(f"IBM run started with the following parameters: ")
        logging.info(f"QIRO repetitions: {self.qiro_reps}, depth: {self.depth}, shots: {self.shots},"
                     f" iterations: {self.iterations}")
        logging.info(f"Be aware that you are responsible for costs incurred by running jobs on an IBM device.")
        self._result = run(
            data.data[0],
            data.data[1],
            self.depth,
            self.qiro_reps,
            self.shots,
            self.iterations,
            backend=backend,
        )
        backend.close_session()
        logging.info("QIRO run completed on IBM device.")
        return Data(None)

    @override
    def postprocess(self, data: None) -> Result:
        return Data(Other(self._result))
