from iqoptionapi.stable_api import IQ_Option
import time, json, threading, sys, requests, hashlib, sqlite3, requests, random
from datetime import datetime, date
from dateutil import tz
from random import randrange, choice
from PyQt5 import uic, QtWidgets, QtGui, QtCore, Qt
from PyQt5.QtGui import QIcon
from Images import File_Resources_rc, Paridades_rc, Icones_rc



API = ''
connection = sqlite3.connect('userdata.db')
c = connection.cursor()

app = QtWidgets.QApplication([])
catal = uic.loadUi('GUI-Catalogador.ui')



#==============================================================================================================================================================

# MODIFICAR A VARIAVEL VERSAO AQUI E NO BANCO DE DADOS CASO HOUVER ALGUMA
# ATUALIZAÇÃO, POIS VERSOES MAIS ANTIGAS NÃO PODERÃO SER MAIS UTILIZADAS


versao = '1.1'
travar = False


payload_version = {'versao': versao}
r_version = requests.post('https://programadoreficaz.000webhostapp.com/catalogador/checkversion.php', data = payload_version)
#print('versao: ' , r_version.text)

if(r_version.text == versao):
	catal.Lbl_Versao.setText(r_version.text)
else:
	travar = True
	catal.Frame_Versao.setMinimumSize(0, 100)
	catal.Lbl_Versao.setText('Versao antiga, por favor baixe a nova versão')
	


#==============================================================================================================================================================
# CRIAÇÃO DE UMA SESSÃO


sessao = ''
count = 0

while (count < 6):
	numero = randrange(0, 2)
	
	if( numero == 0 ):
		sessao = sessao + str(randrange(0, 10))
	else:
		sessao = sessao + random.choice('abcdefghijklmnopqrstuvxywzABCDEFGHIJKLMNOPQRSTUVXYWZ')
	
	count += 1

print(sessao)


#==============================================================================================================================================================


catal.QFrame_Mensagem.setVisible(False)
catal.QFrame_Mensagem_Error.setVisible(False)

# CRIA TABELA SE NAO EXISTIR
c.execute( 'CREATE TABLE IF NOT EXISTS dados (email text, senha text, senha_iq text, lembrar bool )' )

# CHECA SE 'Check Button LEMBRAR' NAO ESTA ATIVO
sql = 'SELECT * FROM dados WHERE email IS NOT NULL and senha IS NOT NULL and lembrar = 1'
for row in c.execute(sql):
	if (row[3] == 1):
		catal.LineEdit_Email.setText(row[0])
		catal.LineEdit_Senha.setText(row[1])
		catal.LineEdit_Senha_IQ.setText(row[2])
		catal.CBox_Remember.setChecked(True)


count = 0



show_senha = False
show_senha_IQ = False
show_senha_registrar = False



# MOSTRAR PARTE DO ALPHAKEY
# DELETAR PARA MOSTRAR QUANDO SAIR DO PERIODO DE TESTE
catal.Frame_Alphakey.setVisible(True)



# ALGUMAS THREADS ==================================================================================================================================================

def CHECK_SESSION(_email, _sessao):
	
	global sair
	global catal
	global app
	
	while True:
		payload_session = {'email': _email, 'sessao': _sessao}
		r_session = requests.post('https://programadoreficaz.000webhostapp.com/catalogador/checksession.php', data = payload_session)
		print(r_session.text)
		
		if(r_session.text != 'ok'):
			sair = True
			catal.Main.setMaximumSize(0,0)
			catal.Main.setMinimumSize(0,0)
			app.exit(0)
			break
		
		time.sleep(10)



def CHECK_PARIDADE_ABERTA():
	global catal
	
	par = API.get_all_open_time()
	lista_pares = []
	
	for paridade in par['turbo']:
		if par['turbo'][paridade]['open'] == True:
			if(len(lista_pares) == 0):
				lista_pares.append(paridade)
			else:
				j = len(lista_pares)
				for i in range(0, len(lista_pares)):
					
					while (j > 0):
						if(paridade == lista_pares[j-1] ):
							break
							
						j -= 1
						if(j==0):
							lista_pares.append(paridade)


	for paridade in par['digital']:
		if par['digital'][paridade]['open'] == True:
			if(len(lista_pares) == 0):
				lista_pares.append(paridade)
			else:
				j = len(lista_pares)
				for i in range(0, len(lista_pares)):
				
					while (j > 0):
						if(paridade == lista_pares[j-1] ):
							break
					
						j -= 1
						if(j==0):
							lista_pares.append(paridade)

	print(lista_pares)



# GUI ================================================================================================================================================================
def SHOW_MESSAGE(_error):
	catal.QFrame_Mensagem.setVisible(True)
	
	if(_error == 'False'):
		catal.Lbl_Mensagem.setText('Email ou senha inválido')
	elif(_error == 'versao_antiga'):
		catal.Lbl_Mensagem.setText('Baixe a nova versão')
	
	
	time.sleep(3)
	catal.QFrame_Mensagem.setVisible(False)
	catal.Lbl_Mensagem.setText('')
	
	
def LOGIN():
	global sessao
	global catal
	global API
	
	email = catal.LineEdit_Email.text()
	
	senha = catal.LineEdit_Senha.text()
	#senha_encrypt = hashlib.md5( senha.encode() ) 
	senha_IQ = catal.LineEdit_Senha_IQ.text()
	
	#payload_login = {'email': email, 'senha': senha}
	payload_login = {'email': email, 'senha': senha, 'sessao': sessao}
	r = requests.post('https://programadoreficaz.000webhostapp.com/catalogador/login.php', data = payload_login)
	#print(r.text)
	
	
	#if(r.text == 'Logando'):
	if(r.text == 'Logando' and (travar == False) ):
		
		if (catal.CBox_Remember.isChecked()):
			c.execute('DELETE FROM dados')
			connection.commit()
			c.execute('INSERT INTO dados VALUES (?, ?, ?, True)', (email, senha, senha_IQ))
			connection.commit()
		else:
			c.execute('DELETE FROM dados')
			connection.commit()
			c.execute('INSERT INTO dados VALUES (NULL, NULL, NULL, False)' )
			connection.commit()
	
		catal.LineEdit_Email.setText('')
		catal.LineEdit_Senha.setText('')

		_API = IQ_Option(email, senha_IQ)
		_API.connect()
		
		
		while True:
			
			if (_API.check_connect() == False):
				_API.connect()

			else:
				# Conectado
				
				#print('Conectado', conectado)
				break
			
			time.sleep(2)
		
	
		
		thread = threading.Thread(target=CHECK_SESSION, args = (email, sessao, ))
		thread.start()
		
		API = _API
		CATAL_PAGE(email)
	

	#print(r.text)
'''
	else:
		if(travar == True):
			thread = threading.Thread(target=SHOW_MESSAGE, args = ('versao_antiga', ))
			thread.start()
			
			catal.LineEdit_Senha.setText('')
			return
		else:
			thread = threading.Thread(target=SHOW_MESSAGE, args = ('False', ))
			thread.start()
			
			catal.LineEdit_Senha.setText('')
			return
'''	


def SHOW_MESSAGE_REGISTER(_error):	
	global catal
	
	catal.QFrame_Mensagem_Error.setVisible(True)
	if(_error == 'email'):
		catal.Lbl_Mensagem_Error.setText('E-Mail não informado')

	if(_error == 'senha nao informada'):
		catal.Lbl_Mensagem_Error.setText('Senha não informada')
	
	if(_error == 'senhas nao coincidem'):
		catal.Lbl_Mensagem_Error.setText('Senhas não coincidem')
	
	if(_error == 'key_nao_informada'):
		catal.Lbl_Mensagem_Error.setText('Alphakey não informada')	

	if(_error == 'key_invalida'):
		catal.Lbl_Mensagem_Error.setText('Alphakey inválida')

	if(_error == 'versao_antiga'):
		catal.Lbl_Mensagem_Error.setText('Baixe a nova versao')
    
	if (_error == 'email_ja_existente'):
	    catal.Lbl_Mensagem_Error.setText('E-mail já cadastrado')
    
	if(_error == 'afiliado_nao_informado'):
		catal.Lbl_Mensagem_Error.setText('Afiliado não Informado')
    
	time.sleep(3)
	catal.QFrame_Mensagem_Error.setVisible(False)
	catal.Lbl_Mensagem_Error.setText('')
	

def REGISTRAR():
	
	
	if (travar == True):
		thread = threading.Thread(target=SHOW_MESSAGE_REGISTER, args = ('versao_antiga', ))
		thread.start()
		return
	
	if (travar == False):
		
		global catal
		senha_not_null = False
		senhas_conferem = False
		senha_valida = False
		email_not_null = False
		senha = ''
		checkkey = ''
		afiliado = ''
		afiliado_ok = False
		
		payload = { 'email': catal.LineEdit_Email_Register.text() }
		checkuser = requests.post('https://programadoreficaz.000webhostapp.com/catalogador/checkuser.php', data = payload)
		#print(checkuser.text)
		
		
		if(catal.LineEdit_Email_Register.text() == ''):
			thread = threading.Thread(target=SHOW_MESSAGE_REGISTER, args = ('email', ))
			thread.start()
			return
		else:
			email_not_null = True
	
		if( (catal.LineEdit_Confirmar_Senha.text() == '') or (catal.LineEdit_Senha_Register.text() == '') ):
			thread = threading.Thread(target=SHOW_MESSAGE_REGISTER, args = ('senha nao informada', ))
			thread.start()
			return
		elif( (catal.LineEdit_Confirmar_Senha.text() != '') or (catal.LineEdit_Senha_Register.text() != '') ):
			senha_not_null = True
		
		if( catal.LineEdit_Senha_Register.text() != catal.LineEdit_Confirmar_Senha.text() ):
			thread = threading.Thread(target=SHOW_MESSAGE_REGISTER, args = ('senhas nao coincidem', ))
			thread.start()
			senha = ''
			return
		elif( catal.LineEdit_Senha_Register.text() == catal.LineEdit_Confirmar_Senha.text() ):
			senhas_conferem = True
		
		
		if( (checkuser.text != "E-mail já existe") and (catal.LineEdit_Email_Register.text() != '') and (senha_not_null) and (senhas_conferem) ):
			senha_valida = True
			senha = catal.LineEdit_Senha_Register.text()
		elif(catal.LineEdit_Email_Register.text() == ''):
			thread = threading.Thread(target=SHOW_MESSAGE_REGISTER, args = ('email_ja_existente', ))
			thread.start()
			return

		if ( (catal.LineEdit_Afiliado.text() == 'galaxy') or (catal.LineEdit_Afiliado.text() == 'eficaz') ):
			afiliado = catal.LineEdit_Afiliado.text()
			afiliado_ok = True

		elif ( (catal.LineEdit_Afiliado.text() != 'galaxy') or (catal.LineEdit_Afiliado.text() != 'eficaz') ):
			thread = threading.Thread(target=SHOW_MESSAGE_REGISTER, args = ('afiliado_nao_informado', ))
			thread.start()
			return
		
		
		if (catal.LineEdit_Alphakey.text() == '' ):
			thread = threading.Thread(target=SHOW_MESSAGE_REGISTER, args = ('key_nao_informada', ))
			thread.start()
			return
		elif ( (catal.LineEdit_Alphakey.text() != '') and (email_not_null == True) ):
			payload = {'key': catal.LineEdit_Alphakey.text(), 'email': catal.LineEdit_Email_Register.text() }
			checkkey_r = requests.post('https://programadoreficaz.000webhostapp.com/catalogador/checkkey.php', data = payload)
			print(checkkey_r.text)
			checkkey = checkkey_r.text
        
        
		if (checkkey != 'Alphakey Activated!'):
			thread = threading.Thread(target=SHOW_MESSAGE_REGISTER, args = ('key_invalida', ))
			thread.start()
			return
        
		
		
		if( (senha_valida ) and (checkuser.text != "E-mail já existe") and (checkkey == 'Alphakey Activated!') and afiliado_ok):

			#senha_encrypt = hashlib.md5( senha.encode() ) 
			email = catal.LineEdit_Email_Register.text()

			payload = {'email': email, 'senha': senha, 'afiliado': afiliado} 
			signup_r = requests.post('https://programadoreficaz.000webhostapp.com/catalogador/signup.php', data = payload)
			#print(signup_r.text)

			LOGIN_PAGE()
	
	

