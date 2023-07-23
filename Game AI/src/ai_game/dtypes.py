"""
This class will provide a number of high-level
categorical datatypes to work with in the project.
"""

import pandas as pd

ActionDType = pd.CategoricalDtype(["atk", "ddg", "blk"])
OutcomeDType = pd.CategoricalDtype(["damaged", "scored", "none"])
