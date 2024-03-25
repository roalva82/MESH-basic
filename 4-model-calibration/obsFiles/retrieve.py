
from owslib.ogcapi.features import Features
import pandas as pd
from pathlib import Path
import logging
import copy 
from datetime import date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retrieve_data_from_api(stations, collection, download_variable,datetime_column, api_url, output_dir,other_variables=[],time_limits=False, start_date=None, end_date=None, limit=10000):

	# Set the time limits for the data retrieval
	if time_limits:
		time_ = f"{start_date}/{end_date}"
		logger.info(f"Retrieving {download_variable} from {collection} for the period {time_}")
	else:
		logger.info(f"Retrieving {download_variable} from {collection} with no time limits")

    # Set columns to be saved to the dataframe
	query_variables = [
					"STATION_NUMBER",
					]
    
    # Append additional query variables
	query_variables.append(datetime_column)
	query_variables.append(download_variable)
	query_variables = query_variables + other_variables
	save_columns = query_variables

	logger.info(f"Query variables: {query_variables}")

    # Output data frame to csv file
	collection_output_dir = Path(output_dir,collection)
	collection_output_dir.mkdir(parents=True, exist_ok=True)
	logger.info(f"Output directory: {collection_output_dir}")

    # Instansiate features
	oafeat = Features(api_url)
    
    # List of stations with no water level data
	stations_with_data = copy.copy(stations)
	stations_without_data = []

    # Data retrieval and creation of the data frames
	for station in stations:
		if time_limits:
           # Retrieval of water level data
			hydro_data = oafeat.collection_items(
				collection,
				limit=limit,
				STATION_NUMBER=station,
				datetime=time_,
			)
		else:
            # Retrieval of water level data
			hydro_data = oafeat.collection_items(
				collection,
				limit=limit,
				STATION_NUMBER=station,
			)

        # Creation of a data frame if there is data for the chosen time period
		if hydro_data["features"]:
            
            # Creation of a dictionary in a format compatible with Pandas
			historical_data_format = [
				{
					"LATITUDE": el["geometry"]["coordinates"][1],
					"LONGITUDE": el["geometry"]["coordinates"][0],
					**el["properties"],
				}
				for el in hydro_data["features"]
			]

            # Creation of the data frame
			historical_data_df = pd.DataFrame(
				historical_data_format,
				columns=save_columns,
			)
            
            # Detect and convert data types of columns
			historical_data_df = historical_data_df.infer_objects(copy=False)

            # Creating an index with the date in a datetime format
			historical_data_df[datetime_column] = pd.to_datetime(
				historical_data_df[datetime_column]
			)
			historical_data_df.set_index([datetime_column], inplace=True, drop=True)
            
			output_csv_path = Path(collection_output_dir,f'{station}_{download_variable}.csv')
			historical_data_df.to_csv(output_csv_path, index=True)

			logger.info(f"{download_variable} from {collection} for station {station} output to {output_csv_path}")
        
        # If there is no data for the chosen time period, the station
        # will be removed from the dataset
		else:
			stations_without_data.append(station)


    # Removing hydrometric stations without water level data from the station list
	for station in stations_without_data:
		logger.warning(
			f"Station {station} has no {download_variable} data for the chosen time period."
		)
		stations_with_data.remove(station)

    # Raising an error if no station is left in the list
	if not stations:
		stations_with_data = []
		raise ValueError(
			f"No {download_variable} data was returned from {collection}, please check the query."
		)
    
	return stations_with_data

def get_stations(province, collection, api_url):
	logger.info(f"Retrieving stations from {province} from {collection}")
	oafeat = Features(api_url)

	hydro_stations = oafeat.collection_items(
		collection,
		limit=10000,
		PROV_TERR_STATE_LOC=province
		)
	stations = [[el['id'], el['geometry']['coordinates'][1], el['geometry']['coordinates'][0]] for el in hydro_stations['features']]
	return stations

api_url = 'https://api.weather.gc.ca/openapi?f=json'
province = 'AB'
collection_stations = 'hydrometric-stations'
collection_data = 'hydrometric-daily-mean'
download_variable = "DISCHARGE"
datetime_column = "DATE"
output_dir = './'
start_date = "2005-01-01"
end_date = "2016-01-01"

stations = get_stations(province, collection_stations, api_url)
stations_id = [el[0] for el in stations]

stations_with_data = retrieve_data_from_api(stations_id, collection_data, download_variable, datetime_column, api_url, output_dir, [], time_limits=True, start_date=start_date, end_date=end_date)
stations_df = pd.DataFrame(stations_with_data)
stations_df.to_csv('./stations_with_data.csv')


