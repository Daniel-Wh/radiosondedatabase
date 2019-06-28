from datetime import datetime
from siphon.simplewebservice.igra2 import IGRAUpperAir
from models.station_model import Launch, StationModel, OniData, Reading


######### Code below used to populate stationdata database ##########


def data_uploader():
    z = 0
    y = 0
    stations = ['USM00072250', 'USM00072251']
    while z < 2:
        beginning = [datetime(2000, 1, 1), datetime(2010, 12, 31)]
        station_name = str(stations[z])
        df, header = IGRAUpperAir.request_data(beginning, station_name)

        x = 0
        station = StationModel(station_name, header['latitude'][0], header['longitude'][0])
        station.save_to_db()
        test = df.notnull()
        date_test = 0
        while x < len(df['height']):
            year = df['date'][x].strftime("%Y")
            month = df['date'][x].strftime("%m")
            oni = OniData.find_by_date(int(year), int(month))
            if test['temperature'][x] and test['height'][x]:
                if date_test != df['date'][x]:
                    launch_data = Launch(df['date'][x], oni, z + 1)
                    launch_data.save_to_db()
                    date_test = df['date'][x]
                    y += 1
                reading = Reading(int(df['height'][x]), df['temperature'][x], y)
                reading.save_to_db()
            x += 1
        z += 1


###### code used to create initial ONI database #######
def unadjusted_oni_uploader():
    file = open('ONI.txt')
    lines = file.readlines()
    file.close()

    oni_data = []
    for line in lines:
        line = line.strip()
        oni_data.append(line)

    month = []
    year = []
    oni = []

    for item in oni_data:
        month.append(item[0:3])
        year.append(int(item[4:8]))
        oni.append(float(item[17:22]))


######## code used to create updated ONI Database, changing values of month and ONI Index ####
def adjusted_oni_uploader():
    file = open('ONI.txt')
    lines = file.readlines()
    file.close()

    oni_data = []
    for line in lines:
        line = line.strip()
        oni_data.append(line)

    month = []
    year = []
    oni = []

    for item in oni_data:
        month.append(item[0:3])
        year.append(int(item[4:8]))
        oni.append(float(item[17:22]))

    updated_month = []

    x = 1
    y = 0
    while y < len(year):
        if x < 13:
            updated_month.append(x)
            x += 1
            y += 1
        elif x >= 13:
            x = 1
            updated_month.append(x)
            x += 1
            y += 1

    updated_oni = []
    for index in oni:
        if index <= -.5:
            updated_oni.append(-1)
        elif -.5 < index < .5:
            updated_oni.append(0)
        else:
            updated_oni.append(1)
    print(year, updated_month, updated_oni)
    z = 4
    while z < len(updated_month):
        oni_upload = OniData(year[z], updated_month[z], updated_oni[z - 4])
        oni_upload.save_to_db()
        z += 1

    print(updated_oni)