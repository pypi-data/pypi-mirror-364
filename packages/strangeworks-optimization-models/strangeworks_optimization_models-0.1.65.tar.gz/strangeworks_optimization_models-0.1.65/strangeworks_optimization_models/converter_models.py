import gzip
import operator as op
import tempfile
from abc import ABC, abstractmethod
from itertools import combinations
from tempfile import NamedTemporaryFile
from typing import Any

import jijmodeling as jm
import networkx as nx
import numpy as np
import pyqubo as pq
import pyscipopt as po
from dimod import (
    BinaryQuadraticModel,
    ConstrainedQuadraticModel,
    DiscreteQuadraticModel,
    lp,
)
from dimod.sym import Comparison, Sense
from dwave.embedding import embed_ising
from minorminer import find_embedding
from titanq import Target, Vtype

from strangeworks_optimization_models.problem_models import (
    AquilaNDArray,
    FujitsuModelList,
    HitachiModelList,
    MatrixMarket,
    MPSFile,
    NECProblem,
    QuboDict,
    SwInfinityQModel,
)


class StrangeworksConverter(ABC):
    model: Any

    @abstractmethod
    def convert(
        model: Any,
    ) -> (
        BinaryQuadraticModel
        | ConstrainedQuadraticModel
        | DiscreteQuadraticModel
        | jm.Problem
        | AquilaNDArray
        | QuboDict
        | NECProblem
        | MPSFile
        | FujitsuModelList
        | HitachiModelList
        | tuple
    ):
        ...


class StrangeworksBinaryQuadraticModelJiJProblemConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel):
        self.model = model

    def convert(self) -> tuple[jm.Problem, dict[str, np.ndarray], Any, Any]:
        Q = jm.Placeholder("Q", ndim=2)  # Define variable d
        Q.len_at(0, latex="N")  # Set latex expression of the length of d
        x = jm.BinaryVar("x", shape=(Q.shape[0],))  # Define binary variable
        i = jm.Element("i", belong_to=(0, Q.shape[0]))  # Define dummy index in summation
        j = jm.Element("j", belong_to=(0, Q.shape[1]))  # Define dummy index in summation
        problem = jm.Problem("simple QUBO problem")  # Create problem instance
        problem += jm.sum(i, jm.sum(j, Q[i, j] * x[i] * x[j]))  # Add objective function

        qubo = self.model.to_qubo()

        Qmat = np.zeros((self.model.num_variables, self.model.num_variables))
        map = {m: i for i, m in enumerate(self.model.variables)}
        for k, v in qubo[0].items():
            Qmat[map[k[0]], map[k[1]]] = v

        offset = self.model.offset

        feed_dict = {"Q": Qmat}
        return problem, feed_dict, map, offset


class StrangeworksMPSFileJiJProblemConverter(StrangeworksConverter):
    def __init__(self, model: MPSFile):
        self.model = model

    def convert(self) -> tuple[jm.Problem, dict[str, np.ndarray]]:
        content = self.model.data.encode("utf-8")
        with NamedTemporaryFile(mode="w+b", delete=True, suffix=".txt.gz", prefix="f") as t_file:
            gzip_file = gzip.GzipFile(mode="wb", fileobj=t_file)
            gzip_file.write(content)
            gzip_file.close()
            t_file.flush()
            t_file.seek(0)

            problem, feed_dict = jm.load_mps(t_file.name)

        return problem, feed_dict


class StrangeworksBinaryQuadraticModelQuboDictConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel):
        self.model = model

    def convert(self) -> QuboDict:
        qubo = {}
        for lin in self.model.linear:
            qubo[(str(lin), str(lin))] = self.model.linear[lin]
        for quad in self.model.quadratic:
            qubo[(str(quad[0]), str(quad[1]))] = self.model.quadratic[quad]

        # Offset term should not added to the linear terms (code below should be removed)
        if self.model.offset != 0:
            for lin in self.model.linear:
                qubo[(str(lin), str(lin))] += self.model.offset

        return QuboDict(qubo)


class StrangeworksBinaryQuadraticModelNECProblemConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel):
        self.model = model

    def convert(self) -> NECProblem:
        # qubo = {}
        qubo: dict[Any, Any] = {}
        for lin in self.model.linear:
            qubo[(str(lin), str(lin))] = self.model.linear[lin]
        for quad in self.model.quadratic:
            qubo[(str(quad[0]), str(quad[1]))] = self.model.quadratic[quad]

        qubo["offset"] = self.model.offset

        return NECProblem(qubo)


