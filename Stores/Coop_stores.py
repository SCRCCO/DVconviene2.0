import json
import requests
from time import sleep

class CoopStoreLocator:
    def __init__(self):
        self.url_coop = "https://www.coop.it/api/esb/storelocator/"
        self.headers = {
            'Accept': 'application/json',
            'Host': 'www.coop.it',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }

    def get_geo_coop(self):
        url = self.url_coop + "getStoresLocation?_format=form"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            stores_dict = {}

            for store in data['payload']['stores']:
                store_id = store['id']
                store_info = {
                    'name': store['name'],
                    'city': store['city'],
                    'province': store['province'],
                    'geo': store['geo'],
                    'store': "coop"
                }
                stores_dict[store_id] = store_info

            return stores_dict
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

    def get_geo_store_coop(self, city):
        coop_dict = self.get_geo_coop()
        store = next((store_info for store_info in coop_dict.values() if store_info['city'] == city), None)

        if store:
            store_coords = store['geo']
            return store_coords
        else:
            print(f"Error extracting coordinates for {city}")

    def get_store_geo_coop(self, geo):
        url_post = self.url_coop + "searchStores?_format=form"
        payload = {
            'coords': geo,
            'storeName': None,
        }
        headers_post = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.coop.it",
            "Referer": "https://www.coop.it/punti-vendita",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        }

        response = requests.post(url_post, headers=headers_post, json=payload)

        if response.status_code == 200:
            data = response.json()
            stores_data = []

            for store in data.get('payload', {}).get('stores', []):
                store_info = {
                    "id": store.get("id"),
                    "coopId": store.get("coopId"),
                    "name": store.get("name"),
                    "cooperativa": store.get("cooperativa"),
                    "address": store.get("address"),
                    "city": store.get("city"),
                    "province": store.get("province"),
                    "phone": store.get("phone"),
                    "geo": store.get("geo"),
                }
                stores_data.append(store_info)

            with open('Outputs/coop_stores.json', 'a', encoding='utf-8') as json_file:
                json_file.seek(0, 2)

                if json_file.tell() > 0:
                    json_file.write(',')

                json.dump(stores_data, json_file, ensure_ascii=False, indent=2)
                json_file.write('\n')
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

    def get_list_of_city_coop(self):
        coop_dict = self.get_geo_coop()
        cities_list = []

        for store_info in coop_dict.values():
            city = store_info.get('city', 'City Not Available')

            if 'store_id' not in store_info:
                cities_list.append(city)

        unique_cities = list(set(cities_list))
        return unique_cities

    def get_all_stores_coop(self):
        coop_dict = self.get_geo_coop()
        cities = self.get_list_of_city_coop()
        total_cities = len(cities)
        completed_cities = 0

        for c in cities:
            self.get_store_geo_coop(self.get_geo_store_coop(c))
            completed_cities += 1

            completion_percentage = (completed_cities / total_cities) * 100
            print(f"{c} Extracted - Completion: {completion_percentage:.2f}%")
            sleep(2)

    def handle_json(self, json_file):
        with open(json_file, 'r') as file:
            data = file.read()

        modified_data = '[' + data + ']'

        with open(json_file, 'w') as file:
            file.write(modified_data)

    def GET_ALL_STORES_COOP(self):
        self.get_all_stores_coop()
        print('Processing the json...')
        self.handle_json("Outputs/coop_stores.json")


if __name__ == "__main__":
    coop_locator = CoopStoreLocator()
    coop_locator.GET_ALL_STORES_COOP()