def REGISTER_PAGE():
	
	global catal
	catal.Login_Page.setMaximumSize(QtCore.QSize(0, 0))
	catal.Register_Page.setMaximumSize(QtCore.QSize(16777215, 16777215))
	
	catal.LineEdit_Email.setText('')
	catal.LineEdit_Senha.setText('')
	catal.LineEdit_Senha_IQ.setText('')
	
	
	
def LOGIN_PAGE():
	
	global catal
	catal.Register_Page.setMaximumSize(QtCore.QSize(0, 0))
	catal.Login_Page.setMaximumSize(QtCore.QSize(16777215, 16777215))
	
	catal.LineEdit_Alphakey.setText('')
	catal.LineEdit_Confirmar_Senha.setText('')
	catal.LineEdit_Email_Register.setText('')
	catal.LineEdit_Senha_Register.setText('')
	catal.LineEdit_Afiliado.setText('')

	
	

def CATAL_PAGE(_email):
	
	global catal
	catal.Login_Page.setMaximumSize(QtCore.QSize(0, 0))
	catal.Register_Page.setMaximumSize(QtCore.QSize(0, 0))
	catal.Head.setMaximumSize(QtCore.QSize(16777215, 90))
	catal.Main.setMaximumSize(QtCore.QSize(16777215, 16777215))
	catal.Lbl_Usuario.setText(_email)



def SHOW_SENHA():
	
	global show_senha
	
	lineEdit = catal.LineEdit_Senha
	
	if(show_senha):
		catal.Btn_Visualizar_Senha.setIcon(QIcon('Images/Visibilidade Off.png'))
		catal.LineEdit_Senha.setEchoMode(lineEdit.EchoMode.Password)
		show_senha = False
	else:
		catal.Btn_Visualizar_Senha.setIcon(QIcon('Images/Visibilidade On.png'))
		catal.LineEdit_Senha.setEchoMode(lineEdit.EchoMode.Normal)
		show_senha = True
	
def SHOW_SENHA_IQ():

	global show_senha_IQ
	
	lineEdit = catal.LineEdit_Senha_IQ
	
	if(show_senha_IQ):
		catal.Btn_Visualizar_Senha_IQ.setIcon(QIcon('Images/Visibilidade Off.png'))
		catal.LineEdit_Senha_IQ.setEchoMode(lineEdit.EchoMode.Password)
		show_senha_IQ = False
	else:
		catal.Btn_Visualizar_Senha_IQ.setIcon(QIcon('Images/Visibilidade On.png'))
		catal.LineEdit_Senha_IQ.setEchoMode(lineEdit.EchoMode.Normal)
		show_senha_IQ = True


def SHOW_SENHA_REGISTRAR():
	
	global show_senha_registrar
	
	lineEdit_s = catal.LineEdit_Senha_Register
	lineEdit_cs = catal.LineEdit_Confirmar_Senha
	
	if(show_senha_registrar):
		catal.Btn_Visualizar_Senha_Registrar.setIcon(QIcon('Images/Visibilidade Off.png'))
		catal.LineEdit_Senha_Register.setEchoMode(lineEdit_s.EchoMode.Password)
		catal.LineEdit_Confirmar_Senha.setEchoMode(lineEdit_cs.EchoMode.Password)
		show_senha_registrar = False
	else:
		catal.Btn_Visualizar_Senha_Registrar.setIcon(QIcon('Images/Visibilidade On.png'))
		catal.LineEdit_Senha_Register.setEchoMode(lineEdit_s.EchoMode.Normal)
		catal.LineEdit_Confirmar_Senha.setEchoMode(lineEdit_cs.EchoMode.Normal)
		show_senha_registrar = True


	

lista_Pares = ["AUDCAD", "AUDJPY", "AUDUSD", "CADCHF", "CADJPY", "CHFJPY", "EURAUD", "EURCAD", "EURGBP", "EURJPY", "EURNZD", "EURUSD", "GBPAUD", "GBPCAD", "GBPCHF", "GBPJPY", "GBPNZD", "GBPUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY", "USDNOK", "USDRUB"]
lista_Pares_OTC = ["AUDCAD-OTC","EURGBP-OTC", "EURJPY-OTC", "EURUSD-OTC", "GBPJPY-OTC", "GBPUSD-OTC", "NZDUSD-OTC", "USDCHF-OTC", "USDJPY-OTC"]

lista_criada = False
lista_catalogacao = []
estatisticas_pares = []

#=================================================================================================================================================================




# CONVERTE O FORMATO DO TEMPO PARA TEMPO NORMAL        #timestamp_converter(API.get_server_timestamp())
def timestamp_converter(x): # Função para converter timestamp
	hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
	hora = hora.replace(tzinfo=tz.gettz('GMT'))
	
	return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6]
	

class VARIAVEIS:
	
	gale = 0
	aux_vela_indicada = ''
	
	#horas = 0
	#min = 0
	vela_indicada = ''
	calls = 0
	puts = 0
	dojis = 0
	cancel_by_doji = 0
	aux_cancel_by_doji = 0
	count_velas = 0
	
	wins = 0
	loss = 0
	
	wins_1 = 0
	loss_1 = 0
	
	wins_2 = 0
	loss_2 = 0
	
	ciclos = 0 # QUANTAS VEZES A ESTRATEGIA FOI CHECADA / REPETIDA 
	
	resultado_operacao = []



def ESTATISTICA(_par, _ciclos, _dojis, _cancel_by_doji, _wins, _wins_1, _wins_2, _loss, _loss_1, _loss_2, _estrategia):

	global estatisticas_pares
	
	_entradas = _wins + _loss
	_entradas_1 = _wins_1 + _loss_1
	_entradas_2 = _wins_2 + _loss_2
	
	_acertividade = round( (_wins/_entradas)* 100 , 2)  
	_acertividade_1 = round( (_wins_1/_entradas_1 )* 100 , 2)  
	_acertividade_2 = round( (_wins_2/_entradas_2)* 100 , 2) 
	
	_media = round( ( (_acertividade + _acertividade_1 + _acertividade_2) / 3 ), 2)
	
	lista = [ _par, _media, _ciclos, _dojis, _cancel_by_doji, _wins, _wins_1, _wins_2, _loss, _loss_1, _loss_2, _acertividade, _acertividade_1, _acertividade_2, _estrategia]
	estatisticas_pares.append(lista)
	
	if ( len( estatisticas_pares ) > 0 ):
		
		for i in range( 1, len( estatisticas_pares ) ):
			aux = estatisticas_pares[i]
			j = i
			
			while ( (j > 0) and (aux[1] > estatisticas_pares[j - 1][1]) ):
				estatisticas_pares[j] = estatisticas_pares[j - 1]
				j -= 1
		
			estatisticas_pares[j] = aux



