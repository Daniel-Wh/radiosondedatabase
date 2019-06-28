from flask import Flask, render_template
from flask_restful import Api
from datetime import datetime
from models.station_model import Launch, StationModel, OniData
from data_uploader import data_uploader
from dateutil.relativedelta import relativedelta
import sqlite3
from db import db


uri = 'sqlite:///data.db'
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = uri
api = Api(app)
db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()
    # data_uploader()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/vis')
def bokeh_route():
    begin_date = datetime(2000, 1, 1, 12)
    end_date = datetime(2010, 12, 31, 12)
    # dates = Launch.get_oni_launch_dates(begin_date, end_date, 0)
    # print(len(dates))
    s1readings = Launch.get_readings_by_dates_no_oni(begin_date, end_date, 1)
    dates = []
    while begin_date != end_date:
        dates.append(begin_date)
        begin_date = begin_date + relativedelta(days=+1)
    # s2readings = Launch.get_readings_by_date_with_oni(dates, 2, 0)
    print(len(s1readings))

    #nprint(len(s2readings))

    # station_1_readings = Launch.get_readings_by_dates_no_oni(datetime(2013, 1, 1, 0), datetime(2013, 12, 31, 0), 1)
    # station_2_readings = Launch.get_readings_by_dates_no_oni(datetime(2013, 1, 1, 0), datetime(2013, 12, 31, 0), 2)

    from bokeh.plotting import figure
    from bokeh.io import output_file, save
    from bokeh.models import ColumnDataSource

    chart_data = {
        'date': dates,
        'y1': s1readings
    }
    output_file('templates\practice.html')
    source = ColumnDataSource(chart_data)
    line = figure(plot_width=1600, plot_height=800, x_axis_type='datetime')
    line.line(y='y1', x='date', color='blue', source=source)
    save(line)
    return render_template('practice.html')


if __name__ == '__main__':

    app.run()
