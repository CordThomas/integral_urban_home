## General

This project offers a RESTful API to access near real-time data on home
intelligence provides a single API interface
to data about solar production, energy consumption, air quality, local climatalogical
information, home occupancy, and more.  The goal is that this will frame the
data foundation to program elements of the integral urban home 2.0.

The project also offers a simple web interface that consumes the data from the API
to demonstrate some of the data and ways in which to represent the data.

## News

## Dependencies

The API currently reads data from 3 repositories described below.  The repositories
store data from sensors and actuators in the modern urban home in near real time enabling the 
integration of information across otherwise siloed systems.

### Air Quality

An air quality sensor reads particulate matter as well as local temperature, 
relative humidity, and pressure.  The sensor collects the data every second and transmits 
it to the vendor's data warehouse roughly every 80 seconds.  An automated process
on the home network queries the sensor's API every 5 minutes to get the data.  Another 
approach would be to use the native ability to send the data
to a custom Data Processor which would be an end point that receives the sensor data
and stores it locally.

Details on the project that support this data collection is in [CordThomas/sunpower]

### Solar

Modern solar energy systems offer detailed data on the energy production as well
as the gross energy consumption of the home network.    For more detailed information
on energy consumption, there are a number of products on the market that can either
report on the consumption of each circuit in the home or even use machine learning
to identify individual consumers (TVs, washing machines, lights, etc.) and track their
consumption.  

The solar data provides information on the energy produced and consumed in 5 minute increments.  
The values are in kWh.

Details on the project that support this data collection is in [CordThomas/sunpower]

### Atmospheric conditions

To put the air quality, solar production and consumption and other factors into context, 
the integral urban home needs to understand the atmospheric conditions including outdoor
temperature, wind speed, water vapor, cloud cover and the azimuth of the sun.  This data
is collected every 5 minutes from the Weatherunderground API and stored locally.

Details on the project that support this data collection is in [CordThomas/darksky_datacollect]
