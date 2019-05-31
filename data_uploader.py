from datetime import datetime
from siphon.simplewebservice.igra2 import IGRAUpperAir
from models.station_model import StationData, StationModel

beginning = [datetime(2014, 9, 10, 0), datetime(2014, 9, 11, 0)]
station = 'USM00072250'

df, header = IGRAUpperAir.request_data(beginning, station)


date = df['date'][0].strftime("%Y%m%d")
print(date)

time = df['date'][0].strftime("%H")
print(time)
print(df['temperature'])

