import json
import logging
import os
import time

import requests

URL = "https://api.exchangerate-api.com/v4/latest/"
MAX_RETRIES = 3
RETRY_DELAY = 2
TIMEOUT = 10
CACHE_EXPIRY = 3600

class CurrencyConverter():
    def __init__(self, source_currency, target_currency):
        self.source_currency = source_currency
        self.target_currency = target_currency
        self.logger = self._setup_logger()
        self.cache_file = f"exchange_rates_{self.source_currency}.json"
        self.cache_expiry = CACHE_EXPIRY
        self.max_retries = MAX_RETRIES
        self.retry_delay = RETRY_DELAY   
        self.url = f"{URL}{self.source_currency}"
        self.rates = self.get_rates()

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger
    
    def _load_from_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    if time.time() - data['timestamp'] < self.cache_expiry:
                        return data['rates']
            except (json.JSONDecodeError, KeyError):
                print("Invalid cache file. Fetching from API.")
                return None
        return None
    
    def _save_to_cache(self, rates):
        try:
            data = {'timestamp': time.time(), 'rates': rates}
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
        except IOError as e:
            print(f"Error saving to cache: {e}")  

    def get_rates(self):
        rates = self._load_from_cache()
        if rates:
            return rates

        for attempt in range(self.max_retries):
            try:
                response = requests.get(self.url, timeout=TIMEOUT)
                response.raise_for_status()
                data = response.json()
                rates = data['rates']
                self._save_to_cache(rates)
                return rates

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error("Max retries reached.  Unable to fetch rates.")
                    return None

            except (json.JSONDecodeError, KeyError) as e:
                self.logger.error(f"Error processing JSON response: {e}")
                return None
   
    def convert(self, amount):
        return amount * self.rates[self.target_currency]