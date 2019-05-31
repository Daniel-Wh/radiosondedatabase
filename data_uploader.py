from datetime import datetime
from siphon.simplewebservice.igra2 import IGRAUpperAir
from models.station_model import StationData, StationModel

beginning = datetime(2014, 9, 10, 0)
station = 'USM00072250'

df, header = IGRAUpperAir.request_data(beginning, station)


date = df['time'][0].astype(str)
new_date = date.replace("-", "")
last_date = new_date[:8]
new_station = StationData(last_date, 1, df['height'][0], df['temperature'][0], 1)
print(new_station)


print(date)
print(type(date))

