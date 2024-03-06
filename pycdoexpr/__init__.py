import math
import re
import os
from dataclasses import dataclass
import pickle

from .util import *

from binarytree import Node


@dataclass
class decision_tree_node:
    node_type: str
    value: str
    number: int
    child_number: tuple

    def __hash__(self):
        return self.value


class CdoExpr:
    def __init__(self) -> None:
        pass

    def digitize(
        self, varname: str, bins: list, map_indices: list = None, right: bool = False
    ) -> str:
        """generate digtize expr which returns the indices of the bins
        to which each varname value in input array belongs, and if map_indices
        is given the func return the map_indices[indices] value

        Usage:
        same as np.digitize

        Args:
            varname (str): varname in expr
            bins (list): bins values list
            map_indices (list, optional): map_indices list. Defaults to None then return indices.
            right (bool, optional): if equal operator in the right (greater than: bins[i-1]< x <=bins[i]). Defaults to False (not less than: bins[i-1]<= x <bins[i]).

        Raises:
            ValueError: _description_

        Returns:
            str: _description_
        """
        try:
            from numpy.core.multiarray import _monotonicity

            mono = _monotonicity(bins)
        except ImportError:
            mono = math.copysign(1, bins[1] - bins[0])

        if mono == 0:
            raise ValueError("bins must be monotonically increasing or decreasing")

        if map_indices is None:
            if mono == -1:
                map_indices = list(range(len(bins), -1, -1))
            else:
                map_indices = list(range(len(bins) + 1))

        cond_operator = self._gt_cond_patt() if right else self._nlt_cond_patt()
        if mono == -1:
            return self._cond_compare_operator(
                varname, cond_operator, bins, map_indices
            )
        else:
            return self._cond_compare_operator(
                varname, cond_operator, bins[::-1], map_indices[::-1]
            )

    def conditions(self, parag: str, verbose: bool = False) -> str:
        """parse python-syntax paragraph

        Args:
            parag (str): paragraph
            verbose (bool, optional): print condtion tree or not. Defaults to True.

        Returns:
            str: expr
        """
        sentences = [p for p in parag.split("\n") if len(p)]
        kw_list, cond_list, value_list = self.parse_sentences(sentences)
        root = construct_tree(kw_list, cond_list)
        leaves = [i for i in root.postorder if i.value in [0, 1]]
        for l, i in zip(leaves, value_list):
            l.value = i.value
        if verbose:
            root.pprint()
        expr = construct_expr(root)
        return expr

    def moore_voting(self, voters: list, varname: str = "MAJOR") -> str:
        """generate moore vote expression

        Args:
            voters (list): voter varname in file
            varname (str, optional): output varname. Defaults to 'MAJOR'.

        Returns:
            str: expr
        """

        expr = "_count=0;\n"
        expr += f"{varname}=0;\n"
        expr += f"_tmp={varname};\n"
        for v in voters[:]:

            tmp_expr = self.conditions(
                f"""
                if _count == 0:
                    _tmp = {v}
                else:
                    _tmp = _tmp
                """
            )
            expr += f"_tmp={tmp_expr};\n"
            count_expr = self.conditions(
                f"""
                if _count == 0:
                    _count = 1
                else:
                    if {varname} == {v}:
                        _count = _count + 1
                    else:
                        _count = _count - 1
                """
            )
            expr += f"_count={count_expr};\n"
            expr += f"{varname}=_tmp;\n"

        return expr

    def _cond_compare_operator(
        self, varname: str, patt: str, bins: list, map_list: list
    ):
        expr = None
        assert len(bins) == len(map_list) - 1
        if len(map_list) == 2:
            expr = patt.format(
                varname=varname,
                bin_value=bins[0],
                true_value=map_list[0],
                false_value=map_list[1],
            )
            return expr
        else:
            last_expr = self._cond_compare_operator(
                varname, patt, bins[1:], map_list[1:]
            )
            expr = patt.format(
                varname=varname,
                bin_value=bins[0],
                true_value=map_list[0],
                false_value=f"({last_expr})",
            )
            return expr

    def _nlt_cond_patt(self) -> str:
        return "(({varname}>={bin_value}))? {true_value}:{false_value}"

    def _gt_cond_patt(self) -> str:
        return "(({varname}>{bin_value}))? {true_value}:{false_value}"

    def _lt_cond_patt(self) -> str:
        return "(({varname}<{bin_value}))? {true_value}:{false_value}"

    def _ngt_cond_patt(self) -> str:
        return "(({varname}<={bin_value}))? {true_value}:{false_value}"

    def _cond_patt(self) -> str:
        return "((condition))? (true_value): (false_value)"

    def parse_sentences(self, sentences: list) -> tuple:
        """parse sentences as keyward list, condition list and value list

        Args:
            sentences (list): sentences list

        Returns:
            tuple: kw_list, cond_list, value_list
        """
        kw_list = []
        cond_list = []
        value_list = []
        for s in sentences:
            node = self.parse_sentence(s)
            if node is None:
                if "else" in s:
                    kw_list.append("else")
            else:
                if node.node_type == "condition":
                    if "elif" in s:
                        kw_list.append("else")
                        kw_list.append("if")
                        cond_list.append(node)
                    else:
                        kw_list.append("if")
                        cond_list.append(node)
                elif node.node_type == "value":
                    value_list.append(node)
        return kw_list, cond_list, value_list

    def parse_sentence(self, sentence: str) -> decision_tree_node:
        """match single sentence as cond/value node

        Args:
            sentence (str): str

        Returns:
            decision_tree_node: conditon / value node
        """
        cond_pattern = "^([\s\t^i]+if|[\s\t^i]+elif|if|elif)\s+([^\:]+)\:"
        value_pattern = "^([\s\t]+)([A-Za-z\_\d]+[\s=]+[A-Za-z\d\s\+\.\-\_]+)"
        match = re.match(cond_pattern, sentence)
        indent_pattern = "^([\s\t]+)(if|else|^\s[A-Za-z\s\d\.=]+)"
        if match:
            match_indent = re.match(indent_pattern, match[1])
            indent = len(match_indent[1]) / 4 if match_indent else 0
            return decision_tree_node(
                node_type="condition", value=match[2], number=indent, child_number=()
            )
        else:
            match = re.match(value_pattern, sentence)
            if match:
                indent = len(match[1]) / 4
                return decision_tree_node(
                    node_type="value", value=match[2], number=indent, child_number=()
                )
        return None

    def parse_xgb_sentence(self, sentence: str) -> decision_tree_node:
        """match single sentence as cond/value node

        Args:
            sentence (str): str

        Returns:
            decision_tree_node: conditon / value node
        """
        cond_pattern = (
            "^([\s\t]+\d+|\d+):\[([^\s]+)\]\syes=(\d+),no=(\d+),missing=(\d+)"
        )
        value_pattern = "^([\s\t]+\d+|\d+):(leaf=[^\s]+)"
        match = re.match(cond_pattern, sentence)
        indent_pattern = "^([\s\t]+|)(\d+)"
        if match:
            match_number = re.match(indent_pattern, match[1])
            number = int(match_number[2])
            child = int(match[3]), int(match[4])
            return decision_tree_node(
                node_type="condition", value=match[2], number=number, child_number=child
            )
        else:
            match = re.match(value_pattern, sentence)
            if match:
                match_number = re.match(indent_pattern, match[1])
                number = int(match_number[2])
                return decision_tree_node(
                    node_type="value", value=match[2], number=number, child_number=()
                )
        return None

    def parse_xgb_single_tree(self, xgb_tree: str) -> Node:
        """parse xgb single tree text to binary tree node

        Args:
            xgb_tree (str): str

        Returns:
            Node: binary tree node
        """
        sentences = xgb_tree.split("\n")
        nodes = {}
        for s in sentences:
            n = self.parse_xgb_sentence(s)
            if n is not None:
                nodes[n.number] = n

        root = construct_tree_with_tree_nodes(nodes)
        return root

    def xgb_decision_trees(self, pkl: str, ensemble: str) -> str:
        with open(pkl, "rb") as f:
            m = pickle.load(f)
        booster = m.get_booster()
        trees = booster.get_dump()

        result_expr = ""
        ensemble_list = []
        for i, tree in enumerate(trees):
            tree_root = self.parse_xgb_single_tree(tree)
            expr = construct_expr(tree_root)
            result_expr += f"_VALUE{i}={expr};\n"
            ensemble_list.append(f"_VALUE{i}")

        if ensemble == "averaging":
            result_expr += (
                f"VALUE=({'+'.join(ensemble_list)}) / {len(ensemble_list)};\n"
            )
        elif ensemble == "boosting":
            result_expr += f"VALUE={'+'.join(ensemble_list)};\n"
        elif ensemble == "moore_voting":
            result_expr += self.moore_voting(ensemble_list, "VALUE")

        return result_expr


def test():
    e = CdoExpr()
    expr = e.digitize(
        "wind",
        [
            61.3,
            56.0,
            50.9,
            46.1,
            41.4,
            36.9,
            32.6,
            28.5,
            24.5,
            20.8,
            17.2,
            13.9,
            10.8,
            8.0,
            5.5,
            3.4,
            1.6,
            0.3,
        ],
    )
    print(expr)


if __name__ == "__main__":
    test()
