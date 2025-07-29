from dataclasses import dataclass
from typing import override

from qrisp.algorithms.qiro import (
    QIROProblem,
    create_max_indep_cost_operator_reduced,
    create_max_indep_replacement_routine,
    create_max_indep_set_cl_cost_function,
    qiro_init_function,
    qiro_rx_mixer,
)
from quark.core import Core, Data, Result
from quark.interface_types import Graph, Other


@dataclass
class MisQiroMappingQrisp(Core):
    def _qiro_select_best_state(self, res_qiro, cost_func) -> str:
        """
        This function is used for post_processing, i.e. finding the best solution out of the 10 most likely ones.
        Since QIRO is an optimization algorithm, the most_likely solution can be of bad quality, depending on
        the problem cost landscape.

        :param res_qiro: Dictionary containing the QIRO optimization routine results, i.e. the final state.
        :param cost_func: classical cost function of the problem instance
        """
        maxfive = sorted(res_qiro, key=res_qiro.get, reverse=True)[:10]
        max_cost = 0
        best_state = "0" * len(maxfive[0])

        for key in maxfive:
            if cost_func({key: 1}) < max_cost:
                best_state = key
                max_cost = cost_func({key: 1})

        return best_state

    @override
    def preprocess(self, data: Graph) -> Result:
        self._graph = data.as_nx_graph()

        qiro_instance = QIROProblem(
            self._graph,
            replacement_routine=create_max_indep_replacement_routine,
            cost_operator=create_max_indep_cost_operator_reduced,
            mixer=qiro_rx_mixer,
            cl_cost_function=create_max_indep_set_cl_cost_function,
            init_function=qiro_init_function,
        )
        return Data(Other((qiro_instance, self._graph.number_of_nodes())))

    @override
    def postprocess(self, data: Other) -> Result:
        res_qiro = data.data
        best_bitstring = self._qiro_select_best_state(
            res_qiro, create_max_indep_set_cl_cost_function(self._graph)
        )

        winner_state = [
            key
            for index, key in enumerate(self._graph.nodes())
            if best_bitstring[index] == "1"
        ]

        return Data(Other(winner_state))