def CATAL_POR_ESTRATEGIA():

	global catal
	global estatisticas_pares
	
	# PRIMEIRO
	if ( len( estatisticas_pares ) > 0 ):
		catal.Frame_Estrategia_1_1.setHidden(False) 
		
		catal.Lbl_Par_1.setText( estatisticas_pares[0][0] )
		catal.Lbl_Estrategia_1.setText( str(estatisticas_pares[0][14]) )
		catal.Lbl_Porcentagem_1.setText( 'Média: ' + str(estatisticas_pares[0][1]) + '%')
		catal.Lbl_Ciclos_1.setText( 'Ciclos: ' + str(estatisticas_pares[0][2]) + ' | Canceladas: ' + str(estatisticas_pares[0][4]))
		
		catal.Lbl_Porc_Ent1_1.setText ( str(estatisticas_pares[0][11]) + '%' )
		catal.Lbl_Wins_Ent1_2.setText ( 'Wins: '+str(estatisticas_pares[0][5]) )
		catal.Lbl_Hits_Ent1_1.setText ( 'Hits: '+str(estatisticas_pares[0][8]) )
		
		catal.Lbl_Porc_Gale1_1.setText ( str(estatisticas_pares[0][12]) + '%' )
		catal.Lbl_Wins_Gale1_1.setText ( 'Wins: '+str(estatisticas_pares[0][6]) )
		catal.Lbl_Hits_Gale1_1.setText ( 'Hits: '+str(estatisticas_pares[0][9]) )
		
		catal.Lbl_Porc_Gale2_1.setText ( str(estatisticas_pares[0][13]) + '%' )
		catal.Lbl_Wins_Gale2_1.setText ( 'Wins: '+str(estatisticas_pares[0][7]) )
		catal.Lbl_Hits_Gale2_1.setText ( 'Hits: '+str(estatisticas_pares[0][10]) )
	else:
		catal.Frame_Estrategia_1_1.setHidden(True) 

	# SEGUNDO
	if ( len( estatisticas_pares ) > 1 ):
		catal.Frame_Estrategia_1_2.setHidden(False) 
		
		catal.Lbl_Par_2.setText( estatisticas_pares[1][0] )
		catal.Lbl_Estrategia_2.setText( str(estatisticas_pares[1][14]) )
		catal.Lbl_Porcentagem_2.setText( 'Média: ' + str(estatisticas_pares[1][1]) + '%')
		catal.Lbl_Ciclos_2.setText( 'Ciclos: ' + str(estatisticas_pares[1][2]) + ' | Canceladas: ' + str(estatisticas_pares[1][4]))
		
		catal.Lbl_Porc_Ent1_2.setText ( str(estatisticas_pares[1][11]) + '%' )
		catal.Lbl_Wins_Ent1_3.setText ( 'Wins: '+str(estatisticas_pares[1][5]) )
		catal.Lbl_Hits_Ent1_2.setText ( 'Hits: '+str(estatisticas_pares[1][8]) )
		
		catal.Lbl_Porc_Gale1_2.setText ( str(estatisticas_pares[1][12]) + '%' )
		catal.Lbl_Wins_Gale1_2.setText ( 'Wins: '+str(estatisticas_pares[1][6]) )
		catal.Lbl_Hits_Gale1_2.setText ( 'Hits: '+str(estatisticas_pares[1][9]) )
		
		catal.Lbl_Porc_Gale2_2.setText ( str(estatisticas_pares[1][13]) + '%' )
		catal.Lbl_Wins_Gale2_2.setText ( 'Wins: '+str(estatisticas_pares[1][7]) )
		catal.Lbl_Hits_Gale2_2.setText ( 'Hits: '+str(estatisticas_pares[1][10]) )
	else:
		catal.Frame_Estrategia_1_2.setHidden(True) 
	
	# TERCEIRO
	if ( len( estatisticas_pares ) > 2 ):
		catal.Frame_Estrategia_1_23.setHidden(False)
		
		catal.Lbl_Par_23.setText( estatisticas_pares[2][0] )
		catal.Lbl_Estrategia_23.setText(  str(estatisticas_pares[2][14]) )
		catal.Lbl_Porcentagem_23.setText( 'Média: ' + str(estatisticas_pares[2][1]) + '%')
		catal.Lbl_Ciclos_23.setText( 'Ciclos: ' + str(estatisticas_pares[2][2]) + ' | Canceladas: ' + str(estatisticas_pares[2][4]))
		
		catal.Lbl_Porc_Ent1_23.setText ( str(estatisticas_pares[2][11]) + '%' )
		catal.Lbl_Wins_Ent1_24.setText ( 'Wins: '+str(estatisticas_pares[2][5]) )
		catal.Lbl_Hits_Ent1_23.setText ( 'Hits: '+str(estatisticas_pares[2][8]) )
		
		catal.Lbl_Porc_Gale1_23.setText ( str(estatisticas_pares[2][12]) + '%' )
		catal.Lbl_Wins_Gale1_23.setText ( 'Wins: '+str(estatisticas_pares[2][6]) )
		catal.Lbl_Hits_Gale1_23.setText ( 'Hits: '+str(estatisticas_pares[2][9]) )
		
		catal.Lbl_Porc_Gale2_23.setText ( str(estatisticas_pares[2][13]) + '%' )
		catal.Lbl_Wins_Gale2_23.setText ( 'Wins: '+str(estatisticas_pares[2][7]) )
		catal.Lbl_Hits_Gale2_23.setText ( 'Hits: '+str(estatisticas_pares[2][10]) )
	else:
		catal.Frame_Estrategia_1_23.setHidden(True)
	
	# QUARTO
	if ( len( estatisticas_pares ) > 3 ):
		catal.Frame_Estrategia_1_24.setHidden(False) 
		
		catal.Lbl_Par_24.setText( estatisticas_pares[3][0] )
		catal.Lbl_Estrategia_24.setText(  str(estatisticas_pares[3][14]) )
		catal.Lbl_Porcentagem_24.setText( 'Média: ' + str(estatisticas_pares[3][1]) + '%')
		catal.Lbl_Ciclos_24.setText( 'Ciclos: ' + str(estatisticas_pares[3][2]) + ' | Canceladas: ' + str(estatisticas_pares[3][4]))
		
		catal.Lbl_Porc_Ent1_24.setText ( str(estatisticas_pares[3][11]) + '%' )
		catal.Lbl_Wins_Ent1_25.setText ( 'Wins: '+str(estatisticas_pares[3][5]) )
		catal.Lbl_Hits_Ent1_24.setText ( 'Hits: '+str(estatisticas_pares[3][8]) )
		
		catal.Lbl_Porc_Gale1_24.setText ( str(estatisticas_pares[3][12]) + '%' )
		catal.Lbl_Wins_Gale1_24.setText ( 'Wins: '+str(estatisticas_pares[3][6]) )
		catal.Lbl_Hits_Gale1_24.setText ( 'Hits: '+str(estatisticas_pares[3][9]) )
		
		catal.Lbl_Porc_Gale2_24.setText ( str(estatisticas_pares[3][13]) + '%' )
		catal.Lbl_Wins_Gale2_24.setText ( 'Wins: '+str(estatisticas_pares[3][7]) )
		catal.Lbl_Hits_Gale2_24.setText ( 'Hits: '+str(estatisticas_pares[3][10]) )
	else:
		catal.Frame_Estrategia_1_24.setHidden(True) 
	
	# QUINTO
	if ( len( estatisticas_pares ) > 4 ):
		catal.Frame_Estrategia_1_25.setHidden(False)
		
		catal.Lbl_Par_25.setText( estatisticas_pares[4][0] )
		catal.Lbl_Estrategia_25.setText( str(estatisticas_pares[4][14]) )
		catal.Lbl_Porcentagem_25.setText( 'Média: ' + str(estatisticas_pares[4][1]) + '%')
		catal.Lbl_Ciclos_25.setText( 'Ciclos: ' + str(estatisticas_pares[4][2]) + ' | Canceladas: ' + str(estatisticas_pares[4][4]))
		
		catal.Lbl_Porc_Ent1_25.setText ( str(estatisticas_pares[4][11]) + '%' )
		catal.Lbl_Wins_Ent1_26.setText ( 'Wins: '+str(estatisticas_pares[4][5]) )
		catal.Lbl_Hits_Ent1_25.setText ( 'Hits: '+str(estatisticas_pares[4][8]) )
		
		catal.Lbl_Porc_Gale1_25.setText ( str(estatisticas_pares[4][12]) + '%' )
		catal.Lbl_Wins_Gale1_25.setText ( 'Wins: '+str(estatisticas_pares[4][6]) )
		catal.Lbl_Hits_Gale1_25.setText ( 'Hits: '+str(estatisticas_pares[4][9]) )
		
		catal.Lbl_Porc_Gale2_25.setText ( str(estatisticas_pares[4][13]) + '%' )
		catal.Lbl_Wins_Gale2_25.setText ( 'Wins: '+str(estatisticas_pares[4][7]) )
		catal.Lbl_Hits_Gale2_25.setText ( 'Hits: '+str(estatisticas_pares[4][10]) )
	else:
		catal.Frame_Estrategia_1_25.setHidden(True)
	
	# SEXTO
	if ( len( estatisticas_pares ) > 5 ):
		catal.Frame_Estrategia_1_26.setHidden(False)
		
		catal.Lbl_Par_26.setText( estatisticas_pares[5][0] )
		catal.Lbl_Estrategia_26.setText( str(estatisticas_pares[5][14]) )
		catal.Lbl_Porcentagem_26.setText( 'Média: ' + str(estatisticas_pares[5][1]) + '%')
		catal.Lbl_Ciclos_26.setText( 'Ciclos: ' + str(estatisticas_pares[5][2]) + ' | Canceladas: ' + str(estatisticas_pares[5][4]))
		
		catal.Lbl_Porc_Ent1_26.setText ( str(estatisticas_pares[5][11]) + '%' )
		catal.Lbl_Wins_Ent1_27.setText ( 'Wins: '+str(estatisticas_pares[5][5]) )
		catal.Lbl_Hits_Ent1_26.setText ( 'Hits: '+str(estatisticas_pares[5][8]) )
		
		catal.Lbl_Porc_Gale1_26.setText ( str(estatisticas_pares[5][12]) + '%' )
		catal.Lbl_Wins_Gale1_26.setText ( 'Wins: '+str(estatisticas_pares[5][6]) )
		catal.Lbl_Hits_Gale1_26.setText ( 'Hits: '+str(estatisticas_pares[5][9]) )
		
		catal.Lbl_Porc_Gale2_26.setText ( str(estatisticas_pares[5][13]) + '%' )
		catal.Lbl_Wins_Gale2_26.setText ( 'Wins: '+str(estatisticas_pares[5][7]) )
		catal.Lbl_Hits_Gale2_26.setText ( 'Hits: '+str(estatisticas_pares[5][10]) )
	else:
		catal.Frame_Estrategia_1_26.setHidden(True)
	
	# SETIMO
	if ( len( estatisticas_pares ) > 6 ):
		catal.Frame_Estrategia_1_27.setHidden(False)
		
		catal.Lbl_Par_27.setText( estatisticas_pares[6][0] )
		catal.Lbl_Estrategia_27.setText( str(estatisticas_pares[6][14]) )
		catal.Lbl_Porcentagem_27.setText( 'Média: ' + str(estatisticas_pares[6][1]) + '%')
		catal.Lbl_Ciclos_27.setText( 'Ciclos: ' + str(estatisticas_pares[6][2]) + ' | Canceladas: ' + str(estatisticas_pares[6][4]))
		
		catal.Lbl_Porc_Ent1_27.setText ( str(estatisticas_pares[6][11]) + '%' )
		catal.Lbl_Wins_Ent1_28.setText ( 'Wins: '+str(estatisticas_pares[6][5]) )
		catal.Lbl_Hits_Ent1_27.setText ( 'Hits: '+str(estatisticas_pares[6][8]) )
		
		catal.Lbl_Porc_Gale1_27.setText ( str(estatisticas_pares[6][12]) + '%' )
		catal.Lbl_Wins_Gale1_27.setText ( 'Wins: '+str(estatisticas_pares[6][6]) )
		catal.Lbl_Hits_Gale1_27.setText ( 'Hits: '+str(estatisticas_pares[6][9]) )
		
		catal.Lbl_Porc_Gale2_27.setText ( str(estatisticas_pares[6][13]) + '%' )
		catal.Lbl_Wins_Gale2_27.setText ( 'Wins: '+str(estatisticas_pares[6][7]) )
		catal.Lbl_Hits_Gale2_27.setText ( 'Hits: '+str(estatisticas_pares[6][10]) )
	else:
		catal.Frame_Estrategia_1_27.setHidden(True)
	
	# OITAVO
	if ( len( estatisticas_pares ) > 7 ):
		catal.Frame_Estrategia_1_28.setHidden(False)
		
		catal.Lbl_Par_28.setText( estatisticas_pares[7][0] )
		catal.Lbl_Estrategia_28.setText( str(estatisticas_pares[7][14]) )
		catal.Lbl_Porcentagem_28.setText( 'Média: ' + str(estatisticas_pares[7][1]) + '%')
		catal.Lbl_Ciclos_28.setText( 'Ciclos: ' + str(estatisticas_pares[7][2]) + ' | Canceladas: ' + str(estatisticas_pares[7][4]))
		
		catal.Lbl_Porc_Ent1_28.setText ( str(estatisticas_pares[7][11]) + '%' )
		catal.Lbl_Wins_Ent1_29.setText ( 'Wins: '+str(estatisticas_pares[7][5]) )
		catal.Lbl_Hits_Ent1_28.setText ( 'Hits: '+str(estatisticas_pares[7][8]) )
		
		catal.Lbl_Porc_Gale1_28.setText ( str(estatisticas_pares[7][12]) + '%' )
		catal.Lbl_Wins_Gale1_28.setText ( 'Wins: '+str(estatisticas_pares[7][6]) )
		catal.Lbl_Hits_Gale1_28.setText ( 'Hits: '+str(estatisticas_pares[7][9]) )
		
		catal.Lbl_Porc_Gale2_28.setText ( str(estatisticas_pares[7][13]) + '%' )
		catal.Lbl_Wins_Gale2_28.setText ( 'Wins: '+str(estatisticas_pares[7][7]) )
		catal.Lbl_Hits_Gale2_28.setText ( 'Hits: '+str(estatisticas_pares[7][10]) )
	else:
		catal.Frame_Estrategia_1_28.setHidden(True)

	# NONO
	if ( len( estatisticas_pares ) > 8 ):
		catal.Frame_Estrategia_1_29.setHidden(False)
		
		catal.Lbl_Par_29.setText( estatisticas_pares[8][0] )
		catal.Lbl_Estrategia_29.setText( str(estatisticas_pares[8][14]) )
		catal.Lbl_Porcentagem_29.setText( 'Média: ' + str(estatisticas_pares[8][1]) + '%')
		catal.Lbl_Ciclos_29.setText( 'Ciclos: ' + str(estatisticas_pares[8][2]) + ' | Canceladas: ' + str(estatisticas_pares[8][4]))
		
		catal.Lbl_Porc_Ent1_29.setText ( str(estatisticas_pares[8][11]) + '%' )
		catal.Lbl_Wins_Ent1_30.setText ( 'Wins: '+str(estatisticas_pares[8][5]) )
		catal.Lbl_Hits_Ent1_29.setText ( 'Hits: '+str(estatisticas_pares[8][8]) )
		
		catal.Lbl_Porc_Gale1_29.setText ( str(estatisticas_pares[8][12]) + '%' )
		catal.Lbl_Wins_Gale1_29.setText ( 'Wins: '+str(estatisticas_pares[8][6]) )
		catal.Lbl_Hits_Gale1_29.setText ( 'Hits: '+str(estatisticas_pares[8][9]) )
		
		catal.Lbl_Porc_Gale2_29.setText ( str(estatisticas_pares[8][13]) + '%' )
		catal.Lbl_Wins_Gale2_29.setText ( 'Wins: '+str(estatisticas_pares[8][7]) )
		catal.Lbl_Hits_Gale2_29.setText ( 'Hits: '+str(estatisticas_pares[8][10]) )
	else:
		catal.Frame_Estrategia_1_29.setHidden(True)
	
	# DECIMO
	if ( len( estatisticas_pares ) > 9 ):
		catal.Frame_Estrategia_1_30.setHidden(False)
		
		catal.Lbl_Par_30.setText( estatisticas_pares[9][0] )
		catal.Lbl_Estrategia_30.setText( str(estatisticas_pares[9][14]) )
		catal.Lbl_Porcentagem_30.setText( 'Média: ' + str(estatisticas_pares[9][1]) + '%')
		catal.Lbl_Ciclos_30.setText( 'Ciclos: ' + str(estatisticas_pares[9][2]) + ' | Canceladas: ' + str(estatisticas_pares[9][4]))
		
		catal.Lbl_Porc_Ent1_30.setText ( str(estatisticas_pares[9][11]) + '%' )
		catal.Lbl_Wins_Ent1_31.setText ( 'Wins: '+str(estatisticas_pares[9][5]) )
		catal.Lbl_Hits_Ent1_2.setText ( 'Hits: '+str(estatisticas_pares[9][8]) )
		
		catal.Lbl_Porc_Gale1_30.setText ( str(estatisticas_pares[9][12]) + '%' )
		catal.Lbl_Wins_Gale1_30.setText ( 'Wins: '+str(estatisticas_pares[9][6]) )
		catal.Lbl_Hits_Gale1_30.setText ( 'Hits: '+str(estatisticas_pares[9][9]) )
		
		catal.Lbl_Porc_Gale2_30.setText ( str(estatisticas_pares[9][13]) + '%' )
		catal.Lbl_Wins_Gale2_30.setText ( 'Wins: '+str(estatisticas_pares[9][7]) )
		catal.Lbl_Hits_Gale2_30.setText ( 'Hits: '+str(estatisticas_pares[9][10]) )
	else:
		catal.Frame_Estrategia_1_30.setHidden(True)
	
	# DECIMO PRIMEIRO
	if ( len( estatisticas_pares ) > 10 ):
		catal.Frame_Estrategia_1_31.setHidden(False)
		
		catal.Lbl_Par_31.setText( estatisticas_pares[10][0] )
		catal.Lbl_Estrategia_31.setText( str(estatisticas_pares[10][14]) )
		catal.Lbl_Porcentagem_31.setText( 'Média: ' + str(estatisticas_pares[10][1]) + '%')
		catal.Lbl_Ciclos_31.setText( 'Ciclos: ' + str(estatisticas_pares[10][2]) + ' | Canceladas: ' + str(estatisticas_pares[10][4]))
		
		catal.Lbl_Porc_Ent1_31.setText ( str(estatisticas_pares[10][11]) + '%' )
		catal.Lbl_Wins_Ent1_32.setText ( 'Wins: '+str(estatisticas_pares[10][5]) )
		catal.Lbl_Hits_Ent1_31.setText ( 'Hits: '+str(estatisticas_pares[10][8]) )
		
		catal.Lbl_Porc_Gale1_31.setText ( str(estatisticas_pares[10][12]) + '%' )
		catal.Lbl_Wins_Gale1_31.setText ( 'Wins: '+str(estatisticas_pares[10][6]) )
		catal.Lbl_Hits_Gale1_31.setText ( 'Hits: '+str(estatisticas_pares[10][9]) )
		
		catal.Lbl_Porc_Gale2_31.setText ( str(estatisticas_pares[10][13]) + '%' )
		catal.Lbl_Wins_Gale2_31.setText ( 'Wins: '+str(estatisticas_pares[10][7]) )
		catal.Lbl_Hits_Gale2_31.setText ( 'Hits: '+str(estatisticas_pares[10][10]) )
	else:
		catal.Frame_Estrategia_1_31.setHidden(True)
	
	# DECIMO SEGUNDO
	if ( len( estatisticas_pares ) > 11 ):
		catal.Frame_Estrategia_1_32.setHidden(False)
		
		catal.Lbl_Par_32.setText( estatisticas_pares[11][0] )
		catal.Lbl_Estrategia_32.setText( str(estatisticas_pares[11][14]) )
		catal.Lbl_Porcentagem_32.setText( 'Média: ' + str(estatisticas_pares[11][1]) + '%')
		catal.Lbl_Ciclos_32.setText( 'Ciclos: ' + str(estatisticas_pares[11][2]) + ' | Canceladas: ' + str(estatisticas_pares[11][4]))
		
		catal.Lbl_Porc_Ent1_32.setText ( str(estatisticas_pares[11][11]) + '%' )
		catal.Lbl_Wins_Ent1_33.setText ( 'Wins: '+str(estatisticas_pares[11][5]) )
		catal.Lbl_Hits_Ent1_32.setText ( 'Hits: '+str(estatisticas_pares[11][8]) )
		
		catal.Lbl_Porc_Gale1_32.setText ( str(estatisticas_pares[11][12]) + '%' )
		catal.Lbl_Wins_Gale1_32.setText ( 'Wins: '+str(estatisticas_pares[11][6]) )
		catal.Lbl_Hits_Gale1_32.setText ( 'Hits: '+str(estatisticas_pares[11][9]) )
		
		catal.Lbl_Porc_Gale2_32.setText ( str(estatisticas_pares[11][13]) + '%' )
		catal.Lbl_Wins_Gale2_32.setText ( 'Wins: '+str(estatisticas_pares[11][7]) )
		catal.Lbl_Hits_Gale2_32.setText ( 'Hits: '+str(estatisticas_pares[11][10]) )
	else:
		catal.Frame_Estrategia_1_32.setHidden(True)
	
	estatisticas_pares.clear()

	