class StrangeworksBinaryQuadraticModelFujitsuDictConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel):
        self.model = model

    def convert(self) -> FujitsuModelList:
        bqm = self.model

        mapping = {}
        iter = 0
        for var in self.model.variables:
            mapping[var] = iter
            iter += 1
        bqm.relabel_variables(mapping)

        qubo, offset = bqm.to_qubo()
        terms = []
        for variables, coefficient in qubo.items():
            term = {"coefficient": coefficient, "polynomials": list(variables)}
            terms.append(term)

        if offset != 0:
            terms.append({"coefficient": offset, "polynomials": []})

        binary_polynomial = {"terms": terms}

        return FujitsuModelList(binary_polynomial=binary_polynomial)


class StrangeworksBinaryQuadraticModelHitachiDictConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel, options: dict = {}):
        self.model = model
        self.options = options

    def convert(self) -> tuple[HitachiModelList, dict[Any, Any]]:
        def get_problem_graph_from_bqm(bqm):
            problem_graph = nx.Graph()
            problem_graph.add_nodes_from(bqm.linear.keys())
            problem_graph.add_edges_from(bqm.quadratic.keys())
            return problem_graph

        def get_target_graph(solver_type):
            # Set the size of the target graph
            if solver_type == 5:
                ll = 384
            elif solver_type == 3 or solver_type == 4:
                ll = 512
            else:
                raise ValueError("machine_type must be 3, 4, or 5.")

            # Create a square graph of size l
            target_graph = nx.grid_graph(dim=[ll, ll])

            # Add the diagonal edges to the square graph.
            target_graph.add_edges_from(
                [
                    edge
                    for x in range(ll - 1)
                    for y in range(ll - 1)
                    for edge in [((x, y), (x + 1, y + 1)), ((x + 1, y), (x, y + 1))]
                ]
            )
            return target_graph

        def get_hitachi(linear: dict, quadratic: dict):
            out_list = []
            for k in quadratic.keys():
                row = []
                for t in k:
                    row.extend(list(t))
                row.append(quadratic[k])
                out_list.append(row)
            for k in linear.keys():
                if linear[k] != 0:
                    row = []
                    row.extend(list(k))
                    row.extend(list(k))  # twice on purpose
                    row.append(linear[k])
                    out_list.append(row)
            return out_list

        # bqm = self.model
        bqm = self.model.change_vartype("SPIN", inplace=False)
        linear = bqm.linear
        quadratic = bqm.quadratic

        # Get Embedding of problem onto target graph
        problem_graph = get_problem_graph_from_bqm(bqm)
        target_graph = get_target_graph(self.options.get("solver_type", 4))
        embedding = find_embedding(problem_graph, target_graph, **self.options.get("embedding_parameters", {}))

        target_linear, target_quadratic = embed_ising(linear, quadratic, embedding, target_graph)
        target_list = get_hitachi(target_linear, target_quadratic)

        return HitachiModelList(target_list), embedding


class StrangeworksBinaryQuadraticModelMatrixMarketConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel):
        self.model = model

    def convert(self) -> tuple[MatrixMarket, dict[Any, Any]]:
        bqm = self.model
        mapping = {}
        iter = 0
        for var in bqm.variables:
            mapping[var] = iter
            iter += 1

        qubo_str = "%%MatrixMarket matrix coordinate integer general"
        qubo_str += f"\n{len(bqm.variables)} {len(bqm.variables)} {len(bqm.linear) + len(bqm.quadratic)}"
        for k, v in bqm.linear.items():
            qubo_str += f"\n{mapping[k] + 1} {mapping[k] + 1} {v}"
        for k, v in bqm.quadratic.items():
            if mapping[k[0]] > mapping[k[1]]:
                qubo_str += f"\n{mapping[k[0]] + 1} {mapping[k[1]] + 1} {v}"
            else:
                qubo_str += f"\n{mapping[k[1]] + 1} {mapping[k[0]] + 1} {v}"

        return MatrixMarket(qubo_str), mapping


class StrangeworksBinaryQuadraticModelSwInfinityQModelConverter(StrangeworksConverter):
    def __init__(self, model: BinaryQuadraticModel):
        self.model = model

    def convert(self) -> tuple[SwInfinityQModel, float, dict[str, int]]:
        def bqm_to_symmetric_qubo(bqm: BinaryQuadraticModel):
            Q = np.zeros((bqm.num_variables, bqm.num_variables)).astype(np.float32)
            map = {m: i for i, m in enumerate(bqm.variables)}
            qubo, offset = bqm.to_qubo()
            for k, v in qubo.items():
                Q[map[k[0]], map[k[1]]] = v
            return (Q + Q.T) / 2.0, offset, map

        def get_bias_and_weights(qubo: np.ndarray):
            # qubo, offset, map = bqm_to_symmetric_qubo(bqm)
            bias = qubo.diagonal()
            weights = qubo.copy() * 2.0  # factor of 2
            np.fill_diagonal(weights, 0)
            if np.any(weights != weights.T):
                raise ValueError("weights should be symmetric")
            return bias, weights

        qubo, offset, map = bqm_to_symmetric_qubo(self.model)
        bias, weights = get_bias_and_weights(qubo)

        IQModel = SwInfinityQModel()
        IQModel.add_variable_vector(
            "x", self.model.num_variables, Vtype.INTEGER, variable_bounds=([[0, 1]] * self.model.num_variables)
        )
        IQModel.set_objective_matrices(weights, bias, Target.MINIMIZE)

        return IQModel, offset, map


