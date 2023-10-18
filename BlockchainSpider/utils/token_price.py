import json
import logging

import requests
from BlockchainSpider.utils.url import QueryURLBuilder


logger = logging.getLogger("token_price")


class TokenPrice:
    def __init__(self, contract_address):
        self.contract_address = contract_address
        self.cache_file_path = "../BlockchainSpider/utils/token_price.json"
        self.cache = self.load_cache()

    def load_cache(self):
        with open(self.cache_file_path, 'r') as f:
            return json.load(f)

    def save_cache(self):
        with open(self.cache_file_path, 'w') as f:
            json.dump(self.cache, f)

    def get_price_at_specific_block(self, block_number, timestamp):
        price = 0
        key = "{}_{}_{}".format(block_number, timestamp, self.contract_address)
        if key in self.cache.keys():
            price = self.cache[key]
        else:
            if self.contract_address == '':
                price = self.eth_price_at_specific_block(block_number, timestamp)
            else:
                response = self.price_usd_api(self.contract_address, block_number)
                data = json.loads(response.text)
                results: list = data.get('results', [])

                if len(results) != 0:
                    price = results[0]['price_token_usd_tick_1']
                else:
                    price = self.get_price_at_nearest_block(self.contract_address, timestamp, 100,
                                                            'price_usd')

            self.cache[key] = price
            self.save_cache()

        return price if price is not None else 0

    def eth_price_at_specific_block(self, block_number, timestamp):
        contract_address = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
        response = self.price_usd_api(contract_address, block_number)
        results: list = json.loads(response.text)['results']
        if len(results) == 0:
            usdt_to_eth = self.get_price_at_nearest_block(contract_address, timestamp, 100, 'price_eth')
            if usdt_to_eth == 0:
                a = 1
            eth_average_price = 1 / usdt_to_eth
            return eth_average_price
        eth_tick_price = results[0]['amount_usd'] / results[0]['amount_eth']
        return eth_tick_price

    def get_price_at_nearest_block(self, contract_address, timestamp, interval, price_type):
        """
        price_type: price_usd, price_eth
        """

        if interval > 10000000000:
            return 0

        base_url = "https://api.syve.ai/v1/price/historical/tick"
        params = {
            "token_address": contract_address,
            "size": 10000,
            "from_timestamp": timestamp - interval // 2,
            "until_timestamp": timestamp + interval // 2,
        }
        url = QueryURLBuilder(base_url).get(params)

        response = requests.request("GET", url)
        data = list()
        try:
            data = json.loads(response.text)['data']
        except KeyError:
            print(params)
            print(response.text)
            return 0

        valid_data = []
        for tx in data:
            if tx[price_type] is not None:
                valid_data.append(tx)

        if len(valid_data) == 0:
            return self.get_price_at_nearest_block(contract_address, timestamp, interval*2, price_type)

        for index, tx in enumerate(valid_data):
            tx_timestamp = tx['timestamp']
            if tx_timestamp < timestamp and index >= 1:
                token_price_before = tx[price_type]
                token_price_after = valid_data[index - 1][price_type]
                token_price = (token_price_after + token_price_before) / 2
                return token_price

        return valid_data[0][price_type]

    @staticmethod
    def price_usd_api(contract_address, block_number):
        url = "https://api.syve.ai/v1/prices_usd"
        payload = json.dumps({
            "filter": {
                "type": "and",
                "params": {
                    "filters": [
                        {
                            "type": "eq",
                            "params": {
                                "field": "block_number",
                                "value": block_number
                            }
                        },
                        {
                            "type": "eq",
                            "params": {
                                "field": "token_address",
                                "value": contract_address
                            }
                        }
                    ]
                }
            },
            "options": [
                {
                    "type": "sort",
                    "params": {
                        "field": "block_number",
                        "value": "desc"
                    }
                },
                {
                    "type": "size",
                    "params": {
                        "value": 5
                    }
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json'
        }
        return requests.request("POST", url, headers=headers, data=payload)


if __name__ == "__main__":
    print(TokenPrice("").get_price_at_specific_block(16772256, 1692343267))
    print(TokenPrice("0xdAC17F958D2ee523a2206206994597C13D831ec7").get_price_at_nearest_block(1692343267,1558371616 ,100, 'price_eth'))
