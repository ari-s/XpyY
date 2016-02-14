import time,numpy,datetime

dateStr = '%Y-%m-%d-%H:%M'
def strptime(data,dateStr=dateStr):
    first = datetime.datetime.strptime(data[0],dateStr)
    return numpy.array([ (datetime.datetime.strptime(i,dateStr) - first).total_seconds() for i in data ],dtype=float)

