import json
import requests

class Mindicador:
		def __init__(self, indicador, year):
				self.indicador = indicador
				self.year = year
		def InfoApi(self):
				# En este caso hacemos la solicitud para el caso de consulta de un indicador en un año determinado
				url = f'https://mindicador.cl/api/{self.indicador}/{self.year}'
				response = requests.get(url)
				data = json.loads(response.text.encode("utf-8"))
				# Para que el json se vea ordenado, retornar pretty_json
				pretty_json = json.dumps(data, indent=2)
				return data


class PhpApi:
	def __init__(self,modelo:str,url:str,id_n:str='id'):
		self.model = modelo
		self.url = url
		self.id_n = id_n

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
			json={f'{self.id_n}':id}
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
			json={f'{self.id_n}':id}
		)
		data = json.loads(res.text.encode("utf-8"))
		pretty_json = json.dumps(data, indent=2)
		return data
