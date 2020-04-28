import csv
import pandas as pd


threshold = 0.15
freqexp = 48000
filename = 'Analog_Trace'
input_file = filename + '.csv'

# rise | fall
edge = 'rise'

df = pd.read_csv(input_file)

print("Sample Rate (MHz): " + (df.loc[6,'Analog:0']))

df = pd.read_csv(input_file, skiprows=[i for i in range(1,12)])
df.columns = ['Time', 'Value']
df['Time'] = df['Time'].astype('float64')
df['Value'] = df['Value'].astype('float64')

ExpectedTime = 1/freqexp

df.loc[df['Value'] > threshold, 'CurrentState'] = 'high'
df.loc[df['Value'] <= threshold, 'CurrentState'] = 'low'

df['PrevState'] = df.CurrentState.shift(1)
df['PrevValue'] = df.Value.shift(1)
df['PrevTime'] = df.Time.shift(1)

if edge == 'rise':
    df.loc[(df['CurrentState'] == 'high') & (df['PrevState'] == 'low'), 'CrossPt'] = 'Y'

if edge == 'fall':
    df.loc[(df['CurrentState'] == 'low') & (df['PrevState'] == 'high'), 'CrossPt'] = 'Y'

df = df[df.CrossPt == 'Y']

#linear interpolation to find x: exact time crossing threshold
slope = (df['Value']-df['PrevValue'])/(df['Time']-df['PrevTime'])
exacttime = (threshold - df['PrevValue'])/slope + df['PrevTime']

df.insert(loc=len(df.columns), column='TimeAtThreshold', value=exacttime)

df['DeltaT'] = df.TimeAtThreshold - df.TimeAtThreshold.shift(1)

df = df.drop(['CurrentState', 'PrevState', 'PrevValue', 'PrevTime', 'CrossPt'], axis = 1)

df['SubExpT'] = df.DeltaT - ExpectedTime

NumberOfEdges = str(len(df.index))

print(df)

print("Number of edges is: " + NumberOfEdges)

df.to_csv(filename +'_out.csv')