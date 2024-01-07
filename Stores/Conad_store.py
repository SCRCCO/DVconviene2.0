import json
import requests
import certifi
import ssl
from geopy.geocoders import Nominatim, options
import time
from tqdm import tqdm

class ConadStoreLocator:
    def __init__(self):
        self.custom_user_agent = "Stocazzo"
        options.default_user_agent = self.custom_user_agent

        # Set up SSL context
        ctx = ssl.create_default_context(cafile=certifi.where())
        options.default_ssl_context = ctx

    def save_to_file(self, data, filename):
        with open("Outputs/"+filename, 'a', encoding='utf-8') as file:
            file.seek(0, 2)  # Move to the end of the file

            if file.tell() > 0:
                file.write(',\n')  # Add a comma and newline if not the first entry
            else:
                file.write('[')  # Add an opening square bracket for the first entry

            file.write(json.dumps(data, ensure_ascii=False, indent=2))
            file.write('\n')  # Add a newline after each entry

    def close_json_file(self, filename):
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(']\n')  # Add a closing square bracket at the end

    def get_citta_conad(self):
        url_citta = "https://axqvoqvbfjpaamphztgd.functions.supabase.co/comuni"
        response = requests.get(url_citta)

        if response.status_code == 200:
            data = response.json()
            città_list = [entry["nome"] for entry in data]
            return città_list
        else:
            print("Errore nell'estrazione delle città")

    def get_lat_and_long(self, città):
        geolocator = Nominatim(scheme='http')
        city_name = f"{città}, Italy"
        location = geolocator.geocode(city_name)

        if location:
            return location.latitude, location.longitude
        else:
            print(f"Location not found for {città}")

    def make_post_request(self, lat, long):
        url = "https://www.conad.it/api/corporate/it-it.retrievePointOfService.json"
        payload = {
            "latitudine": lat,
            "longitudine": long,
            "raggioRicerca": "15",
            "insegneId": [],
            "apertura": [],
            "repartiId": [],
            "serviziId": []
        }

        try:
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code}, {response.text}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def extract_fields(self, data):
        extracted_data = {
            "id": data.get("id", ""),
            "indirizzo": data.get("indirizzo", ""),
            "ragioneSociale": data.get("ragioneSociale", ""),
            "descrizioneInsegna": data.get("descrizioneInsegna", ""),
            "telefono": data.get("telefono", ""),
            "cap": data.get("cap", ""),
            "anacanId": data.get("anacanId", ""),
            "latitudine": data.get("latitudine", ""),
            "longitudine": data.get("longitudine", ""),
            "codiceProvincia": data.get("codiceProvincia", ""),
            "nomeComune": data.get("nomeComune", "")
        }
        return extracted_data

    def GET_ALL_STORES_CONAD(self):
        città_list = self.get_citta_conad()
        total_cities = len(città_list)
        completed_cities = 0

        for c in tqdm(città_list, desc="Progress", unit="city"):
            print(f"Analizzo {c}")
            geo = self.get_lat_and_long(c)
            api_response = self.make_post_request(geo[0], geo[1])
        
            extracted_data_list = [self.extract_fields(entry) for entry in api_response.get("data", [])]

            for extracted_data in tqdm(extracted_data_list, desc="Processing", unit="entry", leave=False):
                self.save_to_file(extracted_data, 'conad_stores.json')
                time.sleep(1)

            completed_cities += 1
            completion_percentage = (completed_cities / total_cities) * 100
            print(f"{c} Extracted - Completion: {completion_percentage:.2f}%")
            time.sleep(2)

        self.close_json_file('conad_stores.json')


if __name__ == "__main__":
    extractor = ConadStoreLocator()
    extractor.GET_ALL_STORES_CONAD()
