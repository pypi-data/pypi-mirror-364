import numpy as np


def saludar ():
    print("Hola, te saludo desde saludos.saludar()")
    

def prueba():
    print("esto es una PRUEBA de la nueva versión")
    
def generar_array(numeros): #esto llamara a numpy para generar un array dependiendo de unos numeros y lo generara dinamicamente dependiendo los numeros 
    return np.arange(numeros) 



class Saludo:
    def __init__ (self):
        print("Hola, te saludo desde Saludos.__init__()")
        
if __name__ == '__name__':
    print(generar_array(5))