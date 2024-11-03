import math
from matplotlib import pyplot
import numpy as np

def getX(Y,P,N):
    X = (P**N-1)*Y/P**N/(P-1)
    return X    

def getY(X,P,N):
    Y = P**N*(P-1)*X/(P**N-1)
    return Y

def getN(X,Y,P):
    M = math.log10(X/Y)+math.log10(P-1)
    N = -1*math.log(1-10**M,P)
    return N

def InterestTrend(X,Y,N,P):
    Result = list()
    RemainX = X
    for n in range(int(N)):
        Result.append(RemainX*(P-1)/12)
        RemainX = RemainX*P - Y
    Result = np.asarray(Result)
    pyplot.plot(Result)
    pyplot.ylabel("monthly paid interest")
    pyplot.xlabel("year")
    pyplot.show()

if __name__ == "__main__":
    X = 400000 #貸款金額
    y = 0 #月付
    p = 0.014 #利率
    N = 10 #總年份

    P = 1+p
    Y = y*12

    if N == 0:
        N = getN(X,Y,P)
        year = N//1
        month = N*12%12
        print("%d years %d Months to finish the loan"%(year,month))

    elif X == 0:
        X = getX(Y,P,N)
        price = X
        print("you can buy the house with the price %.2f"%price)

    elif Y == 0:
        Y = getY(X,P,N)
        MonthPay = Y/12
        print("Every month you need to pay %.2f"%MonthPay)
    print("With this setting you totally pay %.2f, which is %.2f times the money you loan"%(Y*N,Y*N/X))
    MonthlyPayInterest = InterestTrend(X,Y,N,P)     