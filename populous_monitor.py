from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from utilities.send_email import SendEmail
from utilities.customLogger import LogGen
import time
import os
from dotenv import load_dotenv


percent_diff_cutoff = 10
sleep_time_min = 6
old_price = None

load_dotenv()
logger = LogGen.loggen()

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
    'start': '1',
    'limit': '198'
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.getenv("COIN_MARKETCAP_API_KEY"),
}
print(os.getenv("COIN_MARKETCAP_API_KEY"))


while True:
    try:
        session = Session()
        session.headers.update(headers)
        response = session.get(url, params=parameters)
        populous_data = json.loads(response.text)
        data = populous_data['data']
        status = populous_data['status']

        for crypto in data:
            if crypto['symbol'] == 'PPT':
                global populous_crypto
                populous_crypto = crypto

        global current_price
        current_price = populous_crypto['quote']['USD']['price']

        if old_price is None:
            old_price = current_price

        percent_difference = ((current_price - old_price) / old_price) * 100
        logger.info(f'Current Price: {current_price}')
        logger.info(f'Price {sleep_time_min} mins ago: {old_price}')
        logger.info(f'Percent Diff: {percent_difference}')

        if abs(percent_difference) >= percent_diff_cutoff:
            logger.info(f'Populous exceeded {percent_diff_cutoff}% in the last {sleep_time_min} mins. Emailing '
                        f'selected recipients')

            send_email = SendEmail(subject='CHECK POPULOUS',
                                   body=f'Bro.... Populous just went up {percent_difference}% within the last '
                                        f'{sleep_time_min} minutes. You better check that shit out and sell')
            send_email.send_email()
    except Exception as e:
        logger.exception(e)

    time.sleep(sleep_time_min * 60)
    old_price = current_price

log_formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')

my_handler = RotatingFileHandler(os.path.join(ROOT_DIR, 'PPT.log'), mode='a', maxBytes=5 * 1024 * 1024,
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)

app_log.addHandler(my_handler)
