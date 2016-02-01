def derive(y,x):
    return (
        (y[1:]-y[:-1])/(x[1:]-x[:-1]),
        (x[1:]+x[:-1])/2
    )
