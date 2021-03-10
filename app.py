import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import datetime as dt

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

inspect=inspect(engine)
print(inspect.get_table_names())

measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    print("Someone's looking at home page.")
    return (
        f"Welcome to Honolulu Weather, your number 1 source for weather updates in your favorite vacation paradise!<br/> <br/>"
        f"These routes are available:,<br/> <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<start><br/>"
        f"/api/v1.0/range/<start>/<end>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_ago

    results = session.query(measurement.date,measurement.prcp).\
    filter(measurement.date > year_ago).order_by(measurement.date).all()
    
    session.close()

    daily_precipitation = []
    for date, inches in results:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Inches"] = inches
        daily_precipitation.append(precip_dict)
    
    return jsonify(daily_precipitation)
 
@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    station_results = session.query(station.id, station.name, station.station,\
        station.latitude,station.longitude)

    session.close()

    station_list = []
    for id,name,station_code,latitude, longitude in station_results:
        station_dict = {}
        station_dict["ID #"] = id
        station_dict["Name"] = name
        station_dict["Station Code"] = station_code
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_list.append(station_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    session = Session(engine)
    sel = [measurement.station, func.count(measurement.date),station.id]
    most_active = session.query(*sel).filter(measurement.station==station.station).group_by(station.station).\
    order_by(func.count(measurement.date).desc()).first()
    
    temp_results = session.query(measurement.date, measurement.tobs,measurement.station)\
        .filter(measurement.date > year_ago).filter(measurement.station==most_active[2]).all()

    session.close()

    temps_list = []
    for date,temp,stat in temp_results:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature"] = temp
        temp_dict["Station"] = stat
        temps_list.append(temp_dict)

    return jsonify(temps_list)

@app.route("/api/v1.0/start/<start>")
def start(start):
    
    session=Session(engine)

    sel = [func.strftime("%Y-%m-%d", measurement.date),func.min(measurement.tobs), func.avg(measurement.tobs), \
    func.max(measurement.tobs)]

    start_date_results = session.query(*sel).filter(func.strftime("%Y-%m-%d", measurement.date) >= start).\
    group_by(func.strftime("%Y-%m-%d", measurement.date)).all()

    session.close()

    start_temps = []
    for date, tmin, tmax, tavg in start_date_results:
        start_dict = {}
        start_dict['Date'] = date
        start_dict['TMIN'] = tmin
        start_dict['TMAX'] = tmax
        start_dict['TAVG'] = tavg
        start_temps.append(start_dict)
    
        return jsonify(start_temps)

@app.route("/api/v1.0/range/<start>/<end>")
def range(start,end):
    
    session=Session(engine)

    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), \
    func.max(measurement.tobs)]

    range_results = session.query(*sel).filter(func.strftime("%Y-%m-%d", measurement.date) >= start).\
    filter(func.strftime("%Y-%m-%d", measurement.date) <= end).all()

    session.close()

    range_temps = []
    for tmin, tmax, tavg in range_results:
        start_dict = {}
        start_dict['TMIN'] = tmin
        start_dict['TMAX'] = tmax
        start_dict['TAVG'] = tavg
        range_temps.append(start_dict)
    
        return jsonify(range_temps)
            
if __name__ == '__main__':
    app.run(debug=True)

    
    