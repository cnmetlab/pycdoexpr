# pycdoexpr

![](static/digitize.jpg)

CDO (Climate data operator) is a high-efficient command line tool for climate and meteorology data processing. This Python package helps to generate complicated cdo expr(computing expression) in a convenient and pythonic way.

## Usage
1. generate digitize expr (same as np.digitize)
```python 
from pycdoexpr import cdoexpr
cexpr = cdoexpr()
cexpr.digitize(varname=varname, bins=bins, right=False)
```

2. convert multi-condition string in python syntax to expr
- [ ] TODO