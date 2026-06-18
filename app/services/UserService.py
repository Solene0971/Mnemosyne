
from app.models.UserDAO import UserSqliteDAO as UserDAO

class UserService():
	"""
	Classe dédiée à la logique des utilisateurs
	"""
	def __init__(self):
		self.udao = UserDAO()

	def login(self,username, password):
		return self.udao.verifyMDP(username,password)
	
	def changepwd(self,username,password):
		return self.udao.change_mdp(username,password)
	
	def addUser(self,username, password):
		return self.udao.addUser(username,password)
	
	def delUser(self,username):
		return self.udao.suppUser(username)
	
	def getAllUser(self):
		return self.udao.getAllUser()

	def verifMDP(self,username, password):
		return self.udao.verifyMDP(username,password)