# >>> MHIs <<<	M1, M5 e M15
def MHI_1(_par, _tempo_de_vela, _quant, _estrategia):

	var = VARIAVEIS()
	
	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = int(dados[1][4]) 
			
			var.resultado_operacao.append(aux2)
			#print(resultado_operacao)
		
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
		
			#MHI 1
			# VERIFICA SE A ULTIMA CASA DE MINUTOS DO HORARIO É (2,3,4) OU (7,8,9)
			if( ( (min > 1) and (min < 5) )  or  ( ( (min > 6)) and (min <= 9) ) ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				if( ( (min == 4) or (min == 9) ) and (var.count_velas < 3) ):
					var.aux_cancel_by_doji = 0
					var.vela_indicada = ''
					var.calls = 0
					var.puts = 0
					var.count_velas = 0
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 3):
					var.ciclos += 1
					if(var.calls > var.puts):
						var.vela_indicada = 'PUT'
					elif(var.puts > var.calls):
						var.vela_indicada = 'CALL'
				
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 5) or (min == 0) ) and (var.vela_indicada != '') ):
				#print(aux2)
				#print ("vela_indicada: " + vela_indicada)
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
		
			if( ( (min == 6) or (min == 1) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == 7) or (min == 2) ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''

		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)	
	
	
	# >>> M5 <<<
	elif(_tempo_de_vela == 300): # M5
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M5
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')
			
			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int( dados[1][0]+dados[1][1] )
			min = dados[1][3]+dados[1][4]
			
			var.resultado_operacao.append(aux2)
		
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
		
			#MHI 5
			# VERIFICA SE A CASA DE MINUTOS DO HORARIO SÃO (15,20,25) ou (45,50,55)
			if( (min == '15') or (min == '20') or (min == '25') or (min == '45') or (min == '50') or (min == '55') ):
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				if( ( (min == '25') or (min == '55') ) and (var.count_velas < 3) ):
					var.aux_cancel_by_doji = 0
					var.vela_indicada = ''
					var.calls = 0
					var.puts = 0
					var.count_velas = 0
					
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 3):
					var.ciclos += 1
					if(var.calls > var.puts):
						var.vela_indicada = 'PUT'
					elif(var.puts > var.calls):
						var.vela_indicada = 'CALL'
					
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == '00') or (min == '30') ) and (var.vela_indicada != '') ):
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == '05') or (min == '35') ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == '10') or (min == '40') ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''

		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)
	
	# >>> M15 <<<
	elif(_tempo_de_vela == 900): # M15
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M5
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')
			
			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int( dados[1][0]+dados[1][1] )
			min = dados[1][3]+dados[1][4]
			
			var.resultado_operacao.append(aux2)
		
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
			
			#MHI 1
			# VERIFICA SE A CASA DE MINUTOS DO HORARIO SÃO (15,20,25) ou (45,50,55)
			if( (min == '15') or (min == '30') or (min == '45')  ):
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				if( (min == '45') and (var.count_velas < 3) ):
					var.aux_cancel_by_doji = 0
					var.vela_indicada = ''
					var.calls = 0
					var.puts = 0
					var.count_velas = 0
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 3):
					var.ciclos += 1
					if(var.calls > var.puts):
						var.vela_indicada = 'PUT'
					elif(var.puts > var.calls):
						var.vela_indicada = 'CALL'
					
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if(	(min == '00') and (var.vela_indicada != '')):
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if(  (min == '15') and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( (min == '30') and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''
		
		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)


def MHI_2(_par, _tempo_de_vela, _quant, _estrategia):
	
	
	var = VARIAVEIS()
	
	
	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			#min = int(dados[1][3]+dados[1][4]) 
			min = int(dados[1][4]) 
			
		
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
		
			# VERIFICA SE A ULTIMA CASA DE MINUTOS DO HORARIO É (2,3,4) OU (7,8,9)
			if( ( (min > 1) and (min < 5) )  or  ( ( (min > 6)) and (min <= 9) ) ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				if( ( (min == 4) or (min == 9) ) and (var.count_velas < 3) ):
					var.aux_cancel_by_doji = 0
					var.vela_indicada = ''
					var.calls = 0
					var.puts = 0
					var.count_velas = 0
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 3):
					var.ciclos += 1
					if(var.calls > var.puts):
						var.vela_indicada = 'PUT'
					elif(var.puts > var.calls):
						var.vela_indicada = 'CALL'
				
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0

			
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 6) or (min == 1) ) and (var.vela_indicada != '') ):
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.gale = 0
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == 7) or (min == 2) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == 8) or (min == 3) ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''

		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)

	# >>> M5 <<<
	if(_tempo_de_vela == 300): # M5
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			#min = int(dados[1][3]+dados[1][4]) 
			min = dados[1][3]+dados[1][4] 
			
		
			var.resultado_operacao.append(aux2)
			#print(resultado_operacao)
		
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
		
			# VERIFICA SE A ULTIMA CASA DE MINUTOS DO HORARIO É (2,3,4) OU (7,8,9)
			if( (min == '15') or (min == '20') or (min == '25') or (min == '45') or (min == '50') or (min == '55') ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				
				if( ( (min == '25') or (min == '55') ) and (var.count_velas < 3) ):
					var.vela_indicada = ''
					var.calls = 0
					var.puts = 0
					var.count_velas = 0
				
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 3):
					var.ciclos += 1
					if(var.calls > var.puts):
						var.vela_indicada = 'PUT'
					elif(var.puts > var.calls):
						var.vela_indicada = 'CALL'
					
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1	
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == '05') or (min == '35') ) and (var.vela_indicada != '') ):
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == '10') or (min == '40') ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == '15') or (min == '45') ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''
		
		
		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)
	

