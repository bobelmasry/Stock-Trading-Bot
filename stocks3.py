import csv
import matplotlib.pyplot as plt

def getPercentageChange(currentValue, oldValue):
    change = (currentValue - oldValue) // oldValue
    return change * 100

def isAnomaly(arr, value):
    sum = 0
    for i in range(len(arr)):
        sum += arr[i]["Price"]
    avg = sum / len(arr)
    if (value["Price"] > (1.1 * avg)) or (value["Price"] < (0.9 * avg)):
        return True
    return False

def isBuyPosition(arr, value):
    sum = 0
    referencePrice = arr[0]["Price"]
    for i in range(len(arr)):
        sum += arr[i]["Price"]
    avg = sum / len(arr)
    if (getPercentageChange(avg, referencePrice) > -2.5) and (value >= referencePrice):
        return True
    return False

def makeBuyTrade(currentStockValue, day, date):
    global CurrentBalance, holdings, boughtPrice, buy_points
    if CurrentBalance < (startingBalance * 0.3):
        tradeValue = CurrentBalance
    else:
        tradeValue = CurrentBalance * 0.3
    numOfStocks = tradeValue // currentStockValue # Integer Division
    holdings.append([numOfStocks, currentStockValue])
    boughtPrice = currentStockValue
    buy_points.append((day, currentStockValue))
    print(f"Bought {numOfStocks} stocks at {currentStockValue}, current balance now equal to {CurrentBalance} at day {day}")
    print(holdings)
    print(CurrentBalance)

def isSellLosing(arr, currentStockValue):
    isAnomalyCount = 0
    isSell = False
    for i in range(len(arr)):
        if arr[i]["Price"] < currentStockValue * 0.97:
            isAnomalyCount += 1

    if currentStockValue < (boughtPrice * 0.85) or isAnomalyCount >= 3:
        isSell = True
    return isSell

def isSellWinning(arr):
    isAnomalyCount = 0
    for i in range(len(arr)):
        if isAnomaly(arr, arr[i]):
            isAnomalyCount += 1
    if isAnomalyCount >= 1:
        return True
    return False

def makeSellTrade(currentStockValue, day, date):
    global holdings, CurrentBalance, boughtPrice, sell_points
    if holdings != []:
        quantityBought = holdings[0][0]
        priceBought = holdings[0][1]
        amountDifference = (currentStockValue - priceBought) * quantityBought // 1 * 1
        if amountDifference != 0:
            holdings = []
            CurrentBalance += amountDifference
            if amountDifference > 0:
                print(f"Sold {quantityBought} stocks at {currentStockValue} with a gain of {amountDifference} at day {day}, current balance: {CurrentBalance}")
            else:
                print(f"Sold {quantityBought} stocks at {currentStockValue} with a loss of {amountDifference} at day {day}, current balance: {CurrentBalance}")
            sell_points.append((day, currentStockValue))
        boughtPrice = 0

# Load data from CSV file
data = []
with open("MNHD.csv", mode='r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        data.append({"Date": row["Date"], "Price": float(row["Price"])})

startingBalance = 10000
CurrentBalance = startingBalance
holdings = []
boughtPrice = 0

referencePoint = data[0]
currentData = []
buy_points = []
sell_points = []

for day in range(len(data)):
    # Find the index of referencePoint in data
    reference_index = data.index(referencePoint)

    # Include values between referencePoint and data[day]
    currentData = data[reference_index:day + 1]

    if currentData[-1]["Price"] < referencePoint["Price"] * 0.9:
        referencePoint = currentData[-1]

    if holdings == []:  # No current holdings
        if isBuyPosition(currentData, currentData[-1]["Price"]):
            print(currentData[-1]["Date"], "buy")
            makeBuyTrade(currentData[-1]["Price"], day, currentData[-1]["Date"])
            referencePoint = currentData[-1]  # Update referencePoint on buy

    elif data[day]["Price"] < boughtPrice:  # Currently holding and losing
        if isSellLosing(currentData, currentData[-1]["Price"]):
            print(currentData[-1]["Date"], "sell")
            makeSellTrade(currentData[-1]["Price"], day, currentData[-1]["Date"])
            referencePoint = currentData[-1]  # Update referencePoint on sell

    else:  # Currently holding and potentially winning
        if isSellWinning(currentData):
            makeSellTrade(currentData[-1]["Price"], day, currentData[-1]["Date"])
            referencePoint = currentData[-1]  # Update referencePoint on sell

# Plotting the results
days = [day for day in range(len(data))]
prices = [data[day]["Price"] for day in range(len(data))]

plt.figure(figsize=(14, 7))
plt.plot(days, prices, label='Stock Price', color='blue')

# Plot buy points
buy_days, buy_prices = zip(*buy_points) if buy_points else ([], [])
plt.scatter(buy_days, buy_prices, label='Buy Points', color='green', marker='^', s=100)

# Plot sell points
sell_days, sell_prices = zip(*sell_points) if sell_points else ([], [])
plt.scatter(sell_days, sell_prices, label='Sell Points', color='red', marker='v', s=100)

plt.xlabel('Days')
plt.ylabel('Price')
plt.title('Stock Price with Buy and Sell Points')
plt.legend()
plt.grid(True)
plt.show()
