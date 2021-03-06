import json
import requests
from lxml import html
from collections import OrderedDict

def parse(source,destination,date):
	for i in range(5):
		try:
			url = "https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(source,destination,date)
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
			response = requests.get(url, headers=headers, verify=False)
			parser = html.fromstring(response.text)
			json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
			raw_json =json.loads(json_data_xpath[0] if json_data_xpath else '')
			flight_data = json.loads(raw_json["content"])

			flight_info  = OrderedDict() 
			lists=[]
			timings = []
			for i in flight_data['legs'].keys():
				total_distance =  flight_data['legs'][i].get("formattedDistance",'')
				exact_price = flight_data['legs'][i].get('price',{}).get('totalPriceAsDecimal','')

				departure_location_airport = flight_data['legs'][i].get('departureLocation',{}).get('airportLongName','')
				departure_location_city = flight_data['legs'][i].get('departureLocation',{}).get('airportCity','')
				departure_location_airport_code = flight_data['legs'][i].get('departureLocation',{}).get('airportCode','')
				
				arrival_location_airport = flight_data['legs'][i].get('arrivalLocation',{}).get('airportLongName','')
				arrival_location_airport_code = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCode','')
				arrival_location_city = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCity','')
				airline_name = flight_data['legs'][i].get('carrierSummary',{}).get('airlineName','')
				
				no_of_stops = flight_data['legs'][i].get("stops","")
				flight_duration = flight_data['legs'][i].get('duration',{})
				flight_hour = flight_duration.get('hours','')
				flight_minutes = flight_duration.get('minutes','')
				flight_days = flight_duration.get('numOfDays','')

				if no_of_stops==0:
					stop = "Nonstop"
				else:
					stop = str(no_of_stops)+' Stop'

				total_flight_duration = "{0} days {1} hours {2} minutes".format(flight_days,flight_hour,flight_minutes)
				departure = departure_location_airport+", "+departure_location_city
				arrival = arrival_location_airport+", "+arrival_location_city
				carrier = flight_data['legs'][i].get('timeline',[])[0].get('carrier',{})
				plane = carrier.get('plane','')
				plane_code = carrier.get('planeCode','')
				formatted_price = "{0:.2f}".format(exact_price)

				if not airline_name:
					airline_name = carrier.get('operatedBy','')
				
				for timeline in  flight_data['legs'][i].get('timeline',{}):
					if 'departureAirport' in timeline.keys():
						departure_airport = timeline['departureAirport'].get('longName','')
						departure_time = timeline['departureTime'].get('time','')
						arrival_airport = timeline.get('arrivalAirport',{}).get('longName','')
						arrival_time = timeline.get('arrivalTime',{}).get('time','')
						flight_timing = {
											'departure_airport':departure_airport,
											'flight_hour' : flight_hour,
											'flight_minutes': flight_minutes,
											'departure_time':departure_time,
											'price': exact_price,
											'aircraft':plane,
											'flight_number': timeline.get('carrier').get('flightNumber'),
											'airline': airline_name,
											'arrival_airport':arrival_airport,
											'arrival_time':arrival_time
						}
						timings.append(flight_timing)
			return timings
		
		except ValueError:
			print ("Rerying...")
			
		return {"error":"failed to process the page",}


def callExpedia(source, destination, date):
	
	print ("Fetching flight details")
	scraped_data = parse(source,destination,date)
	return scraped_data