class StrangeworksMPSFileSwInfinityQModelConverter(StrangeworksConverter):
    def __init__(self, model: MPSFile):
        self.model = model

    def convert(self) -> tuple[SwInfinityQModel, float, dict[str, int]]:
        def _to_expr(
            name: str, comp: Comparison, vs: dict[str, pq.Binary], traditional_only: bool
        ) -> tuple[pq.UserDefinedExpress, str]:
            """Transform a `dimod.sym.Comparison` into a `pyqubo` user-defined
            expression, using the given dictionaries of binary variables.

            Args:
                name: Name of comparison from original problem.
                comp: Comparison to transform.
                vs: Dictionary of binary variables.
                traditional_only: If true, only use the `pyqubo.Constraint` class for
                    transformations, not other algebraic expressions.

            Returns:
                An expression to add to the Hamiltonian, and the name for a placeholder
                for a multiplier.

            Raises:
                A `QuboTransformationException` if arguments are incorrect.
            """
            if not isinstance(comp.rhs, (int, float)):
                raise Exception("Comparison rhs not a number")
            if comp.sense is None:
                raise Exception("Comparison sense not set")
            xs = [vs[v] for v in comp.lhs.variables]
            t = f"{name}_{comp.sense.value}_{len(comp.lhs.variables)}"
            p = pq.Placeholder(t)

            terms = [(k, v) for k, v in comp.lhs.linear.items()]
            constant = comp.lhs.offset
            if comp.sense == Sense.Eq:
                lb = comp.rhs
                ub = comp.rhs
            elif comp.sense == Sense.Ge:
                lb = comp.rhs
                ub = np.iinfo(np.int64).max
            else:  # comp.sense == Sense.Le:
                lb = np.iinfo(np.int64).min
                ub = comp.rhs
            terms_upper_bound = sum(v for _, v in terms if v > 0)
            terms_lower_bound = sum(v for _, v in terms if v < 0)
            ub_c = min(terms_upper_bound, ub - constant)
            lb_c = max(terms_lower_bound, lb - constant)

            if lb_c > ub_c:
                raise ValueError("infeasible constraint")
            # TODO: add checks for the cases when: lb_c > ub_c: ValueError: infeasible
            # constraint terms_upper_bound <= ub_c and terms_lower_bound >= lb_c: WARN:
            # don't add constraint (always satisfied)

            slack_upper_bound = int(ub_c - lb_c)
            slack_integer = 0
            if slack_upper_bound != 0:
                slack_integer = pq.LogEncInteger(f"slack_{name}", (0, slack_upper_bound))

            # TODO: Add check to make sure all terms values == 1. What follows in only
            # correct if all terms values are 1.

            # fmt: off
            match (traditional_only, comp.sense, len(xs), comp.rhs):
                case (False, Sense.Ge, 2, 1):
                    x, y = xs
                    # P(1 - x - y + xy)
                    return p * pq.Constraint(1 - x - y + x * y, name), t
                case (False, Sense.Eq, 2, 1):
                    x, y = xs
                    # P(1 - x - y + 2xy)
                    return p * pq.Constraint(1 - x - y + 2 * x * y, name), t
                case (False, Sense.Le, _, 1):
                    # P(∑𝑥ᵢ𝑥ⱼ)
                    return p * pq.Constraint(sum(x * y for x, y in combinations(xs, 2)), name), t
                case (_, s, _, r):
                    relation = {Sense.Le: op.le, Sense.Eq: op.eq, Sense.Ge: op.ge}[s]
                    return p * (pq.Constraint(sum(xs), name, lambda x: relation(x, r)) + slack_integer - ub_c) ** 2, t
                case args:
                    # Shouldn't happen, this is just to appease pyright.
                    raise NotImplementedError(f"Unimplemented: {args}")
            # fmt: on

        def convert_cqm(
            cqm: ConstrainedQuadraticModel,
            strength: float = 5.0,
            traditional_only: bool = False,
        ) -> tuple[pq.Model, list[str]]:  # type: ignore
            """Convert a `dimod.ConstrainedQuadraticModel` into a `pyqubo.Model`.

            Args:
                cqm: Model to convert.
                strength: Passed to `pyqubo`'s `Model.compile`.
                traditional_only: If true, only use the `pyqubo.Constraint` class for
                    transformations, not other algebraic expressions.

            Returns:
                A compiled `pyqubo.Model` and a list placeholder names for the constraints.

            Raises:
                A `QuboTransformationException` if arguments are incorrect.
            """
            vs = {v: pq.Binary(v) for v in cqm.variables}
            objective_linear = pq.SubH(
                sum(vs[v] * cqm.objective.get_linear(v) for v in cqm.variables),
                label="orig_objective",
            )
            if not cqm.is_linear():
                raise Exception("Non-linear objective not supported")
            penalty, placeholders = pq.Num(0), []  # type: ignore
            for k, v in cqm.constraints.items():
                e, t = _to_expr(k, v, vs, traditional_only)
                penalty += e
                placeholders.append(t)
            return (objective_linear + penalty).compile(strength), placeholders

        def load_to_cqm(mps: str) -> ConstrainedQuadraticModel:
            """Load the LP from the MPS and convert it to a `ConstrainedQuadraticModel`."""

            with tempfile.NamedTemporaryFile(mode="+w", suffix=".mps") as tmp:
                tmp.write(mps)
                tmp.flush()
                m = po.Model()
                m.hideOutput()
                m.readProblem(tmp.name)

            with NamedTemporaryFile(suffix=".lp") as f:
                m.writeProblem(f.name, genericnames=True)
                return lp.load(f.name)

        # Convert BQM to Symmetric QUBO
        def bqm_to_symmetric_qubo(bqm: BinaryQuadraticModel):
            Q = np.zeros((bqm.num_variables, bqm.num_variables)).astype(np.float32)
            map = {m: i for i, m in enumerate(bqm.variables)}
            qubo, offset = bqm.to_qubo()
            for k, v in qubo.items():
                Q[map[k[0]], map[k[1]]] = v
            return (Q + Q.T) / 2.0, offset, map

        # Convert Symmetric QUBO to weights and bias (for TitanQ)
        def weights_and_bias(qubo: np.ndarray):
            # qubo, offset, map = bqm_to_symmetric_qubo(bqm)
            bias = qubo.diagonal()
            weights = qubo.copy() * 2  # factor of 2 due to TitanQ convention
            np.fill_diagonal(weights, 0)
            if np.any(weights != weights.T):
                raise ValueError("weights should be symmetric")
            return weights, bias

        model, placeholders = convert_cqm(load_to_cqm(self.model.data), 5.0, traditional_only=True)
        feed_dict = {p: 1.0 for p in placeholders}
        bqm = model.to_bqm(feed_dict=feed_dict)

        qubo, offset, map = bqm_to_symmetric_qubo(bqm)
        weights, bias = weights_and_bias(qubo)

        IQModel = SwInfinityQModel()
        IQModel.add_variable_vector("x", bqm.num_variables, Vtype.BINARY)
        IQModel.set_objective_matrices(weights, bias, Target.MINIMIZE)

        return IQModel, offset, map


