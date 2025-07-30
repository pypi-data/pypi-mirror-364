import numpy as np
import pandas as pd
from pathlib import Path
from missensemble import MissEnsemble

class Test_Missensemble:
    def test_init(self):
        data_pre = pd.DataFrame(
            {"X1": [1, np.nan, 3, 10, 12, 15], "X2": [-1, 5, 2, 9, np.nan, 15]}
        )
        missensemble = MissEnsemble(numerical_vars=["X1", "X2"])
        data_post = missensemble.fit_transform(data_pre)
        if data_post.convergence_:
            assert all(~data_post.isna().values)
