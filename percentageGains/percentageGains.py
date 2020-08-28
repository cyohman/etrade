import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# logger settings
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler("python_client.log", maxBytes=5 * 1024 * 1024, backupCount=3)
FORMAT = "%(asctime)-15s %(message)s"
fmt = logging.Formatter(FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(fmt)
logger.addHandler(handler)


class PercentageGains:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    def quotes(self):
        """
        Calls quotes API to provide quote details for equities, options, and mutual funds
        :param self: Passes authenticated session in parameter
        """

        with open('symbols', 'r', newline='') as symbolsFile:
            symbols = symbolsFile.read().splitlines()

        symbols = sorted(symbols, key=str.upper)

        symbols = list(dict.fromkeys(symbols))

        os.rename('symbols', 'old_symbols_lists/symbols_'+datetime.now().strftime("%m-%d-%Y_%H:%M%S"))

        newSymbolsFile=open('symbols','w')

        for element in symbols:
             newSymbolsFile.write(element)
             newSymbolsFile.write('\n')

        newSymbolsFile.close()

	#declare a dictionary
        percentageGains = {}

        while (len(symbols)>0):
           joined_string = ",".join(symbols[0:25])
           symbols = symbols[25:]
           #print(joined_string)
        
           #        symbols = input("\nPlease enter Stock Symbol: ")

           # URL for the API endpoint
           url = self.base_url + "/v1/market/quote/" + joined_string + ".json"

           #print(url)

           # Make API call for GET request
           response = self.session.get(url)
           logger.debug("Request Header: %s", response.request.headers)

           if response is not None and response.status_code == 200:

               parsed = json.loads(response.text)
               logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))

               # Handle and parse response
               #print("")
               data = response.json()
               if data is not None and "QuoteResponse" in data and "QuoteData" in data["QuoteResponse"]:
                   for quote in data["QuoteResponse"]["QuoteData"]:
                       #if quote is not None and "dateTime" in quote:
                       #    print("Date Time: " + quote["dateTime"])
                       #if quote is not None and "Product" in quote and "symbol" in quote["Product"]:
                       #    print("Symbol: " + quote["Product"]["symbol"])
                       #if quote is not None and "Product" in quote and "securityType" in quote["Product"]:
                       #    print("Security Type: " + quote["Product"]["securityType"])
                       #if quote is not None and "All" in quote and "lastTrade" in quote["All"]:
                       #    print("Last Price: " + str(quote["All"]["lastTrade"]))
                       if quote is not None and "All" in quote and "changeClose" in quote["All"] \
                           and "changeClosePercentage" in quote["All"]:
                       #    print("Today's Change: " + str('{:,.3f}'.format(quote["All"]["changeClose"])) + " (" +
                       #       str(quote["All"]["changeClosePercentage"]) + "%)")
                           percentageGains[quote["Product"]["symbol"]] = quote["All"]["changeClosePercentage"]   
                       #if quote is not None and "All" in quote and "open" in quote["All"]:
                       #    print("Open: " + str('{:,.2f}'.format(quote["All"]["open"])))
                       #if quote is not None and "All" in quote and "previousClose" in quote["All"]:
                       #    print("Previous Close: " + str('{:,.2f}'.format(quote["All"]["previousClose"])))
                       #if quote is not None and "All" in quote and "bid" in quote["All"] and "bidSize" in quote["All"]:
                       #    print("Bid (Size): " + str('{:,.2f}'.format(quote["All"]["bid"])) + "x" + str(
                       #        quote["All"]["bidSize"]))
                       #if quote is not None and "All" in quote and "ask" in quote["All"] and "askSize" in quote["All"]:
                       #    print("Ask (Size): " + str('{:,.2f}'.format(quote["All"]["ask"])) + "x" + str(
                       #        quote["All"]["askSize"]))
                       #if quote is not None and "All" in quote and "low" in quote["All"] and "high" in quote["All"]:
                       #    print("Day's Range: " + str(quote["All"]["low"]) + "-" + str(quote["All"]["high"]))
                       #if quote is not None and "All" in quote and "totalVolume" in quote["All"]:
                       #    print("Volume: " + str('{:,}'.format(quote["All"]["totalVolume"])))
                   #print(percentageGains)
                   #print(sorted(percentageGains))
                   #print(sorted(percentageGains.items(), key=lambda x: x[1], reverse=True))
               else:
               # Handle errors
                   if data is not None and 'QuoteResponse' in data and 'Messages' in data["QuoteResponse"] \
                       and 'Message' in data["QuoteResponse"]["Messages"] \
                       and data["QuoteResponse"]["Messages"]["Message"] is not None:
                       for error_message in data["QuoteResponse"]["Messages"]["Message"]:
                            print("Error: " + error_message["description"])
                   else:
                       print("Error: Quote API service error")
           else:
               logger.debug("Response Body: %s", response)
               print("Error: Quote API service error")
        print() 
        sorted_pg = sorted(percentageGains.items(), key=lambda x: x[1], reverse=False)
        print(*sorted_pg, sep = "\n")
        print()
