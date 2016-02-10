def derive(x,y):
    return (
        (x[1:]+x[:-1])/2,
        (y[1:]-y[:-1])/(x[1:]-x[:-1])
    )
