'''
Se importa la librería grpc y los archivos que contienen
las clases de protocolos de comunicación
'''
import grpc
from random import randint
import time

import protocoloAtt_pb2
import protocoloAtt_pb2_grpc

'''
Clase avion
'''
class Avion:
    '''
    atributos de la clase
    '''
    aerolinea = ''
    n_avion = ''
    pesoMaximo = 0
    tanque = 0
    TC_inicial = '' #se conoce al instanciar
    destino = ''
    TC_destino = '' #se pregunta a la torre de control
    origen = ''
    altura = 0
    '''
    métodos de la clase
    '''
    def combustible(self, tanque):
        n = int(1.5*int(tanque))
        n2 = int(0.9*int(tanque))
        carga_actual = randint(n2, n)
        return carga_actual

    def pasajerosActual(self, pesoMaximo):
        pasajerosMaximo = int(pesoMaximo)/80
        n1 = int(pasajerosMaximo/2)
        n2 = int(pasajerosMaximo + pasajerosMaximo/2)
        pasajeros = randint(n1,n2)
        return pasajeros


''' Funciones '''

'''
    Funcion instanciaAvion:
    Que instancia un avión de acuerdo a lo pedido, al instanciar
    se completan los datos iniciales para proceder a la comunicacion con las torres de control
'''
def instanciaAvion(avion):
    print("Bienvenido al Vuelo\n[Avion] Nombre de la Aerolínea y número de Avión:\n")
    aerolinea, nAvion = input().split(' ')
    avion.aerolinea = aerolinea
    avion.n_avion = nAvion
    print("[Avion - "+nAvion+"]: Peso Maximo de carga [Kg]:\n")
    pesoMaximo = input()
    avion.pesoMaximo = pesoMaximo
    print("[Avion - "+nAvion+"]: Capacidad del tanque de combustibe [L]:\n")
    combustible = input()
    avion.tanque = combustible
    print("[Avion - "+nAvion+"]: Torre de control inicial:\n")
    TCinicial = input ()
    avion.TC_inicial = TCinicial

''' Funciones para despegar'''
'''
    Funcion ConsultarCola:
    Se realiza una consulta a la torre de control para verificar la posicion de la cola
    si la cabeza de la cola coincide con el numero de avion, entonces se despega,
    en caso contrario, se espera unos segundos para volver a verificar.
'''
def ConsultarCola(avion, stub, instrucciones):
    avionPrev = instrucciones.avionPrevio
    pista = instrucciones.pista
    altura = instrucciones.altura
    print("[Avion - "+avion.n_avion+"] Todas las pistas están ocupadas, el avión predecedor es "+avionPrev+"...")
    pista = protocoloAtt_pb2.ColaRequest(pista = pista)
    cabezaCola = stub.VerificarCola(pista)
    if (cabezaCola.cabezaCola == avion.n_avion):
        print("[Avion - "+avion.n_avion+"] Pista ",instrucciones.pista," asignada y altura de ",altura," km.")
        #time.sleep(10)     #Descomentar para dar delay al despegue y poder probar las colas
        despegue = protocoloAtt_pb2.DespegueRequest(vuelo = avion.n_avion, pista = instrucciones.pista)
        stub.AvisarDespegue(despegue)
        print("[Avion - "+avion.n_avion+"] Despegando...")
    else:
        print("[Avion - "+avion.n_avion+"] verificando cola de espera...")
        time.sleep(1)
        ConsultarCola(avion, stub, instrucciones)

'''
    Funcion instrucciones:
    Cuando se cumplen las restricciones de pasajeros y combustible, se piden instrucciones para despegar
    a la torre de control a traves de los protocolos de comunicacion declarasdos. Si todas las pistas estan pistasOcupadas
    el avión queda en cola de espera y pide instrucciones hasta que llega su turno de despegar.
'''
def instrucciones(avion, stub):
    print("[Avion - "+avion.n_avion+"] Pidiendo instrucciones para despegar ...")
    newInstrucciones = protocoloAtt_pb2.InstruccionesRequest(vuelo = avion.n_avion)
    instrucciones = stub.PedirInstrucciones(newInstrucciones)
    ocupado = instrucciones.pistasOcupadas
    pista = instrucciones.pista
    altura = instrucciones.altura
    time.sleep(5)
    if (ocupado == 1):
         ConsultarCola(avion, stub, instrucciones)
    else:
        print("[Avion - "+avion.n_avion+"] Pista ",pista," asignada y altura de ",altura," km.")
        #time.sleep(10)     #Descomentar para dar delay al despegue y poder probar las colas
        despegue = protocoloAtt_pb2.DespegueRequest(vuelo = avion.n_avion, pista = instrucciones.pista)
        stub.AvisarDespegue(despegue)
        print("[Avion - "+avion.n_avion+"] Despegando...")

