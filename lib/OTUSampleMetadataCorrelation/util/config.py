from dotmap import DotMap

config = dict(
    debug=True, # toggle for debugging prints/conditionals
    rmd_flpth="/kb/module/lib/R/workflow.Rmd",
)

Var = DotMap(config)

def reset_Var():
    Var.clear()
    Var.update(config)
