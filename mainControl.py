from time import sleep
from libraries import mcp3008
from controlmypi import ControlMyPi
import logging
import datetime
import pickle
from genericpath import exists
import smtplib


PICKLE_FILE = '/home/pi/py/moisture/moist.pkl'

def on_msg(conn, key, value):
    pass

def append_chart_point(chart, point):
    if len(chart) >= 48:
        del chart[0]
    chart.append(point)
    return chart

#Salva el dato recogido al archivo definido en PICKLE_FILE
def save(data):
    output = open(PICKLE_FILE, 'wb')
    pickle.dump(data, output)
    output.close()

#Salva el dato recogido al archivo definido en PICKLE_FILE
def load(default):
    if not exists(PICKLE_FILE):
        return default
    pkl_file = open(PICKLE_FILE, 'rb')
    data = pickle.load(pkl_file)
    pkl_file.close()
    return data

#Mandar un mail con el dato a traves del servidor de correo de GMAIL.
def send_gmail(from_name, sender, password, recipient, subject, body):
    senddate=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    msg="Date: %s\r\nFrom: %s <%s>\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (senddate, from_name, sender, recipient, subject)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipient, msg+body)
    server.quit()

logging.basicConfig(level=logging.INFO)

# VARIABLES QUE SON VALORES DE CONFIGURACION Y DESARROLLO
debugMode = True #Para imprimir movidas y ver que pasa por el terminal
idMail = 'jardineando.medialab@gmail.com'
passMail = 'visualizar'
updateControlMyPi = True
updateEmailSender = False

p = [ 
    [ ['G','moist','level',0,0,100], ['LC','chart1','Time','Value',0,100] ], 
    ]

c1 = load([])

readings = []



if updateControlMyPi:
	conn = ControlMyPi(idMail, passMail, 'moisbanc', 'Sensor de Humedad Bancal', p, on_msg)

delta = datetime.timedelta(minutes=120)
next_time = datetime.datetime.now()

delta_email = datetime.timedelta(days=1)
next_email_time = datetime.datetime.now()

if conn.start_control():
    try:
        while True:
            dt = datetime.datetime.now()
            m = mcp3008.read_pct(3)
            readings.append(m)
            to_update = {'moist':m}
            if(debugMode):
            	print "DateTime: " + dt.strftime("%B %d, %Y") + "; Valor leido: " + str(m); 

            

            # Update the chart?
            if updateControlMyPi:
	            if dt > next_time:
	                # Take the average from the readings list to smooth the graph a little
	                avg = int(round(sum(readings)/len(readings)))             
	                readings = []   
	                c1 = append_chart_point(c1, [dt.strftime('%H:%M'), avg])
	                save(c1)
	                next_time = dt + delta
	                to_update['chart1'] = c1
	            conn.update_status(to_update)
	            if(debugMode):
            		print "Control My Pi has been correctly updated" 
            
            #Send an email?
            if updateEmailSender:
	            if dt > next_email_time:
	                next_email_time = dt + delta_email
	                if m < 40:
	                    send_gmail('Jardineando', 'jardineando.medialab@gmail.com', 'visualizar', 'jardineando.medialab@gmail.com', 'Nivel de Humedad Bancal', 'El nivel es: %s' % m)
            
            sleep(30)
    finally:
    	if updateControlMyPi:
        	conn.stop_control()
