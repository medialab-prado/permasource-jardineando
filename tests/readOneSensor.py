from time import sleep
import mcp3008
while True:
	m= mcp3008.readadc(3)
	print "Valor instantaneo de temperatura: {:>5} ".format(m)
	sleep(.5)