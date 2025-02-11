# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect =True)



# Save references to each table

Measurement = Base.classes.measurement 
Station = Base.classes.station


# Create our session (link) from Python to the DB

session = Session(engine)



#################################################
# Flask Setup

app= Flask(__name__)





# Flask Routes
@app.route("/")

def homepage():
    return (
        f"Hawaii Climate Analysis API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"

    )



#### defining percip

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    #year_precip = session.query(Measurement.date, Measurement.prcp).\
    #filter(Measurement.date<= "2017-08-23").filter(Measurement.date>= "2016-08-23").order_by(Measurement.date).all()
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_percip= session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
    
    

    percip_dict= {date: prcp for date, prcp in year_percip}
    return jsonify(percip_dict)
    session.close()
#################################################



#return the stations

@app.route("/api/v1.0/stations")
def stations():

    stations= session.query(Station.station, Station.name).all()
    station_dict = {name: station for name, station in stations}

    return jsonify(station_dict)
    session.close()


#return the tobs

@app.route("/api/v1.0/tobs")
def tobs():
    
    tob_active= session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= dt.date(2016,8,18)).all()

#my one line loop didnt work so will type the whole thing out, assuming it has to look like a list of dictonaries

    tob_list =[]
    for date, tobs in tob_active:
        tob_dict = {}
        tob_dict["Date"] = date
        tob_dict["Temperature"] = tobs
        tob_list.append(tob_dict)

    return jsonify(tob_list)
    session.close()


#start date 
@app.route("/api/v1.0/temp/<start>")
def start_input(start):
    #print("input start date...")

    start= dt.datetime.strptime(start, "%m%d%Y")


#set variables as instructed 

    TMIN = func.min(Measurement.tobs)
    TMAX = func.max(Measurement.tobs)
    TAVG = func.avg(Measurement.tobs)
    
#return the query with the calcuated variables    

    results = session.query([TMIN, TMAX, TAVG]).filter(Measurement.date >=start).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)
        



#@app.route("/api/v1.0/<start>/<end>")
#def input_end():
def date_range(start, end):


    start= dt.datetime.strptime(start, "%m%d%Y")
    end= dt.datetime.strptime(end, "%m%d%Y")

#set variables as instructed 

    TMIN = func.min(Measurement.tobs)
    TMAX = func.max(Measurement.tobs)
    TAVG = func.avg(Measurement.tobs)
    
#return the query with the calcuated variables    

    rresults = session.query([TMIN, TMAX, TAVG]).filter(Measurement.date >=start).filter(Measurement.date<=end).all()
    session.close()
    rtemps = list(np.ravel(rresults))
    return jsonify(rtemps=rtemps)
        
    
if __name__ == '__main__':
    app.run()