def MHI_3(_par, _tempo_de_vela, _quant, _estrategia):

	var = VARIAVEIS()
	

	
	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			#min = int(dados[1][3]+dados[1][4]) 
			min = int(dados[1][4]) 
			
		
			var.resultado_operacao.append(aux2)

			if(dados[2] == 'DOJI'):	
				var.dojis += 1
		
			#MHI 1
			# VERIFICA SE A ULTIMA CASA DE MINUTOS DO HORARIO É (2,3,4) OU (7,8,9)
			if( ( (min >= 2) and (min <= 4) )  or  ( (min >= 7) and (min <= 9) ) ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				
				if( ( (min == 4) or (min == 9) ) and (var.count_velas < 3) ):
					var.aux_cancel_by_doji = 0
					var.vela_indicada = ''
					var.calls = 0
					var.puts = 0
					var.count_velas = 0
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 3):
					var.ciclos += 1
					if(var.calls > var.puts):
						var.vela_indicada = 'PUT'
					elif(var.puts > var.calls):
						var.vela_indicada = 'CALL'
				
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 7) or (min == 2) ) and (var.vela_indicada != '') ):
				#print(aux2)
				#print ("vela_indicada: " + vela_indicada)
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
		
			
			if( ( (min == 8) or (min == 3) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == 9) or (min == 4) ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):		
					var.wins_2 += 1
				else:
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)

	# >>> M5 <<<
	if(_tempo_de_vela == 300): # M5
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M5
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			#min = int(dados[1][3]+dados[1][4]) 
			min = dados[1][3] + dados[1][4]
			
		
			var.resultado_operacao.append(aux2)
			#print(resultado_operacao)
		
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
			
		
			#MHI 3
			# VERIFICA SE A ULTIMA CASA DE MINUTOS DO HORARIO É (2,3,4) OU (7,8,9)
			if( (min == '15') or (min == '20') or (min == '25') or (min == '45') or (min == '50') or (min == '55') ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				
				if( ( (min == '25') or (min == '55') ) and (var.count_velas < 3) ):
					var.vela_indicada = ''
					var.calls = 0
					var.puts = 0
					var.count_velas = 0
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 3):
					var.ciclos += 1
					if(var.calls > var.puts):
						var.vela_indicada = 'PUT'
					elif(var.puts > var.calls):
						var.vela_indicada = 'CALL'
				
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == '15') or (min == '45') ) and (var.vela_indicada != '') ):
				#print(aux2)
				#print ("vela_indicada: " + vela_indicada)
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == '20') or (min == '50') ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == '25') or (min == '55') ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)



# >>> MILHÕES <<<	M1 e M5
def MILHAO_MINORIA(_par, _tempo_de_vela, _quant, _estrategia):
	
	var = VARIAVEIS()
	
	

	# VARIAVEL ESCLUSIVAS 
	analise_ativa = False
	
	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M5
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')
			
			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int( dados[1][0]+dados[1][1] )
			min = int (dados[1][4])
			
			var.resultado_operacao.append(aux2)
		
		
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
		
			# VERIFICA AS CASAS DE MINUTOS E SOMA ATE 5 (QUE É 1 QUADRADO DE M1)
			# POREM, SÃO EM TODAS AS VELAS, POR ISSO NÃO TERA UM IF
			# MAS SO CONTABILIZA SE A CONTAGEM DE VELAS FOR 6 E TERMINAR EM 30 OU 55	
			if( (min == 0) or (min == 5)  ): 
				analise_ativa = True
			
	
			if(analise_ativa):
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):
					var.aux_cancel_by_doji += 1
				
				var.count_velas += 1
			
		
			# VERIFICA A DIREÇÂO PARA ENTRAR
			if( var.count_velas == 5 ):
				var.ciclos += 1
				
				if(var.calls > var.puts):
					var.vela_indicada = 'PUT'
				elif(var.puts > var.calls):
					var.vela_indicada = 'CALL'
			
				if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
					var.cancel_by_doji += 1
					var.vela_indicada = ''
			
				var.calls = 0
				var.puts = 0
				var.aux_cancel_by_doji = 0
				var.count_velas = 0
			
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 0) or (min == 5) ) and (var.vela_indicada != '') ):
				#print(aux2)
				#print ("vela_indicada: " + vela_indicada)
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
	
			
			if( ( (min == 1) or (min == 6) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == 2) or (min == 7) ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''

		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)

	# >>> M5 <<<
	elif(_tempo_de_vela == 300): # M5
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M5
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')
			
			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int( dados[1][0]+dados[1][1] )
			min = dados[1][3]+dados[1][4]
			
			var.resultado_operacao.append(aux2)
		
	
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
	
			# VERIFICA AS CASAS DE MINUTOS E SOMA ATE 6 (QUE É 1 QUADRADO DE M5)
			# POREM, SÃO EM TODAS AS VELAS, POR ISSO NÃO TERA UM IF
			# MAS SO CONTABILIZA SE A CONTAGEM DE VELAS FOR 6 E TERMINAR EM 30 OU 55	
			if( (min == '00') or (min == '30')  ): 
				analise_ativa = True
			
			
			if(analise_ativa):
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
			
			
			# VERIFICA A DIREÇÂO PARA ENTRAR
			if( var.count_velas == 6 ):
				var.ciclos += 1
				var.count_velas = 0
				if(var.calls > var.puts):
					var.vela_indicada = 'PUT'
				elif(var.puts > var.calls):
					var.vela_indicada = 'CALL'
			
				if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
					var.cancel_by_doji += 1
					var.vela_indicada = ''
			
				var.calls = 0
				var.puts = 0
				var.aux_cancel_by_doji = 0
				var.count_velas = 0
		
			
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == '00') or (min == '30') ) and (var.vela_indicada != '') ):
				#print(aux2)
				#print ("vela_indicada: " + vela_indicada)
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == '05') or (min == '35') ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == '10') or (min == '40') ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''

		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)


def MILHAO_MAIORIA(_par, _tempo_de_vela, _quant, _estrategia):

	var= VARIAVEIS()
	
	

	
	# VARIAVEL ESCLUSIVAS 
	analise_ativa = False
	

	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M5
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')
			
			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int( dados[1][0]+dados[1][1] )
			min = int (dados[1][4])
			
			var.resultado_operacao.append(aux2)
		
		
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
		
		
			# VERIFICA AS CASAS DE MINUTOS E SOMA ATE 6 (QUE É 1 QUADRADO DE M5)
			# POREM, SÃO EM TODAS AS VELAS, POR ISSO NÃO TERA UM IF
			# MAS SO CONTABILIZA SE A CONTAGEM DE VELAS FOR 6 E TERMINAR EM 30 OU 55	
			if( (min == 0) or (min == 5)  ): 
				analise_ativa = True
			
			
			if(analise_ativa):
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
			
			
		
			# VERIFICA A DIREÇÂO PARA ENTRAR
			if( var.count_velas == 5 ):
				var.ciclos += 1
				if(var.calls > var.puts):
					var.vela_indicada = 'CALL'
				elif(var.puts > var.calls):
					var.vela_indicada = 'PUT'
				
				if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
					var.cancel_by_doji += 1
					var.vela_indicada = ''
			
				var.calls = 0
				var.puts = 0
				var.aux_cancel_by_doji = 0
				var.count_velas = 0
		
			
			
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 0) or (min == 5) ) and (var.vela_indicada != '') ):
				#print(aux2)
				#print ("vela_indicada: " + vela_indicada)
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada =var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == 1) or (min == 6) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == 2) or (min == 7) ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''

		
		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)


	# >>> M5 <<<
	elif(_tempo_de_vela == 300): # M5
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M5
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')
			
			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int( dados[1][0]+dados[1][1] )
			min = dados[1][3]+dados[1][4]
			
			var.resultado_operacao.append(aux2)
		
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
	
			# VERIFICA AS CASAS DE MINUTOS E SOMA ATE 6 (QUE É 1 QUADRADO DE M5)
			# POREM, SÃO EM TODAS AS VELAS, POR ISSO NÃO TERA UM IF
			# MAS SO CONTABILIZA SE A CONTAGEM DE VELAS FOR 6 E TERMINAR EM 30 OU 55	
			if( (min == '00') or (min == '30')  ): 
				analise_ativa = True
			
			
			if(analise_ativa):
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):
					var.aux_cancel_by_doji += 1
				
				var.count_velas += 1
				#print ('count velas:', count_velas)
			
			
			# VERIFICA A DIREÇÂO PARA ENTRAR
			if( var.count_velas == 6 ):
				var.ciclos += 1
				if(var.calls > var.puts):
					var.vela_indicada = 'CALL'
				elif(var.puts > var.calls):
					vela_indicada = 'PUT'
			
				if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
					var.cancel_by_doji += 1
					var.vela_indicada = ''
		
				var.calls = 0
				var.puts = 0
				var.aux_cancel_by_doji = 0
				var.count_velas = 0
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == '00') or (min == '30') ) and (var.vela_indicada != '') ):
				#print(aux2)
				#print ("vela_indicada: " + vela_indicada)
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == '05') or (min == '35') ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == '10') or (min == '40') ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''

		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)



# >>> TURN OVER <<<		M15
def TURN_OVER(_par, _tempo_de_vela, _quant, _estrategia):

	var = VARIAVEIS()
	
	
	
	# >>> M15 <<<
	if(_tempo_de_vela == 900): # M15
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M5
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')
			
			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int( dados[1][0]+dados[1][1] )
			min = dados[1][3]+dados[1][4]
			
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
			
		
			# VERIFICA SE A VELA DE MINUTO 45 É VERDE OU VERMELHA, SENDO UM OU OUTRA A ENTRADA É O CONTRARIO
			# EXEMPLO: SE VELA DE 45 FOR VERDE, ENTAO ENTRADA É VERMELHA
			if( (min == '45') ):
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'PUT'
					elif(var.puts > 0):
						var.vela_indicada = 'CALL'
						
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
					
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
		
			
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if(	(min == '00') and var.vela_indicada != '' ):
				#print(aux2)
				#print ("vela_indicada: " + vela_indicada)
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if(  (min == '15') and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( (min == '30') and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''
		
		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)



# >>> TORRES GEMEAS <<<		M1, M5 E M15
def TORRES_GEMEAS(_par, _tempo_de_vela, _quant, _estrategia):
	
	var = VARIAVEIS()
	
	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = int(dados[1][4]) 
			
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
			
			if( (min == 0) or (min == 5) ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'CALL'
					elif(var.puts > 0):
						var.vela_indicada = 'PUT'
					
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 4) or (min == 9) ) and (var.vela_indicada != '') ):
				
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == 5) or (min == 0) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == 6) or (min == 1) ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)

	# >>> M5 <<<
	elif(_tempo_de_vela == 300): # M5
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M5
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')
			
			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int( dados[1][0]+dados[1][1] )
			min = dados[1][3]+dados[1][4]
			
			var.resultado_operacao.append(aux2)
		
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
		
			#MHI 5
			# VERIFICA SE A CASA DE MINUTOS DO HORARIO SÃO (15,20,25) ou (45,50,55)
			if( (min == '00') or (min == '30') ):
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'CALL'
					elif(var.puts > 0):
						var.vela_indicada = 'PUT'
						
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( (min == '25') or (min == '55') and (var.vela_indicada != '') ):
				#print(aux2)
				#print ("vela_indicada: " + vela_indicada)
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == '30') or (min == '00') ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == '35') or (min == '05') ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''

		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)
	
	# >>> M15 <<<
	elif(_tempo_de_vela == 900): # M15
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M5
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')
			
			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int( dados[1][0]+dados[1][1] )
			min = dados[1][3]+dados[1][4]
			
			var.resultado_operacao.append(aux2)
		
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
		
			if( min == '00' ):
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'CALL'
					elif(var.puts > 0):
						var.vela_indicada = 'PUT'
					
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if(	(min == '45') and (var.vela_indicada != '') ):
				#print(aux2)
				#print ("vela_indicada: " + vela_indicada)
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if(  (min == '00') and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( (min == '15') and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''
		
		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)



# >>> FLIPs <<<		SEVEN FLIP: M1	|	FIVE FLIP: M5
def FIVE_FLIP(_par, _tempo_de_vela, _quant, _estrategia): #M5
	
	var = VARIAVEIS()
	
	

	
	# >>> M5 <<<
	if(_tempo_de_vela == 300): # M5
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M5
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = dados[1][3]+dados[1][4]
			
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
			
			if( (min == '20') or (min == '50') ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'PUT'
					elif(var.puts > 0):
						var.vela_indicada = 'CALL'
				
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
					
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == '25') or (min == '55') ) and (var.vela_indicada != '') ):
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == '30') or (min == '00') ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == '35') or (min == '05') ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)


