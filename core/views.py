from twilio.twiml.messaging_response import MessagingResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import requests
import datetime
import emoji
import random
import json

@csrf_exempt
def index(request):
    if request.method == 'POST':
        # retrieve incoming message from POST request in lowercase
        incoming_msg = request.POST['Body'].lower()

        # create Twilio XML response
        resp = MessagingResponse()
        msg = resp.message()

        if incoming_msg == 'hello':
        	 response = emoji.emojize("""
*Hey! I am the MasirorBot* I give latest Corona virus stats:sunglasses:
Let's be friends :wink:
*You can give me the following commands:*
:black_small_square: *'kenya':* Get stats for Covid19 :wave:
:black_small_square: *'yes':* Get daily stats for Covid :wave:
:black_small_square: *'statistics <country>'*: Show the latest COVID19 statistics for each country. :earth_americas:
:black_small_square: *'statistics <prefix>'*: Show the latest COVID19 statistics for all countries starting with that prefix. :globe_with_meridians:

""", use_aliases=True)
        	 msg.body(response)
        	 responded = True       
        elif incoming_msg == 'kenya':
            # returns a quote
            r = requests.get('https://corona.lmao.ninja/v2/countries/kenya')
            if r.status_code == 200:
                data = r.json()
                kenya = f"""
                Total tests done stands at {data["tests"]},\n 
and the cases are {data["cases"]}.\n
We have {data["recovered"]} recoveries,\n
while {data["active"]} are active cases.\n
Now {data["critical"]} are critical cases.\n
Sadly {data["deaths"]} Kenyans have died.\n
Would you like me to tell you the stats for today alone?
                """
            else:
                kenya = 'I could not retrieve the info at this time, sorry.'
            msg.body(kenya)
            responded = True
        elif incoming_msg == 'yes':
            # returns a quote
            r = requests.get('https://corona.lmao.ninja/v2/countries/kenya')
            if r.status_code == 200:
                data = r.json()
                yes = f"""
Today`s cases are {data["todayCases"]}'.\n
We have {data["todayRecovered"]} recoveries today.\n
Unfortunately we have lost {data["todayDeaths"]} Kenyans today.\n
That is all I have for you.
Stay safe we shall overcome!
                """
            else:
                yes = 'I could not retrieve the info at this time, sorry.'
            msg.body(yes)
            responded = True
        elif incoming_msg.startswith('statistics'):
            # runs task to aggregate data from Apify Covid-19 public actors
            requests.post('https://api.apify.com/v2/actor-tasks/5MjRnMQJNMQ8TybLD/run-sync?token=qTt3H59g5qoWzesLWXeBKhsXu&ui=1')         
            # get the last run dataset items
            r = requests.get('https://api.apify.com/v2/actor-tasks/5MjRnMQJNMQ8TybLD/runs/last/dataset/items?token=qTt3H59g5qoWzesLWXeBKhsXu')         
            if r.status_code == 200:
                data = r.json()
                country = incoming_msg.replace('statistics', '')
                country = country.strip()
                country_data = list(filter(lambda x: x['country'].lower().startswith(country), data))
                if country_data:
                    result = ''
                    for i in range(len(country_data)):
                        data_dict = country_data[i]
                        last_updated = datetime.datetime.strptime(data_dict.get('lastUpdatedApify', None), "%Y-%m-%dT%H:%M:%S.%fZ")
                        result += """
*Statistics for country {}*
Infected: {}
Tested: {}
Recovered: {}
Deceased: {}
Last updated: {:02}/{:02}/{:02} {:02}:{:02}:{:03} UTC
""".format(
    data_dict['country'], 
    data_dict.get('infected', 'NA'), 
    data_dict.get('tested', 'NA'), 
    data_dict.get('recovered', 'NA'), 
    data_dict.get('deceased', 'NA'),
    last_updated.day,
    last_updated.month,
    last_updated.year,
    last_updated.hour,
    last_updated.minute,
    last_updated.second
    )
                else:
                    result = "Country not found. Sorry!"
            
            else:
                result = "I cannot retrieve statistics at this time. Sorry!"

            msg.body(result)
            responded = True
        return HttpResponse(str(resp))



        
