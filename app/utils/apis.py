from datetime import datetime, timedelta
import json
import requests

class Mindicador:
    def __init__(self, indicador):
        self.indicador = indicador

    def get_indicator_value(self, date=None):
        if date is None:
            # Obtener la fecha del día anterior
            date = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y')
        url = f'https://mindicador.cl/api/{self.indicador}/{date}'
        response = requests.get(url)
        data = json.loads(response.text.encode("utf-8"))
        return data

    def get_dollar_value_today(self):
        data = self.get_indicator_value()
        dollar_value = None 
        if "serie" in data and len(data["serie"]) > 0:
            dollar_value = data["serie"][0]["valor"]
        return dollar_value

class PhpApi:
	url = 'http://localhost/php_api/api/service.php?'
	#							^^^^^^^^^
	#change host here
	def __init__(self,modelo:str):
		self.model = modelo
	def getAll(self):
		res = requests.get(
			url=self.url,
			params={'model':self.model}
		)
		data = json.loads(res.text.encode("utf-8"))
		pretty_json = json.dumps(data, indent=2)
		return data
	def getOne(self,id:int):
		res = requests.get(
			url=self.url,
			params={'model':self.model},
			json={'id':id}
		)
		data = json.loads(res.text.encode("utf-8"))
		pretty_json = json.dumps(data, indent=2)
		return data
	def post(self,data):
		res = requests.post(
			url=self.url,
			params={'model':self.model},
			json=data
		)
		data = json.loads(res.text.encode("utf-8"))
		pretty_json = json.dumps(data, indent=2)
		return data
	def put(self,data):
		res = requests.put(
			url=self.url,
			params={'model':self.model},
			json=data
		)
		data = json.loads(res.text.encode("utf-8"))
		pretty_json = json.dumps(data, indent=2)
		return data
	def Del(self,id:int):
		res = requests.delete(
			url=self.url,
			params={'model':self.model},
			json={'id':id}
		)
		data = json.loads(res.text.encode("utf-8"))
		pretty_json = json.dumps(data, indent=2)
		return data