def SEVEN_FLIP(_par, _tempo_de_vela, _quant, _estrategia): #M1
	
	var = VARIAVEIS()
	


	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = int(dados[1][4]) 
			
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
			
			if( (min == 6) ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'PUT'
					elif(var.puts > 0):
						var.vela_indicada = 'CALL'
				
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
					
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( (min == 7) and (var.vela_indicada != '') ):
				
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( (min == 8) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( (min == 9) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)



# >>> TRES <<< 		MOSQUETEIROS: M1 | VIZINHOS: M1 e M5
def TRES_MOSQUETEIROS(_par, _tempo_de_vela, _quant, _estrategia):
	
	var = VARIAVEIS()
	
	

	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = int(dados[1][4]) 
			
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
			
			if( (min == 2) or (min == 7) ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'CALL'
					elif(var.puts > 0):
						var.vela_indicada = 'PUT'
						
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 3) or (min == 8) ) and (var.vela_indicada != '') ):
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
				
			
			if( ( (min == 4) or (min == 9) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == 5) or (min == 0) ) and (var.gale == 2)):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)
	

def TRES_VIZINHOS(_par, _tempo_de_vela, _quant, _estrategia):
	
	var = VARIAVEIS()
	
	

	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = int(dados[1][4]) 
			
			var.resultado_operacao.append(aux2)
			#print(resultado_operacao)
		
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
		
			#MHI 1
			# VERIFICA SE A ULTIMA CASA DE MINUTOS DO HORARIO É (2,3,4) OU (7,8,9)
			if( (min == 3) or (min == 8) ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'CALL'
					elif(var.puts > 0):
						var.vela_indicada = 'PUT'
					
					if( var.aux_cancel_by_doji > 0 ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 4) or (min == 9) ) and (var.vela_indicada != '') ):
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == 5) or (min == 0) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == 6) or (min == 1) ) and (var.gale == 2)):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)


	# >>> M5 <<<
	if(_tempo_de_vela == 300): # M5
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0] + dados[1][1])
			min = dados[1][3] + dados[1][4] 
			
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
			
			if( (min == '15') or (min == '45') ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'CALL'
					elif(var.puts > 0):
						var.vela_indicada = 'PUT'
				
					if( var.aux_cancel_by_doji > 0 ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
				
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == '20') or (min == '50') ) and (var.vela_indicada != '') ):
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == '25') or (min == '55') ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == '00') or (min == '30') ) and (var.gale == 2)):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''

		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)



# >>> PADRÕES <<<		M1
def PADRAO_IMPAR(_par, _tempo_de_vela, _quant, _estrategia):

	var = VARIAVEIS()
	

	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = int(dados[1][4]) 
			
			var.resultado_operacao.append(aux2)
			
			if (dados[2] == 'DOJI'):
				var.dojis += 1
			
			if( (min == 2) or (min == 7)):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'CALL'
					elif(var.puts > 0):
						var.vela_indicada = 'PUT'
					
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
					
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 0) or (min == 5) ) and (var.vela_indicada != '') ):
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == 2) or (min == 7) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == 4) or (min == 9) ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)


def R7(_par, _tempo_de_vela, _quant, _estrategia):

	var = VARIAVEIS()
	
	


	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = int(dados[1][4]) 
			
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
			
			if (min == 8):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
		
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÃO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'CALL'
					elif(var.puts > 0):
						var.vela_indicada = 'PUT'
				
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
						
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( (min == 6) and (var.vela_indicada != '') ):
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( (min == 7) or (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
					var.ativar = False
				else:
					var.loss_1 += 1
					var.gale += 1

			if( (min == 8) or (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)
	

def PADRAO_23(_par, _tempo_de_vela, _quant, _estrategia):
	
	var = VARIAVEIS()
	
	

	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = int(dados[1][4]) 
			
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
			
			if( (min == 0) or (min == 5) ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(var.calls > 0):
						var.vela_indicada = 'CALL'
					elif(var.puts > 0):
						var.vela_indicada = 'PUT'
					
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
					
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 1) or (min == 6) ) and (var.vela_indicada != '') ):
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
				
			
			if( ( (min == 2) or (min == 7) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == 3) or (min == 8) ) and (var.gale == 2)):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)
	
	
def MELHOR_DE_3(_par, _tempo_de_vela, _quant, _estrategia):

	var = VARIAVEIS()
	
	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1
	
		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = int(dados[1][4]) 
			
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1
			
			if( ( (min >= 1) and (min <= 3) ) or ( (min >= 6) and  (min <= 8) ) ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 3):
					var.ciclos += 1
					if(var.calls > var.puts):
						var.vela_indicada = 'CALL'
					elif(var.puts > var.calls):
						var.vela_indicada = 'PUT'
					
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
					
					var.calls = 0
					var.puts = 0
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE
		
			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 2) or (min == 7) ) and (var.vela_indicada != '') ):
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada
		
				var.vela_indicada = ''
			
			if( ( (min == 3) or (min == 8) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == 4) or (min == 9) ) and (var.gale == 2)):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)
	
'''
def C3(_par, _tempo_de_vela, _quant):	
	
	var = VARIAVEIS()


	# VARIAVEIS EXCLUSIVAS
	ativado = False
	vela_gale_1 = ''
	aux_gale_1 = ''
	vela_gale_2 = ''
	aux_gale_2 = ''
	vela_primeira_entrada = ''

	# >>> M1 <<<
	if(_tempo_de_vela == 60): # M1

		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = int(dados[1][4]) 
			
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):
				var.dojis += 1

			#MHI 1
			# VERIFICA SE A ULTIMA CASA DE MINUTOS DO HORARIO É (0) OU (5)
			if( (min == 0) or (min == 5) ):
			
				ativado = True
				
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				# VERIFICA A DIREÇÃO PARA ENTRAR
				if(var.count_velas == 1):
					var.ciclos += 1
					if(ativado == True):
						if(var.vela_indicada == ''):
							vela_primeira_entrada = dados[2]
						else:
							vela_primeira_entrada = var.vela_indicada
						
				
					if(var.calls > 0):
						var.vela_indicada = 'CALL'
					elif(var.puts > 0):
						var.vela_indicada = 'PUT'
					
					if( (var.aux_cancel_by_doji > 0) or (var.calls == var.puts) ):
						var.vela_indicada = ''
						vela_primeira_entrada = ''
						vela_gale_1 = ''
						aux_gale_1 = ''
						vela_gale_2 = ''
						aux_gale_2 = '' 
						ativado = False
						
					var.calls = 0 
					var.puts = 0
					var.count_velas = 0
			
			
			if( (min == 2) or (min == 7) ):
				if(ativado == True):
					aux_gale_1 = vela_gale_1
				
				vela_gale_1 = dados[2]
		
			if( ( (min == 4) or (min == 9) ) ):
				if(ativado == True):
					aux_gale_2 = vela_gale_2
				
				vela_gale_2 = dados[2]


			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == 0) or (min == 5) ) and (vela_primeira_entrada != '') ):
				
				if(dados[2] == vela_primeira_entrada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = vela_gale_1

				#vela_indicada = dados[2]

			
			if( ( (min == 2) or (min == 7) ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1
					var.aux_vela_indicada = vela_gale_2

			if( ( (min == 4) or (min == 9) ) and (var.gale == 2)):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''

		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)
'''


