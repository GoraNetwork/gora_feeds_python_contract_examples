

# PRICE PAIR REQUEST SOURCE SPEC
# THIS IS FOR THE CLASSIC ORACLE REQUEST
pricePairSource = {
    "sourceId":7,
    "queryArgs":[ 
        b"##signKey", # API endpoint access key
        b"btc", 
        b"usd" 
    ]
}


# GORA SOURCE SPEC FOR FLIGHT DATA
# THIS IS FOR THE CLASSIC ORACLE REQUEST
# [ "##env:GORA_FLIGHTS_KEY", "arrival", "NBO", "EK719", "$.flight_status" ] 
flightDataSource = {
    "sourceId":26,
    "queryArgs":[
        b"##signKey", # API endpoint access key
        b"arrival", # Flight direction
        b"ABC", # Airport IATA code query parameter
        b"KQ510", # Flight IATA code query parameter
        b"$.flight_status", # Value path
    ]
} 


# direction=arrival&airportCode=NBO&flightCode=KQ205&key=QRf49wM72TCIHRI2g2WeI9WGW

# SPORTS FEED BY HOME TEAM REQUEST SOURCE SPEC
# THIS IS FOR THE CLASSIC ORACLE REQUEST
sportsFeedSourceEntireMatchInfo = {
    "sourceId":24,
    "queryArgs":[
        b"##signKey", # API endpoint access key
        b"usa", # region
        b"soccer", # sport
        b"epl", # league
        b"2023-05-25", # date
        b"manchester+united", # hometeam
        b"$.data", # Value Path
    ]
} 

sportsFeedSourceOneTeamScore = {
    "sourceId":24,
    "queryArgs":[
        b"##signKey", # API endpoint access key
        b"usa", # region
        b"soccer", # sport
        b"epl", # league
        b"2023-05-25", # date
        b"manchester+united", # hometeam
        b"$.data.homeTeamScore", # Value Path
    ]
} 


# GORA SOURCE SPEC FOR WEATHER DATA
# THIS IS FOR THE CLASSIC ORACLE REQUEST
# [ "##env:GORA_WEATHER_KEY", "Spain", "Madrid", "metric", "$.data.feelsLike","$.timestamp" ]
weatherFeedSource = {
    "sourceId":28,
    "queryArgs":[
        b"##signKey", # API endpoint access key
        b"Kenya", # Country query parameter
        b"Kiambu", # State query parameter
        b"Ruiru", # Area query parameter
        b"metric", # Unit of measure query parameter
        b"2023-07-13T12:00:00", # "Date and time parameter"
        # b"$.timestamp", # Timestamp path (JSONPath)
    ]
}


# CUSTOM SOURCE SPEC FOR GETTING DATA FROM A WEBPAGE USING REGEX
# THIS IS FOR THE CUSTOM ORACLE REQUEST
# THIS IS SCRAPING THE WEB PAGE FOR DATA AND RETURNING A SPECIFIC DATA FROM THE PAGE USING REGEX
webPageSource =  [
    [
        b"https://coinmarketcap.com/currencies/bnb/", # url
        b"", # auth_url
        b"regex:>BNB is (?:up|down) ([.0-9]+)% in the last 24 hours", # value_expr
        b"",# timestamp_expr
        0,# max_age
        1, # value_type
        0, # round_to
        b"",# gateway_url
        b"",# reserved_0
        b"",# reserved_1
        0,# reserved_2
        0,# reserved_3
    ]
]


# CUSTOM SOURCE SPEC FOR GETTING DATA FROM A WEBPAGE USING JSON API RETURN DATA
# THIS IS FOR THE CUSTOM ORACLE REQUEST
# THIS CALLS AN API (IT CAN BE A SELF HOSTED API) AND RETURNS THE JSON DATA FROM THE API
# THIS CALLS AN API AND RETURNS A RANDOM MATCH FACT EACH TIME IT'S CALLED
apiJsonSource =  [
    [
        b"https://catfact.ninja/fact", # url
        b"", # auth_url
        b"jsonpath:$.fact", # value_expr
        b"",# timestamp_expr
        0,# max_age
        0, # value_type
        0, # round_to
        b"",# gateway_url
        b"",# reserved_0
        b"",# reserved_1
        0,# reserved_2
        0,# reserved_3
    ]
]
