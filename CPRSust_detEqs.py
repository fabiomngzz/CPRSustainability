def eq_resource_logistic(R, x, b, ehat, K=1):
    return b*(R*(1-R/K) - R*(x*ehat[0] + (1-x)*ehat[1]))

def eq_strategy(R,x,w=1):
    return -w*R*x*(1-x)

# define the HES to be used with numpy.solve_ivp
def HES(t,z,b,extractionRates):
    R = z[0]
    x = z[1]
    return [eq_resource_logistic(R, x, b, extractionRates),eq_strategy(R, x)]