# >>> TRIPLICAÇÂO <<<		M5	
def TRIPLICACAO(_par, _tempo_de_vela, _quant, _estrategia):
	
	var = VARIAVEIS()


	# >>> M5 <<<
	if(_tempo_de_vela == 300): # M5

		# VERIFICAÇÃO DO RESULTADO DAS VELAS DE M1
		for velas in lista_catalogacao:
			resultado = ''
			if (velas['open'] < velas['close']):	
				resultado = 'CALL'
			elif (velas['open'] > velas['close']):
				resultado = 'PUT'
			elif (velas['open'] == velas['close']):
				resultado = 'DOJI'
				
			#print(timestamp_converter(velas['from']) + ' Open: ' , velas['open'], ' Close: ', velas['close'], ' ' + resultado)	
			
			aux = timestamp_converter(velas['from']) + " " + resultado # >>> EXEMPLO: aux = 2020-08-02 14:55:00 CALL  
			dados = aux.split(' ')

			dia = dados[0][8]+dados[0][9]
			mes = dados[0][5]+dados[0][6]
			
			aux2 = ['','','','']
			aux2[0] = mes
			aux2[1] = dia
			aux2[2] = dados[1] # HORARIO
			aux2[3] = dados[2] # DIREÇÂO

			horas = int(dados[1][0]+dados[1][1])
			min = dados[1][3]+dados[1][4]
			
			var.resultado_operacao.append(aux2)
			
			if(dados[2] == 'DOJI'):	
				var.dojis += 1

			if( (min == '00') or (min == '05') or (min == '15') or (min == '20') or (min == '30') or (min == '35') or (min == '45') or (min == '50') ):
			
				if(dados[2] == 'CALL'):
					var.calls += 1
				elif(dados[2] == 'PUT'):
					var.puts += 1
				elif(dados[2] == 'DOJI'):	
					var.aux_cancel_by_doji += 1
			
				var.count_velas += 1
				#print ('count velas:', count_velas)
				
				if( ( (min == '05') or (min == '20') or (min == '35') or (min == '50') ) and (var.count_velas <= 1 ) ):
					var.aux_cancel_by_doji = 0
					var.vela_indicada = ''
					var.calls = 0
					var.puts = 0
					var.count_velas = 0
				
				# VERIFICA A DIREÇÂO PARA ENTRAR
				if(var.count_velas == 2):
					var.ciclos += 1
					if(var.calls == 2):
						var.vela_indicada = 'CALL'
					elif(var.puts == 2):
						var.vela_indicada = 'PUT'
					elif ( var.calls == var.puts ):
						var.vela_indicada = ''
				
					if( (var.aux_cancel_by_doji > 0) ):
						var.cancel_by_doji += 1
						var.vela_indicada = ''
		
					var.calls = 0
					var.puts = 0	
					var.aux_cancel_by_doji = 0
					var.count_velas = 0
			
			# COLOCAR OPÇÃO DE SO ENTRADA / COM 1 MARTINGALE / COM 2 MARTINGALE

			# VERIFICA SE VELA_INDICADA É A MESMA DO SINAL CATALOGADO, CONFIGURANDO ASSIM UM WIN OU LOSS
			if( ( (min == '10') or (min == '25') or (min == '40') or (min == '55') ) and (var.vela_indicada != '') ):
			
				if(dados[2] == var.vela_indicada):	
					#print('WIN')
					var.wins += 1
					var.wins_1 += 1
					var.wins_2 += 1
					var.aux_vela_indicada = ''
				else:
					var.gale += 1
					var.loss += 1
					var.aux_vela_indicada = var.vela_indicada

				var.vela_indicada = ''
			
			if( ( (min == '00') or (min == '15') or (min == '30') or (min == '45') ) and (var.gale == 1) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 1')
					var.wins_1 += 1
					var.wins_2 += 1
					var.gale = 0
					var.aux_vela_indicada = ''
				else:
					var.loss_1 += 1
					var.gale += 1

			if( ( (min == '05') or (min == '20') or (min == '35') or (min == '50') ) and (var.gale == 2) ):
				if(dados[2] == var.aux_vela_indicada):	
					#print('WIN GALE 2')
					var.wins_2 += 1
				else:
					#print('LOSS')
					var.loss_2 += 1
			
				var.gale = 0
				var.aux_vela_indicada = ''


		ESTATISTICA(_par, var.ciclos, var.dojis, var.cancel_by_doji, var.wins, var.wins_1, var.wins_2, var.loss, var.loss_1, var.loss_2, _estrategia)
	
	

def CHECK_TIMEFRAME():
	global catal

	if (catal.CBox_Timeframe.currentText() == "M1"):
		
		catal.CBox_Estrategia.clear()
		catal.CBox_Estrategia.addItems(["MHI 1", "MHI 2", "MHI 3", "MELHOR DE 3", "MILHÃO MAIORIA", "MILHÃO MINORIA", "PADRÃO 23", "PADRÃO ÍMPAR", "R7", "TORRES GÊMEAS", "TRÊS MOSQUETEIROS", "TRÊS VIZINHOS", "SEVEN FLIP"])
		
		if ( catal.CBox_Periodo_De_Catalogacao.count() > 0):
			catal.CBox_Periodo_De_Catalogacao.clear()
		
		catal.CBox_Periodo_De_Catalogacao.addItems(["2 Horas" , "3 Horas", "4 Horas" , "5 Horas"])# 120 = 2H / 180 = 3H / 240 = 4H | 300 = 5H RECOMENDADO: 3H = 180
	
	if (catal.CBox_Timeframe.currentText() == "M5"):
		
		catal.CBox_Estrategia.clear()
		catal.CBox_Estrategia.addItems(["FIVE FLIP", "MHI 1", "MHI 2", "MHI 3", "MILHÃO MAIORIA", "MILHÃO MINORIA", "TORRES GÊMEAS", "TRÊS VIZINHOS", "TRIPLICAÇÃO"])
		
		if ( catal.CBox_Periodo_De_Catalogacao.count() > 0):
			catal.CBox_Periodo_De_Catalogacao.clear()
		
		catal.CBox_Periodo_De_Catalogacao.addItems(["8 Horas", "12 Horas", "1 Dia", "2 Dias", "3 Dias"])# 96 = 8H / 144 = 12H / 288 = 24H / 576 = 48H / 842 = 72H | RECOMENDADO: 12H = 144

	if (catal.CBox_Timeframe.currentText() == "M15"):

		catal.CBox_Estrategia.clear()
		catal.CBox_Estrategia.addItems(["MHI 1", "TORRES GÊMEAS", "TURN OVER"])
		
		if ( catal.CBox_Periodo_De_Catalogacao.count() > 0):
			catal.CBox_Periodo_De_Catalogacao.clear()
		
		catal.CBox_Periodo_De_Catalogacao.addItems(["12 Horas", "1 Dia", "2 Dias", "3 Dias", "4 Dias", "5 Dias"]) # 48 = 12H / 96 = 24H / 192 = 48H / 288 = 72H / 384 = 96H / 480 = 120H



def TEMPO_DE_VELA(_tempo_expiracao):

	if(_tempo_expiracao == 'M1'):
		return (1 * 60) # POR PADRÃO É 60SEG, ALTERAR TEMPO EM CONFIG
	if(_tempo_expiracao == 'M5'):
		return (5 * 60) # POR PADRÃO É 60SEG, ALTERAR TEMPO EM CONFIG
	if(_tempo_expiracao == 'M15'):
		return (15 * 60) # POR PADRÃO É 60SEG, ALTERAR TEMPO EM CONFIG



def QUANT_DE_VELAS(_quant):

	#M1: 120 = 2H / 180 = 3H / 240 = 4H | 300 = 5H | RECOMENDADO: 3H = 180
	#M5: 96 = 8H / 144 = 12H / 288 = 24H / 576 = 48H / 842 = 72H | RECOMENDADO: 12H = 144
	#M15: 48 = 12H / 96 = 24H / 192 = 48H / 288 = 72H / 384 = 96H / 480 = 120H
	
	#M1: "2 Horas" , "3 Horas", "4 Horas" , "5 Horas"
	#M5: "8 Horas", "12 Horas", "1 Dia", "2 Dias", "3 Dias"
	#M15: "12 Horas", "1 Dia", "2 Dias", "3 Dias", "4 Dias", "5 Dias"
	
	if( TEMPO_DE_VELA( catal.CBox_Timeframe.currentText() ) == 60 ):
		if(_quant == '2 Horas'):
			return 120

		if(_quant == '3 Horas'):
			return 180
		
		if(_quant == '4 Horas'):
			return 240
		
		if(_quant == '5 Horas'):
			return 300
	
	if( TEMPO_DE_VELA( catal.CBox_Timeframe.currentText() ) == 300 ):
	
		if(_quant == '8 Horas'):
			return 96
		
		if(_quant == '12 Horas'):
			return 144
	
		if(_quant == '1 Dia'):
			return 288
		
		if(_quant == '2 Dias'):
			return 576
		
		if(_quant == '3 Dias'):
			return 842
	
	if( TEMPO_DE_VELA( catal.CBox_Timeframe.currentText() ) == 900 ):
		if(_quant == '12 Horas'):
			return 48
		
		if(_quant == '1 Dia'):
			return 96
		
		if(_quant == '2 Dias'):
			return 192
		
		if(_quant == '3 Dias'):
			return 288
		
		if(_quant == '4 Horas'):
			return 384
		
		if(_quant == '5 Horas'):
			return 480
	

# TESTE PRA SABER SE DA ERROR
'''
def PAR_CATALOGAR():

	CATALOGAR(pares, TEMPO_DE_VELA(1), )
	CATALOGAR(pares, TEMPO_DE_VELA(5), )
	CATALOGAR(pares, TEMPO_DE_VELA(15), )
'''


def CARREGAR_LISTA(_tipo_de_mercado):
	
	par = API.get_all_open_time()
	lista_pares = []

	for paridade in par['turbo']:
		if par['turbo'][paridade]['open'] == True:
			#print('[ TURBO ]: '+paridade)
			
			if(len(lista_pares) == 0):
				lista_pares.append(paridade)
			else:
			
				j = len(lista_pares)
				
				for i in range(0, len(lista_pares)):
					
					while (j > 0):
						if(paridade == lista_pares[j-1] ):
							break
							
						j -= 1
						if(j==0):
							lista_pares.append(paridade)


	for paridade in par['digital']:
		if par['digital'][paridade]['open'] == True:
			#print('[ DIGITAL ]: '+paridade)
			
			if(len(lista_pares) == 0):
				lista_pares.append(paridade)
			else:

				j = len(lista_pares)
				for i in range(0, len(lista_pares)):
				
					while (j > 0):
						if(paridade == lista_pares[j-1] ):
							break
					
						j -= 1
						if(j==0):
							lista_pares.append(paridade)

	print(lista_pares)
	
	remover = []
	
	if(_tipo_de_mercado == 'OTC'):
		for i in range (0 , len(lista_pares)):
			if( not 'OTC' in lista_pares[i]):
				remover.append(i)
		
		if(len(remover) == len(lista_pares)):
			return 'NULL'
	
	if(_tipo_de_mercado == 'Normal'):
		for i in range (0 , len(lista_pares)):
			if( 'OTC' in lista_pares[i]):
				remover.append(i)
		
		if(len(remover) == len(lista_pares)):
			return 'NULL'
	
	
	
	print(remover)
	
	for i in range (0, len(remover)):
		print (int(remover[i]) )
    
		if(i==0):	
			lista_pares.pop( int(remover[i]) )
		else:	
			lista_pares.pop( int(remover[i])-1 )
	
	
	
	print(lista_pares)
	return lista_pares


def BTN_CATALOGAR():
	
	global catal
	global lista_Pares
	global lista_Pares_OTC
	global lista_catalogacao
	global estatisticas_pares
	global lista_criada
	

	
	
	if( len(estatisticas_pares) > 0):
		estatisticas_pares.clear()
	
	catal.Btn_Catalogar.setCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
	
	# 120 = 2H / 180 = 3H / 240 = 4H | 300 = 5H | RECOMENDADO: 3H = 180
	# 96 = 8H / 144 = 12H / 288 = 24H / 576 = 48H / 842 = 72H | RECOMENDADO: 12H = 144
	# 48 = 12H / 96 = 24H / 192 = 48H / 288 = 72H / 384 = 96H / 480 = 120H
	
	tempo_de_vela = TEMPO_DE_VELA( catal.CBox_Timeframe.currentText() )
	quant_de_velas = QUANT_DE_VELAS( catal.CBox_Periodo_De_Catalogacao.currentText() )
	estrategia = catal.CBox_Estrategia.currentText()
	
	
	# MERCADO NORMAL (SEMANA)
	if ( catal.CBox_M_Normal.isChecked() ):
		
		lista_teste = CARREGAR_LISTA('Normal')
		
		if(lista_teste == 'NULL'):
			catal.Btn_Catalogar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
			return
		
		for par in lista_teste:
			CATALOGAR_PARES( par, tempo_de_vela, quant_de_velas, estrategia, 'estrategia')
	
	# MERCADO EM OTC (FIM DE SEMANA)
	elif ( catal.CBox_M_OTC.isChecked() ) :
	
		lista_teste = CARREGAR_LISTA('OTC')
		
		if(lista_teste == 'NULL'):
			catal.Btn_Catalogar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
			return
	
		for par in lista_teste:
			CATALOGAR_PARES( par, tempo_de_vela, quant_de_velas, estrategia, 'estrategia')
	
	elif( ( catal.CBox_M_OTC.isChecked() == False ) and ( catal.CBox_M_Normal.isChecked() == False ) ):
		pass

	lista_catalogacao.clear()
	lista_criada = False

	catal.Btn_Catalogar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
	
	if( catal.CBox_M_OTC.isChecked() or catal.CBox_M_Normal.isChecked() ):
		CATAL_POR_ESTRATEGIA()
	
	

def CATALOGAR_PARES(par, tempo_de_vela, quant, _estrategia, _metodo):
	
	global lista_criada
	global lista_catalogacao
	tempo = time.time()
	
	if( tempo_de_vela == 60 ): # M1 >>> 120 = 2H / 180 = 3H / 240 = 4H | RECOMENDADO: 3H = 180
		vela = API.get_candles(par, tempo_de_vela, quant, tempo)
		
		if(_metodo == 'estrategia'):
			lista_catalogacao = vela + lista_catalogacao
	
		elif( (_metodo == 'par') and  (lista_criada == False) ):
			lista_catalogacao = vela + lista_catalogacao
			lista_criada = True
		
		tempo = int(vela[0]['from']) - 1

	elif ( tempo_de_vela == 300 ): # M5 >>> 96 = 8H / 144 = 12H / 288 = 24H / 576 = 48H / 842 = 72H | RECOMENDADO: 12H = 144
		vela = API.get_candles(par, tempo_de_vela, quant, tempo)
		
		if(_metodo == 'estrategia'):
			lista_catalogacao = vela + lista_catalogacao
		
		elif( (_metodo == 'par') and  (lista_criada == False) ):
			lista_catalogacao = vela + lista_catalogacao
			lista_criada = True
		
		tempo = int(vela[0]['from']) - 1
	
	elif ( tempo_de_vela == 900  ): # M15 >>> 48 = 12H / 96 = 24H / 192 = 48H / 288 = 72H / 384 = 96H / 480 = 120H
		vela = API.get_candles(par, tempo_de_vela, quant, tempo)
		
		if(_metodo == 'estrategia'):
			lista_catalogacao = vela + lista_catalogacao
		
		elif( (_metodo == 'par') and  (lista_criada == False) ):
			lista_catalogacao = vela + lista_catalogacao
			lista_criada = True
		
		tempo = int(vela[0]['from']) - 1
	
	
	
	
	if(_estrategia == 'MHI 1'):
		MHI_1(par, tempo_de_vela, quant, 'MHI 1')
	
	if(_estrategia == 'MHI 2'):
		MHI_2(par, tempo_de_vela, quant, 'MHI 2')
	
	if(_estrategia == 'MHI 3'):
		MHI_3(par, tempo_de_vela, quant, 'MHI 3')
	
	if(_estrategia == 'MILHÃO MINORIA'):
		MILHAO_MINORIA(par, tempo_de_vela, quant, 'MILHÃO MINORIA')
		
	if(_estrategia == 'MILHÃO MAIORIA'):
		MILHAO_MAIORIA(par, tempo_de_vela, quant, 'MILHÃO MAIORIA')
	
	if(_estrategia == 'TURN OVER'):
		TURN_OVER(par, tempo_de_vela, quant, 'TURN OVER')
	
	if(_estrategia == 'TORRES GÊMEAS'):
		TORRES_GEMEAS(par, tempo_de_vela, quant, 'TORRES GÊMEAS')
	
	if(_estrategia == 'FIVE FLIP'):
		FIVE_FLIP(par, tempo_de_vela, quant, 'FIVE FLIP')

	if(_estrategia == 'SEVEN FLIP'):
		SEVEN_FLIP(par, tempo_de_vela, quant, 'SEVEN FLIP')
	
	if(_estrategia == 'TRÊS MOSQUETEIROS'):
		TRES_MOSQUETEIROS(par, tempo_de_vela, quant, 'TRÊS MOSQUETEIROS')
	
	if(_estrategia == 'TRÊS VIZINHOS'):
		TRES_VIZINHOS(par, tempo_de_vela, quant, 'TRÊS VIZINHOS')
	
	if(_estrategia == 'PADRÃO ÍMPAR'):
		PADRAO_IMPAR(par, tempo_de_vela, quant, 'PADRÃO ÍMPAR')
	
	if(_estrategia == 'R7'):
		R7(par, tempo_de_vela, quant, 'R7')
	
	if(_estrategia == 'PADRÃO 23'):
		PADRAO_23(par, tempo_de_vela, quant, 'PADRÃO 23')
	
	if(_estrategia == 'MELHOR DE 3'):
		MELHOR_DE_3(par, tempo_de_vela, quant, 'MELHOR DE 3')
	
	'''
	if(_estrategia == 'C3'):
		C3(par, tempo_de_vela, quant, 'C3')
	'''
	
	if(_estrategia == 'TRIPLICAÇÃO'):
		TRIPLICACAO(par, tempo_de_vela, quant, 'TRIPLICAÇÃO')

	
	if(_metodo == 'estrategia'):
		lista_catalogacao = []
	
	
#=======================================================================================================
# NORMAL
def CAT_Btn_AUDCAD():
	BTN_PAR_CATALOGAR('AUDCAD')

def CAT_Btn_AUDJPY():
	BTN_PAR_CATALOGAR('AUDJPY')

def CAT_Btn_AUDUSD():
	BTN_PAR_CATALOGAR('AUDUSD')

def CAT_Btn_CADCHF():
	BTN_PAR_CATALOGAR('CADCHF')

def CAT_Btn_CADJPY():
	BTN_PAR_CATALOGAR('CADJPY')

def CAT_Btn_CHFJPY():
	BTN_PAR_CATALOGAR('CHFJPY')

def CAT_Btn_EURAUD():
	BTN_PAR_CATALOGAR('EURAUD')

def CAT_Btn_EURCAD():
	BTN_PAR_CATALOGAR('EURCAD')

def CAT_Btn_EURGBP():
	BTN_PAR_CATALOGAR('EURGBP')

def CAT_Btn_EURJPY():
	BTN_PAR_CATALOGAR('EURJPY')

def CAT_Btn_EURNZD():
	BTN_PAR_CATALOGAR('EURNZD')

def CAT_Btn_EURUSD():
	BTN_PAR_CATALOGAR('EURUSD')

def CAT_Btn_GBPAUD():
	BTN_PAR_CATALOGAR('GBPAUD')

def CAT_Btn_GBPCAD():
	BTN_PAR_CATALOGAR('GBPCAD')

def CAT_Btn_GBPCHF():
	BTN_PAR_CATALOGAR('GBPCHF')

def CAT_Btn_GBPJPY():
	BTN_PAR_CATALOGAR('GBPJPY')

def CAT_Btn_GBPNZD():
	BTN_PAR_CATALOGAR('GBPNZD')

def CAT_Btn_GBPUSD():
	BTN_PAR_CATALOGAR('GBPUSD')
	
def CAT_Btn_NZDUSD():
	BTN_PAR_CATALOGAR('NZDUSD')

def CAT_Btn_USDCAD():
	BTN_PAR_CATALOGAR('USDCAD')

def CAT_Btn_USDCHF():
	BTN_PAR_CATALOGAR('USDCHF')

def CAT_Btn_USDJPY():
	BTN_PAR_CATALOGAR('USDJPY')

def CAT_Btn_USDNOK():
	BTN_PAR_CATALOGAR('USDNOK')

#======================================================
# OTC
def CAT_Btn_AUDCAD_OTC():
	BTN_PAR_CATALOGAR('AUDCAD-OTC')
	
def CAT_Btn_EURGBP_OTC():
	BTN_PAR_CATALOGAR('EURGBP-OTC')
	
def CAT_Btn_EURJPY_OTC():
	BTN_PAR_CATALOGAR('EURJPY-OTC')
	
def CAT_Btn_EURUSD_OTC():
	BTN_PAR_CATALOGAR('EURUSD-OTC')
	
def CAT_Btn_GBPJPY_OTC():
	BTN_PAR_CATALOGAR('GBPJPY-OTC')
	
def CAT_Btn_GBPUSD_OTC():
	BTN_PAR_CATALOGAR('GBPUSD-OTC')
	
def CAT_Btn_NZDUSD_OTC():
	BTN_PAR_CATALOGAR('NZDUSD-OTC')
	
def CAT_Btn_USDCHF_OTC():
	BTN_PAR_CATALOGAR('USDCHF-OTC')
	
def CAT_Btn_USDJPY_OTC():
	BTN_PAR_CATALOGAR('USDJPY-OTC')
	
	
	
#========================================================
# CATALOGAÇÃO
	
	


def BTN_PAR_CATALOGAR(par):

	global catal
	global lista_catalogacao
	global estatisticas_pares
	global lista_criada
	
	lista_estrategias = []
	
	if( len(estatisticas_pares) > 0):
		estatisticas_pares.clear()
	
	for i in range( 0, catal.CBox_Estrategia.count() ):
		#print ( catal.CBox_Estrategia.itemText(i) )
		lista_estrategias.append( catal.CBox_Estrategia.itemText(i) )

	
	tempo_de_vela = TEMPO_DE_VELA( catal.CBox_Timeframe.currentText() )
	quant_de_velas = QUANT_DE_VELAS( catal.CBox_Periodo_De_Catalogacao.currentText() )


	for _estrategia in lista_estrategias:
		CATALOGAR_PARES( par, tempo_de_vela, quant_de_velas, _estrategia, 'par')
	
	lista_catalogacao.clear()
	lista_criada = False
	
	CATAL_POR_ESTRATEGIA()
	
	
	
def SET_M_NORMAL():
	global catal
	
	#print('NORMAL')
	#catal.CBox_M_Normal.setChecked(True)
	catal.CBox_M_OTC.setChecked(False)
	

def SET_M_OTC():
	global catal
	
	#print('OTC')
	catal.CBox_M_Normal.setChecked(False)
	


#=================================================================================================================




'''
def CHECK_SESSION(_email, _sessao):
	
	while True:
		payload_session = {'email': _email, 'sessao': _sessao}
		r_session = requests.post('https://traderautomatico.000webhostapp.com/catalogador/checksession.php', data = payload_session)
		print(r_session.text)
		
		if(r_session.text != 'ok'):
			SAIR()
			break
		
		time.sleep(10)
'''
#=================================================================================================================


sair = False

# LOGIN PAGE
catal.Btn_Login.clicked.connect(LOGIN)
catal.Btn_Registrar.clicked.connect(REGISTER_PAGE)
catal.Btn_Visualizar_Senha.clicked.connect(SHOW_SENHA)
catal.Btn_Visualizar_Senha_IQ.clicked.connect(SHOW_SENHA_IQ)


#REGISTER PAGE
catal.Btn_Registrar_Register.clicked.connect(REGISTRAR)
catal.Btn_Voltar.clicked.connect(LOGIN_PAGE)
catal.Btn_Visualizar_Senha_Registrar.clicked.connect(SHOW_SENHA_REGISTRAR)

#LOGIC
catal.CBox_Timeframe.currentTextChanged.connect(CHECK_TIMEFRAME)
catal.Btn_Catalogar.clicked.connect(BTN_CATALOGAR)

# NORMAL =======================================================
catal.Btn_AUDCAD.clicked.connect(CAT_Btn_AUDCAD)
catal.Btn_AUDJPY.clicked.connect(CAT_Btn_AUDJPY)
catal.Btn_AUDUSD.clicked.connect(CAT_Btn_AUDUSD)
catal.Btn_CADCHF.clicked.connect(CAT_Btn_CADCHF)
catal.Btn_CADJPY.clicked.connect(CAT_Btn_CADJPY)
catal.Btn_CHFJPY.clicked.connect(CAT_Btn_CHFJPY)
catal.Btn_EURAUD.clicked.connect(CAT_Btn_EURAUD)
catal.Btn_EURCAD.clicked.connect(CAT_Btn_EURCAD)
catal.Btn_EURGBP.clicked.connect(CAT_Btn_EURGBP)
catal.Btn_EURJPY.clicked.connect(CAT_Btn_EURJPY)
catal.Btn_EURNZD.clicked.connect(CAT_Btn_EURNZD)
catal.Btn_EURUSD.clicked.connect(CAT_Btn_EURUSD)
catal.Btn_GBPAUD.clicked.connect(CAT_Btn_GBPAUD)
catal.Btn_GBPCAD.clicked.connect(CAT_Btn_GBPCAD)
catal.Btn_GBPCHF.clicked.connect(CAT_Btn_GBPCHF)
catal.Btn_GBPJPY.clicked.connect(CAT_Btn_GBPJPY)
catal.Btn_GBPNZD.clicked.connect(CAT_Btn_GBPNZD)
catal.Btn_GBPUSD.clicked.connect(CAT_Btn_GBPUSD)
catal.Btn_NZDUSD.clicked.connect(CAT_Btn_NZDUSD)
catal.Btn_USDCAD.clicked.connect(CAT_Btn_USDCAD)
catal.Btn_USDCHF.clicked.connect(CAT_Btn_USDCHF)
catal.Btn_USDJPY.clicked.connect(CAT_Btn_USDJPY)
catal.Btn_USDNOK.clicked.connect(CAT_Btn_USDNOK)
# OTC =========================================================
catal.Btn_AUDCAD_OTC.clicked.connect(CAT_Btn_AUDCAD_OTC)
catal.Btn_EURGBP_OTC.clicked.connect(CAT_Btn_EURGBP_OTC)
catal.Btn_EURJPY_OTC.clicked.connect(CAT_Btn_EURJPY_OTC)
catal.Btn_EURUSD_OTC.clicked.connect(CAT_Btn_EURUSD_OTC)
catal.Btn_GBPJPY_OTC.clicked.connect(CAT_Btn_GBPJPY_OTC)
catal.Btn_GBPUSD_OTC.clicked.connect(CAT_Btn_GBPUSD_OTC)
catal.Btn_NZDUSD_OTC.clicked.connect(CAT_Btn_NZDUSD_OTC)
catal.Btn_USDCHF_OTC.clicked.connect(CAT_Btn_USDCHF_OTC)
catal.Btn_USDJPY_OTC.clicked.connect(CAT_Btn_USDJPY_OTC)



#catal.CBox_M_Normal.stateChanged.connect(SET_M_NORMAL)
#catal.CBox_M_OTC.stateChanged.connect(SET_M_OTC)

catal.CBox_M_Normal.clicked.connect(SET_M_NORMAL)
catal.CBox_M_OTC.clicked.connect(SET_M_OTC)

catal.show()
app.exec()

#sys.exit(app.exec())



	
# IDEIA PARA CATALOGAÇÃO >>>>>  CATALOGAR M5 E M15 E VERIFICAR SE EM M15 TAMBEM ESTA NA MESMA DIREÇÃO (CALL OU PUT)
# IDEIA PARA CATALOGAÇÃO >>>>>  CATALOGAR E DIZER MELHOR ESTRATEGIA: SE MHI1, MHI2, MOONWALK, MILHAO