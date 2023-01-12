# set up and dependencies
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.types import Date
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import func
from flask import Flask, jsonify
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import numpy as np
#set up base
Base = declarative_base()


#create class for measurement table
class Measurement(Base):
    __tablename__ = "measurement"
    
    id = Column(Integer, primary_key=True)
    station = Column(String)
    date = Column(String)
    prcp = Column(Float)
    tobs = Column(Float)


#create class for station table
class Station(Base):
    __tablename__ = "station"
    
    id = Column(Integer, primary_key=True)
    station = Column(String)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation =  Column(Float)


# create engine and session to link to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()
session = scoped_session(sessionmaker(bind=engine))


# establish app
app = Flask(__name__)


# create home page route
@app.route("/")
def main():
    return (
        f"Welcome to the Climate App Home Page!<br>"
       
        f"Precipitation last 12 months                                                     : /api/v1.0/precipitation<br>"
        
        f"A list of stations and station numbers                                           : /api/v1.0/stations<br>"

        f"Temperature observations at the most active station over the previous 12 months  : /api/v1.0/tobs<br>"
        f"Enter a start date (yyyy-mm-dd) at the end of url to get the info (--> Example:http://127.0.0.1:5000/api/v1.0/2019-10-25<--)               : /api/v1.0/<start><br>"
        f"Enter both a start and end date (yyyy-mm-dd) at the end of url to get the info (--> Example:http://127.0.0.1:5000/api/v1.0/2017-10-15/2018-10-15<--)   : /api/v1.0/<start>/<end><br>"
    )


# create precipitation route of last 12 months of precipitation data

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from Python to the DB
    session = Session(engine)

    # Query all precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    
    precipitation_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation_data.append(precipitation_dict)  

    return jsonify(precipitation_data)



# create station route of a list of the stations in the dataset
@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(Station.name, Station.station).all()

    # convert results to a dict
    stations_dict = dict(stations)

    # return json list of dict (I decided to do a dict instead of a list here to show both the station name and the station number)
    return jsonify(stations_dict)


# create tobs route of temp observations for most active station over last 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from Python to the DB
    session = Session(engine)
    
    # Latest date
    latest_date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latest_date = datetime.strptime(latest_date_query[0], '%Y-%m-%d').date()
    # Date 12 months ago
    date_one_year_ago = latest_date - relativedelta(months= 12)

    # Query for temperature in the last 12 months
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= date_one_year_ago).all()

    session.close()
    
    temperature_data = []
    for date, tobs in results:
        temperature_dict = {}
        temperature_dict["Date"] = date
        temperature_dict["Temperature"] = tobs
        temperature_data.append(temperature_dict)  

    return jsonify(temperature_data)

# create start and start/end route
# min, average, and max temps for a given date range
@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create session from Python to the DB
    session = Session(engine)

    start_date = datetime.strptime(start, '%Y-%m-%d').date()

    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    temps_stats_results = list(np.ravel(temperature_stats))
    
    min_temp = temps_stats_results[0]
    max_temp = temps_stats_results[1]
    avg_temp = temps_stats_results[2]
    
    temp_stats_data= []
    temp_stats_dict = [{"Start Date": start},
                       {"Minimum Temperature": min_temp},
                       {"Maximum Temperature": max_temp},
                       {"Average Temperature": avg_temp}]

    temp_stats_data.append(temp_stats_dict)
    
    return jsonify(temp_stats_data)


#------------------------------------------------

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create session from Python to the DB
    session = Session(engine)

    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    end_date = datetime.strptime(end, '%Y-%m-%d').date()

    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    temps_stats_results = list(np.ravel(temperature_stats))
    
    min_temp = temps_stats_results[0]
    max_temp = temps_stats_results[1]
    avg_temp = temps_stats_results[2]
    
    temp_stats_data = []
    temp_stats_dict = [{"Start Date": start_date},
                       {"End Date": end_date},
                       {"Minimum Temperature": min_temp},
                       {"Maximum Temperature": max_temp},
                       {"Average Temperature": avg_temp}]

    temp_stats_data.append(temp_stats_dict)
    
    return jsonify(temp_stats_data)

if __name__ == "__main__":
    app.run(debug=True)