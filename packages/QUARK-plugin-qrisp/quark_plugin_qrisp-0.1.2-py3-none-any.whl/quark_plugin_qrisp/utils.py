import logging

from qrisp import QuantumVariable
from qrisp.algorithms.qiro import QIROProblem
from qrisp.interface.qunicorn.backend_client import BackendClient


def run(
    qiro_problem: QIROProblem,
    arg,
    depth: int,
    qiro_reps: int,
    shots: int,
    iterations: int,
    backend: BackendClient | None = None,
):
    qarg = QuantumVariable(arg)

    try:
        res_qiro = qiro_problem.run_qiro(
            qarg=qarg,
            depth=depth,
            n_recursions=qiro_reps,
            mes_kwargs={"shots": shots, "backend": backend},
            max_iter=iterations,
        )
    except ValueError as e:
        logging.error(f"The following ValueError occurred in module QrispQIRO: {e}")
        logging.error("The benchmarking run terminates with exception.")
        raise Exception("Please refer to the logged error message.") from e

    return res_qiro
