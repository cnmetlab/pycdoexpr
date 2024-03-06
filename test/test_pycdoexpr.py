from pycdoexpr import cdoexpr


def test_digitize():
    cexpr = cdoexpr()
    wind_level_bins = [
        0.3,
        1.6,
        3.4,
        5.5,
        8.0,
        10.8,
        13.9,
        17.2,
        20.8,
        24.5,
        28.5,
        32.6,
        36.9,
        41.4,
        46.1,
        50.9,
        56.0,
        61.3,
    ]
    wind_level = range(0, len(wind_level_bins) + 1)
    expr = cexpr.digitize("WIND", wind_level_bins, wind_level, right=False)


def test_conditions():
    cexpr = cdoexpr()
    s = """
    if PRE1H > 0.001:
        if TEM2 >= 3:
            if PRE1H < 0.1:
                WW = 51
            elif PRE1H < 2.5:
                WW = 61
            elif PRE1H < 8:
                WW = 62
            else:
                WW = 63
        elif TEM2 >=0:
            if PRE1H < 2.5:
                WW = 66
            else:
                WW = 67
        else:
            if PRE1H < 0.1:
                WW = 71
            elif PRE1H < 0.2:
                WW = 73
            else:
                WW = 75
    else:
        if VIS > 10000:
            if TCC > 80:
                WW = 3
            elif TCC > 40:
                WW = 2
            else:
                WW = 0
        elif VIS >= 1000:
            if RHU2 > 80:
                WW = 45
            elif RHU2 > 50:
                WW = 48
            else:
                WW = 31
        else:
            if WS10 < 1:
                WW = 45
            else:
                if RHU2 >=50:
                    WW = 45
                else:
                    WW = 34
    """
    expr = cexpr.conditions(s, verbose=True)


def test_moore_voting():
    cexpr = cdoexpr()
    expr = cexpr.moore_voting(["a", "b", "c"], "MAJOR")


def test_xgb_decision_trees():
    cexpr = cdoexpr()
    expr = cexpr.xgb_decision_trees("./static/model.pkl", ensemble="averaging")
