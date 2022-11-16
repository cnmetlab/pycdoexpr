import math

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


def test():
    e = cdoexpr()
    expr = e.digitize('wind',[61.3, 56. , 50.9, 46.1, 41.4, 36.9, 32.6, 28.5, 24.5, 20.8, 17.2, 13.9, 10.8,  8. ,  5.5,  3.4,  1.6,  0.3])
    print(expr)

if __name__ == '__main__':
    test()