'''
    Funcion pasajeroYtanque:
    Se comprueban las condiciones de peso maximo y combustible enviando los datos a la
    torre de control, si la torre autoriza el despegue se piden instrucciones, en caso contrario
    se vuelve a calcular los datos de pasajeros/peso y combustible.
'''
def pasajeroYtanque(avion, stub):
    pesoMax = avion.pesoMaximo
    pesoActual = 80 * int(avion.pasajerosActual(pesoMax))
    tanque = avion.tanque
    tanqueActual = avion.combustible(tanque)
    #print(avion.pesoActual(pesoMax))
    #pesoActual = randint(pesoMaximo/2,pesoMaximo + pesoMaximo/2)
    print("[Avion - "+avion.n_avion+"] Todos los pasajeros a bordo y combustible cargado.")
    new_permiso = protocoloAtt_pb2.PermisoRequest(vuelo = avion.n_avion, pasajeros = pesoActual, combustible = tanqueActual)
    permiso = stub.PedirPermiso(new_permiso)
    if (permiso.permiso == True):
        instrucciones(avion, stub)
    else:
        pasajeroYtanque(avion, stub)

'''
    Funcion despegar:
    Se solicita permiso para despegar, para esto se indica a la torre de control el destino,
    luego se pasa por el gate y tras esto se comprueba que la cantidad de pasajeros(peso) y el combustible
    cumplan las condiciones necesarias de despegue.
'''
def despegar(avion, stub):
    print("[Avion - "+avion.n_avion+"] Presione enter para despegar")
    input()
    print("[Avion - "+avion.n_avion+"] Ingrese destino:")
    destino = input()
    avion.destino = destino
    new_avion = protocoloAtt_pb2.NuevoAvionRequest(vuelo = avion.n_avion, linea = avion.aerolinea, destino = avion.destino, peso = int(avion.pesoMaximo), combustible = int(avion.tanque))
    direccion = stub.ConsultarDestino(new_avion)
    if(direccion.direccion != 'No existe'):
        avion.TC_destino = direccion.direccion
        avion.origen = direccion.origen
        print("[Avion - "+avion.n_avion+"] Pasando por el Gate...")
        pasajeroYtanque(avion, stub)
    else:
        despegar(avion, stub)
'''
    Funcion ConsultarColaAt:
    Se realiza una consulta a la torre de control para verificar la posicion de la cola
    si la cabeza de la cola coincide con el numero de avion, entonces se aterriza,
    en caso contrario, se espera unos segundos para volver a verificar.
'''
def ConsultarColaAt(avion, stub, instrucciones):
    avionPrev = instrucciones.avionPrevio
    pista = instrucciones.pista
    altura = instrucciones.altura
    print("[Avion - "+avion.n_avion+"] Todas las pistas están ocupadas, el avión predecedor es "+avionPrev+" altura ",altura," km.")
    pista = protocoloAtt_pb2.At_ColaRequest(pista = pista)
    cabezaCola = stub.VerificarCola_At(pista)
    if (cabezaCola.cabezaCola == avion.n_avion):
        time.sleep(10)     #Descomentar para dar delay al despegue y poder probar las colas
        aterrizaje = protocoloAtt_pb2.AterrizarRequest(vuelo = avion.n_avion, pista = instrucciones.pista)
        stub.AvisarAterrizaje(aterrizaje)
        print("[Avion - "+avion.n_avion+"] Aterrizando en la pista ",instrucciones.pista)
    else:
        print("[Avion - "+avion.n_avion+"] verificando cola de espera...")
        time.sleep(2)
        ConsultarColaAt(avion, stub, instrucciones)

'''
    Funcion Aterizar:
    Se solicita permiso para Aterrizar, para esto se conecta se verifica si las pistas
    de la torre de destino estan disponibles para el aterrizaje.
'''
def Aterizar(avion, stub):
    newAterrizaje = protocoloAtt_pb2.AterrizajeRequest(vuelo = avion.n_avion , linea = avion.aerolinea, origen = avion.origen )
    print("[Avion - "+avion.n_avion+"] Esperando pista de aterrizaje...")
    time.sleep(1)
    att = stub.Atterizar(newAterrizaje)
    if (att.pistasOcupadas == 1):
        ConsultarColaAt(avion, stub, att)
    else:
        time.sleep(10)     #Descomentar para dar delay al despegue y poder probar las colas
        aterrizaje = protocoloAtt_pb2.AterrizarRequest(vuelo = avion.n_avion, pista = att.pista)
        stub.AvisarAterrizaje(aterrizaje)
        print("[Avion - "+avion.n_avion+"] Aterrizando en la pista ",att.pista)

'''
    Funcion run:
    funcion para iniciar la comunicación con la torre de control, es necesario ingresar la IP
    con la que se iniciará la comunicacion, luego se instancia un avión y se crea el stub de comunicacion,
    para proceder a despegar o aterrizar siguiendo las instrucciones de la torre de control en comunicacion.
'''
def run():
    avion = Avion()
    instanciaAvion(avion)
    with grpc.insecure_channel(avion.TC_inicial+':7777') as channel: 
        stub = protocoloAtt_pb2_grpc.ServicioStub(channel)
        despegar(avion, stub)
        time.sleep(5) #tiempo de espera para aterrizar
    with grpc.insecure_channel(avion.TC_destino+':7777') as channel:
        stub = protocoloAtt_pb2_grpc.ServicioStub(channel)
        Aterizar(avion, stub)

'''MAIN'''
if __name__ == '__main__':
    run()
