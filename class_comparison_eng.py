'''

This code  aims to find the impact of the commisions payed by clients on
mutual funds' performance.

With that, a decision rule is set based on a threshold that defines the 
proportion of annualized return in terms of the return of Class A Funds 
that is accepted for the client to lose that increases the firm's revenues 
through higher trailer fees.

In addition, it finds those cases in which it is better to invest in
a mutual fund that pays less trailer fees to the firm but represent a 
significant outperformance for their portfolios.


'''

# Loading libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## Load data extracted from Bloomberg in an Excel File
df = pd.read_excel(r"C:\Users\portafolio\Documents\Solfin\Research\Class A vs Class C\class_comp.xlsx", 'Fondos - Valores', parse_dates=['Dates'])
df.set_index('Dates', inplace= True)

## Estimate daily returns
daily_returns= df.pct_change(1)

## Estimate annualized returns
ann = daily_returns.mean() * 252 * 100
ann_df = pd.DataFrame(ann)


## Select Class A and Class C Funds and store in new dataframes
ClassA = daily_returns.iloc[:, 0::2]
ClassC = daily_returns.iloc[:, 1::2]


## Create a Base 100 index for Class C Funds
ClassC_index = 100*np.exp(ClassC.cumsum())
ClassC_index.plot()
plt.title('Class C')
plt.show()
ClassC_index.info()

# Create a Base 99 index for Class A Funds 
# (Because when a client purchases a Class A Fund, a front-load comission of 1 % is charged)
ClassA_index = 99*np.exp(ClassA.cumsum())
ClassA_index.plot()
plt.title('Class A')
plt.show()
ClassA_index.info()

# Estimate historical spreads
spreads = pd.DataFrame(ClassA_index.values - ClassC_index.values)
spreads.columns = ClassA.columns.values
spreads.index = ClassA.index
spreads.info()

# Plot historical spreads (positive slope means Class A Funds outperform Class C Funds)
spreads.plot(subplots = True, layout = (6,6))
plt.title('Spreads históricos')
plt.show()


## Estimate spreads from annualized returns
# Selecting Class A and Class C Funds
ClassA_ann = ann.iloc[0::2]
ClassC_ann = ann.iloc[1::2]

## Plot annualized returns on an overlapped barchart
width = 0.8
indices = np.arange(len(ClassA_ann))
plt.bar(indices, (ClassA_ann*100), width=width, 
        color='b', label='Class A')
plt.bar([i+0.25*width for i in indices], (ClassC_ann *100), 
        width=0.5*width, color='r', alpha=0.8, label='Class C')
plt.xticks(ticks = range(0,len(ClassA_ann.index)), labels = ClassA_ann.index, rotation = 'vertical')
plt.legend()
plt.show()

# Estimate spread from annualized returns
diff_dfu = pd.Series(ClassA_ann.values - ClassC_ann.values)
diff_dfu.index = ClassA.columns.values

# Visualize spread distribution in a histogram
diff_dfu.hist(bins = 25)
plt.show()
    
# Visualize annualized spreads
diff_dfu.plot(kind = 'barh')
plt.show()

# Add a vertical line (defining the threshold) to the previous plot
xs = np.linspace(1, 21, 200)
plt.vlines(x=0.0075, ymin=0, ymax=len(xs), colors='green', ls=':', lw=2, label='Threshold')

# Scatter plot comparing annualized spreads with the lifespan of the fund
D = ClassA_index.count()
new = pd.concat([diff_dfu, D], axis = 1)
new.columns = ['Annualized Return Spreads', 'Length']
new.plot(kind = 'scatter', x = 'Length', y = 'Annualized Return Spreads') # Los spreads anualizados no tienen relación con la longitud de la vida del fondo
plt.show()

# Estimate spreads as a proportion of annualized return of Class A Fund
## This is the most notorious plot of the project. It clearly visualizes how Funds' performances diminished by the Commisions from Class C Funds
prop = pd.DataFrame((diff_dfu.values / abs(ClassA_ann.values))*100, index = ClassA_ann.index)
prop.sort_values(by = [0], ascending = 0, inplace = True)
prop.plot(kind = 'barh')
plt.title("Spread as a proportion of Class A Funds' annualized return")
plt.show()

# Histogram of spreds as proportions
prop.hist(bins = 30)
plt.title("Distribution of spreads as proportions of Class A Fund's annualized returns")
plt.show()


## Ammount of days that Class C outperforms Class A
neg = pd.DataFrame(spreads.lt(0).sum())
pos = pd.DataFrame(spreads.gt(0).sum())
tot = pd.DataFrame(spreads.count())
neg_ratio = neg/tot
pos_ratio = pos/tot
total = pd.concat([neg_ratio, pos_ratio], axis = 1)
total.columns = ['Class C', 'Class A']

