import math
import re
from dataclasses import dataclass

from binarytree import Node

@dataclass
class cond_node:
    node_type: str
    value: str
    indent: int
    def __hash__(self):
        return self.value

class cdoexpr:
    def __init__(self) -> None:
        pass

    def digitize(self, varname:str, bins:list, map_indices:list=None, right:bool=False)->str:
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
            mono = math.copysign(1, bins[1]-bins[0])

        if mono == 0:
            raise ValueError("bins must be monotonically increasing or decreasing")

        if map_indices is None:
            if mono == -1:
                map_indices = list(range(len(bins),-1,-1))
            else:
                map_indices = list(range(len(bins)+1))

        cond_operator = self._gt_cond_patt() if right else self._nlt_cond_patt()
        if mono == -1:
            return self._cond_compare_operator(varname, cond_operator, bins, map_indices)
        else:
            return self._cond_compare_operator(varname, cond_operator, bins[::-1], map_indices[::-1])

    def _cond_compare_operator(self, varname:str, patt:str, bins:list,map_list:list):
        expr = None
        assert len(bins)==len(map_list)-1
        if len(map_list)==2:
            expr = patt.format(varname=varname,bin_value=bins[0],true_value=map_list[0],false_value=map_list[1])
            return expr
        else:
            last_expr = self._cond_compare_operator(varname, patt, bins[1:], map_list[1:])
            expr = patt.format(varname=varname,bin_value=bins[0],true_value=map_list[0],false_value=f'({last_expr})')
            return expr

    def _nlt_cond_patt(self)->str:
        return '(({varname}>={bin_value}))? {true_value}:{false_value}'

    def _gt_cond_patt(self)->str:
        return '(({varname}>{bin_value}))? {true_value}:{false_value}'

    def _lt_cond_patt(self)->str:
        return '(({varname}<{bin_value}))? {true_value}:{false_value}'

    def _ngt_cond_patt(self)->str:
        return '(({varname}<={bin_value}))? {true_value}:{false_value}'

    def _cond_patt(self)->str:
        return '((condition))? (true_value): (false_value)'

    def parse_sentences(self, sentences:list)->tuple:
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
                if 'else' in s:
                    kw_list.append('else')
            else:
                if node.node_type == 'condition':
                    if 'elif' in s:
                        kw_list.append('else')
                        kw_list.append('if')
                        cond_list.append(node)
                    else:
                        kw_list.append('if')
                        cond_list.append(node)
                elif node.node_type == 'value':
                    value_list.append(node)
        return kw_list, cond_list, value_list

    def parse_sentence(self, sentence:str)->cond_node:
        """match single sentence as cond/value node

        Args:
            sentence (str): str

        Returns:
            cond_node: conditon / value node
        """
        cond_pattern='^([\s\t^i]+if|[\s\t^i]+elif|if|elif)\s+([^\:]+)\:'
        value_pattern = '^([\s\t]+)([A-Za-z\d]+[\s=]+[A-Za-z\d\.]+)'
        match = re.match(cond_pattern, sentence)
        indent_pattern = '^([\s\t]+)(if|else|^\s[A-Za-z\s\d\.=]+)'
        if match:
            match_indent = re.match(indent_pattern, match[1])
            indent = len(match_indent[1])/4 if match_indent else 0
            return cond_node(node_type='condition', value=match[2], indent=indent)
        else:
            match = re.match(value_pattern, sentence)
            if match:
                indent = len(match[1])/4
                return cond_node(node_type='value', value=match[2], indent=indent)
        return None

    def _construct_tree(self,kw:list, cond:list)->Node:
        """construct condition binary tree with keyword list and condition list

        Args:
            kw (list): keyword list
            cond (list): condition list

        Returns:
            Node: binary tree root node
        """
        if len(kw)==2 and len(cond)==1 and kw[0]=='if' and kw[1] == 'else':
            left = Node(value=0)
            right = Node(value=1)
            root = Node(value=cond[0].value, left=left, right=right)
            return root
        else:
            stack = []
            for n,k in enumerate(kw):
                if k == 'if':
                    stack.append(n)
                elif k == 'else':
                    idx = stack.pop()
                if len(stack) == 0:
                    if_index = idx
                    else_index = n
                    break
            
            root = Node(value=cond[if_index].value)

            if if_index+1 == else_index:
                left = Node(0)
                right = self._construct_tree(kw[else_index+1:],cond[if_index+1:])
            elif if_index+1 < else_index:
                cond_num = kw[if_index+1:else_index-1].count('if')
                left = self._construct_tree(kw[if_index+1:else_index], cond[1:cond_num+1])
                if len(kw[else_index+1:])<=1:
                    right = Node(1)
                else:
                    right = self._construct_tree(kw[else_index+1:], cond[cond_num+1:])
        
            root.left = left
            root.right = right
            return root

    def _construct_expr(self, node:Node)->str:
        """construct cdo condition expr from binary tree root node

        Args:
            node (Node): root node

        Returns:
            str: expr str
        """
        patt = '(({condition}))? ({true_value}): ({false_value})'
        if node.max_leaf_depth == 1:
            res = patt.format(condition=node.value, true_value=node.left.value.split('=')[-1], false_value=node.right.value.split('=')[-1])
            return res
        else:
            if node.left.max_leaf_depth>=1:
                left = self._construct_expr(node.left)
            else:
                left = node.left.value.split('=')[-1]
            if node.right.max_leaf_depth>=1:
                right = self._construct_expr(node.right)
            else:
                right = node.right.value.split('=')[-1]
            res = patt.format(condition=node.value, true_value=left, false_value=right)
            return res

    def conditions(self, parag:str, verbose:bool=False)->str:
        """parse python-syntax paragraph

        Args:
            parag (str): paragraph
            verbose (bool, optional): print condtion tree or not. Defaults to True.

        Returns:
            str: expr
        """
        sentences = [p for p in parag.split('\n') if len(p)]
        kw_list, cond_list, value_list  = self.parse_sentences(sentences)
        root = self._construct_tree(kw_list, cond_list)
        leaves = [i for i in root.postorder if i.value in [0,1]]
        for l,i in zip(leaves,value_list):
            l.value = i.value
        if verbose:
            root.pprint()
        expr = self._construct_expr(root)
        return expr

def test():
    e = cdoexpr()
    expr = e.digitize('wind',[61.3, 56. , 50.9, 46.1, 41.4, 36.9, 32.6, 28.5, 24.5, 20.8, 17.2, 13.9, 10.8,  8. ,  5.5,  3.4,  1.6,  0.3])
    print(expr)

if __name__ == '__main__':
    test()