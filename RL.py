import os
import numpy as np
from Drone import Drone
import matplotlib.pyplot as plt
import math
from Speech import Speech
import datetime

class Agente():
    def __init__(self, entorno, alpha = 0.1, epsilon = 0.1, gamma = 1):#0.99):
        self.entorno = entorno
        self.nEstados = [11, 11, 4]
        self.nAcciones = 9

        # policy params
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.Q = np.zeros([self.nEstados[0], self.nEstados[1], self.nEstados[2],self.nAcciones])
        self.MIN_ALPHA = 0.1
        self.MIN_EPSILON = 0.01
        self.calidad = 1 # calidad
        self.SpeechTranslator = Speech()
        # print(self.Q)
    # end __init__
    
    #policy Epsilon-Greedy
    def seleccionarAccion(self, estado):
        #exploracion
        if np.random.rand() <= self.epsilon: #aleatorio
            return np.random.randint(self.nAcciones)
        #explotacion
        else: # mejor valor Q
            return np.argmax(self.Q[estado[0],estado[1],estado[2], :])
    # end seleccionarAccion

    def seleccionarAccionFeedback(self, estado, entrenador, feedbackProbabilidad):
        if np.random.rand() <= feedbackProbabilidad: #consejo
            if np.random.rand() <= self.calidad: #buen consejo 
                return self.SpeechTranslator.Action(np.argmax(entrenador.Q[estado[0], estado[1],estado[2], :]))
            else:
                return self.SpeechTranslator.Action(np.argmin(entrenador.Q[estado[0], estado[1],estado[2], :]))
        else:#accion agente
            return self.seleccionarAccion(estado)
        
    def update_explore_rate(self, t):
        self.epsilon = max(self.MIN_EPSILON, min(self.epsilon, 1.0 - math.log10((t+1)/25)))
    # end update_explore_rate

    # td control
    def QLearning(self, estado, estado_sig, accion, reward):
        td_target = reward + self.gamma * np.max(self.Q[estado_sig[0], estado_sig[1], estado_sig[2],:])
        td_error = td_target - self.Q[estado[0], estado[1],estado[2], accion]
        self.Q[estado[0], estado[1], estado[2],accion] += self.alpha * td_error
        

    
    
    def entrenar(self, episodios, entrenador = None, feedbackProbabilidad = 0, rShapping=0):
        recompensas = []
        for e in range(episodios):
            estado= self.entorno.reset()
            recompensa = 0
            fin = False
            contador = 0
            while not fin:
                #accion = self.seleccionarAccion(estado)
                
                accion = self.seleccionarAccionFeedback(estado, entrenador, feedbackProbabilidad)
                #self.actos(accion)
                estado_sig, reward, fin = self.entorno.action(accion,rShapping)
                
                if(contador>=2000):
                    fin = True
                    reward = -200
                recompensa += reward                
                
                #fin = self.entorno.goalPos == estado

                if not fin:
                    #actualizar valor Q
                    self.QLearning(estado, estado_sig, accion, reward)
                estado = estado_sig
                contador = contador + 1

            print('Fin episodio {}, reward: {}'.format(e, recompensa))
            recompensas.append(recompensa)
            # self.update_explore_rate(e)

        return recompensas
    
    # end entrenar
    
    
    
entorno = Drone()

episodios = 20
cantidadAgentes = 20


rewardEntrenador = np.zeros(episodios)
rewardAprendizP = np.zeros(episodios)
rewardAprendizR = np.zeros(episodios)
rewardAprendizPR = np.zeros(episodios)

feedback = 0.15 #l intervencion

rShappingProbability = 0.15

#Autonomo
tiempoInicio=datetime.datetime.now()
for r in range(cantidadAgentes):
    print('Entrenando Agente entrenador: ',r)
    entrenador = Agente(entorno)
    rewardEntrenador += entrenador.entrenar(episodios)
    #print('Recompensa Entrenador',rewardEntrenador)
tiempoEntrenador=datetime.datetime.now()-tiempoInicio

#Policy-Shapping
tiempoInicio=datetime.datetime.now()
for r in range(cantidadAgentes):
    print('Entrenando Agente aprendiz P-S: ',r)
    aprendiz = Agente(entorno)
    rewardAprendizP += aprendiz.entrenar(episodios,entrenador, feedbackProbabilidad=feedback, rShapping=0)
    #print('Recompensa Aprendiz',rewardAprendizP)
tiempoPS=datetime.datetime.now()-tiempoInicio

#Reward-Sapping
tiempoInicio=datetime.datetime.now()
for r in range(cantidadAgentes):
    print('Entrenando Agente aprendiz R-S: ',r)
    aprendiz = Agente(entorno)
    rewardAprendizR += aprendiz.entrenar(episodios, entrenador = None, feedbackProbabilidad = 0, rShapping=rShappingProbability)
    #print('Recompensa Aprendiz',rewardAprendizR)
tiempoRS=datetime.datetime.now()-tiempoInicio

#Policy-Shapping and Reward-Sapping
tiempoInicio=datetime.datetime.now()
for r in range(cantidadAgentes):
    print('Entrenando Agente aprendiz P-S and R-S: ',r)
    aprendiz = Agente(entorno)
    rewardAprendizPR += aprendiz.entrenar(episodios,entrenador, feedbackProbabilidad=feedback, rShapping=rShappingProbability)
    #print('Recompensa Aprendiz',rewardAprendizPR)
tiempoPSRS=datetime.datetime.now()-tiempoInicio

rewardEntrenador /= cantidadAgentes
rewardAprendizP /= cantidadAgentes
rewardAprendizR /= cantidadAgentes
rewardAprendizPR /= cantidadAgentes

plt.plot(rewardEntrenador, label='Entrenador')
plt.plot(rewardAprendizP, label='Aprendiz P-S')
plt.plot(rewardAprendizR, label='Aprendiz R-S')
plt.plot(rewardAprendizPR, label='Aprendiz P-S y R-S')

plt.xlabel('Episodios')
plt.ylabel('Recompensa promedio')
#plt.ylim([-250, -5])
#plt.xlim([0,250])
plt.legend()
print(entrenador.Q)