from quark.plugin_manager import factory

from quark_plugin_qrisp.mis_qiro_mapping_qrisp import MisQiroMappingQrisp
from quark_plugin_qrisp.qiro_ibm_device_qrisp import QiroIbmDeviceQrisp
from quark_plugin_qrisp.qiro_statevector_simulator_qrisp import (
    QiroStatevectorSimulatorQrisp,
)


def register() -> None:
    """
    Register all modules exposed to quark by this plugin.
    For each module, add a line of the form:
        factory.register("module_name", Module)

    The "module_name" will later be used to refer to the module in the configuration file.
    """
    factory.register("mis_qiro_mapping_qrisp", MisQiroMappingQrisp)
    factory.register("qiro_statevector_simulator_qrisp", QiroStatevectorSimulatorQrisp)
    factory.register("qiro_ibm_device_qrisp", QiroIbmDeviceQrisp)