# % of days on which Class A outperforms Class C
total.plot(kind = 'bar', stacked = True)
plt.show()

# Descriptive statistics on the ammount of days in which Class C outperforms Class A
neg.describe()
neg_ann = neg / 252
neg_ann.describe()
neg_cleaned = neg.drop(['NREAX US Equity','SGDWDAA LX Equity', 'SCHPFAA LX Equity', 'SCGCAIU LX Equity', 'TEMFIAI LX Equity', 'BWGIAAU ID Equity', 'IGFAAGU LX Equity', 'BASSBTA ID Equity'])
neg_cleaned_ann = neg_cleaned / 252
neg_cleaned_ann.describe()
neg_cleaned.describe()


# Histogram of the ammount of days that Class A take to outperform Class C (Excluding those mutual funds on which Class A never outperforms Class C)
neg_cleaned.hist(bins= 50)
xs = np.linspace(1, 21, 3)
plt.vlines(x=neg_cleaned.median(), ymin=0, ymax=len(xs), colors='green', ls=':', lw=2, label='Median')
plt.vlines(x=neg_cleaned.quantile(0.25), ymin=0, ymax=len(xs), colors='red', ls=':', lw=2, label='25th Percentile')
plt.vlines(x=neg_cleaned.quantile(0.75), ymin=0, ymax=len(xs), colors='red', ls=':', lw=2, label='75th Percentile')
plt.legend()
plt.title('Ammount of days that take Class A Funds to outperform Class C Funds (Excluding Class C outperformers)')
plt.show()


# Histogram with the frequencey of days that Class A takes to outperform Class C (Including all funds)
neg.hist(bins= 100)
xs = np.linspace(1, 21, 5)
plt.vlines(x=neg.median(), ymin=0, ymax=len(xs), colors='green', ls=':', lw=2, label='Mean')
plt.vlines(x=neg.quantile(0.25), ymin=0, ymax=len(xs), colors='red', ls=':', lw=2, label='25th Percentile')
plt.vlines(x=neg.quantile(0.75), ymin=0, ymax=len(xs), colors='red', ls=':', lw=2, label='75th Percentile')
plt.legend()
plt.title('Ammount of days that take Class A Funds to outperform Class C Funds')
plt.show()

# Histogram with the frequency of years that Class A take to outperform Class C (Excluding those mutual funds on which Class A never outperforms Class C)
neg_cleaned_ann.hist(bins= 50)
xs = np.linspace(1, 21, 3)
plt.vlines(x=neg_cleaned_ann.median(), ymin=0, ymax=len(xs), colors='green', ls=':', lw=2, label='Median')
plt.vlines(x=neg_cleaned_ann.quantile(0.25), ymin=0, ymax=len(xs), colors='red', ls=':', lw=2, label='25th Percentile')
plt.vlines(x=neg_cleaned_ann.quantile(0.75), ymin=0, ymax=len(xs), colors='red', ls=':', lw=2, label='75th Percentile')
plt.legend()
plt.title('Years that Class A Funds take to outperform Class C Funds')
plt.show()










'''

The following code aims to analyze the difference of specific mutual funds


'''


## Index base 100 for all of the Funds
df2 = 100*np.exp(daily_returns.cumsum())
df2.info()
df2.tail()
plt.plot(df2)

# Franklin Technology Funds (Class A and C)
ftech = df2.iloc[:, 10:12].dropna()
ftech.plot()
plt.title('Franklin Technology Fund')
plt.ylabel('Retorno (Indice Base 100)')
plt.show()

# MFS Limited Maturity Funds (Class A and C)
LM = df2.iloc[:, 26:28].dropna()
LM.plot()
plt.title('MFS Limited Maturity Bond Fund')
plt.ylabel('Return (Base 100 index)')
plt.show()

# Schroder Global Sustainable Growth (Class A and C)
GSG = df2.iloc[:, 4:6].dropna()
GSG.plot()
plt.title('Schroder Global Sustainable Growth Fund')
plt.ylabel('Retorno (Indice Base 100)')
plt.show()

# MFS Limited Maturity from the clients' perspective
full_df = pd.concat([ClassA_index, ClassC_index], axis = 1)
full_df.info()

MFSA = full_df['MFMLMAA LX Equity'].dropna()
MFSC = full_df['MFMLMCR LX Equity'].dropna()

MFSL = pd.concat([MFSA, MFSC], axis = 1)
MFSL.plot()
plt.title("MFS Limited Maturity Fund from the clients' perspective")
plt.ylabel('USD')
plt.show()

