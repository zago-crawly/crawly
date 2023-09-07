import requests
import json

body = json.dumps({
                    'q': "test test",
                    'source': 'en',
                    'target': 'ru'})

response = requests.post(
                    # url=f"http://{os.environ.get('TRANSLATOR_SERVER')}:{os.environ.get('TRANSLATOR_PORT')}/translate",
                    url="http://87.249.44.229:5000/translate",
                    data=
                        json.dumps({
                        'q': "You try this in the figma application",
                        'source': 'en',
                        'target': 'ru'
                        }),
                        headers={ "Content-Type": "application/json" }
                )
print(response.text)