class StrangeworksConverterFactory:
    @staticmethod
    def from_model(model_from: Any, model_to: Any, options: dict = {}) -> StrangeworksConverter:
        if isinstance(model_from, BinaryQuadraticModel) and model_to == jm.Problem:
            return StrangeworksBinaryQuadraticModelJiJProblemConverter(model=model_from)
        elif isinstance(model_from, MPSFile) and model_to == jm.Problem:
            return StrangeworksMPSFileJiJProblemConverter(model=model_from)
        elif isinstance(model_from, BinaryQuadraticModel) and model_to == QuboDict:
            return StrangeworksBinaryQuadraticModelQuboDictConverter(model=model_from)
        elif isinstance(model_from, BinaryQuadraticModel) and model_to == NECProblem:
            return StrangeworksBinaryQuadraticModelNECProblemConverter(model=model_from)
        elif isinstance(model_from, BinaryQuadraticModel) and model_to == FujitsuModelList:
            return StrangeworksBinaryQuadraticModelFujitsuDictConverter(model=model_from)
        elif isinstance(model_from, BinaryQuadraticModel) and model_to == HitachiModelList:
            return StrangeworksBinaryQuadraticModelHitachiDictConverter(model=model_from, options=options)
        elif isinstance(model_from, BinaryQuadraticModel) and model_to == MatrixMarket:
            return StrangeworksBinaryQuadraticModelMatrixMarketConverter(model=model_from)
        elif isinstance(model_from, BinaryQuadraticModel) and model_to == SwInfinityQModel:
            return StrangeworksBinaryQuadraticModelSwInfinityQModelConverter(model=model_from)
        elif isinstance(model_from, MPSFile) and model_to == SwInfinityQModel:
            return StrangeworksMPSFileSwInfinityQModelConverter(model=model_from)
        else:
            raise ValueError("Unsupported model type")
