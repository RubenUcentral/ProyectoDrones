# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 23:44:17 2020

@author: Rubenz
"""

#Librerias
import sim
import time
import sys
import math
import threading
import speech_recognition as sr
import pandas as pd 
import numpy as np
from Speech import Speech

class Drone(object):
    
    def __init__(self):

        #Iniciar Variables
        self.distancia_pasoX=0
        self.distancia_pasoY=0
        self.distancia_paso=0
        
        self.cantidad_pasos=10
        self.largo_paso=1/self.cantidad_pasos
        self.tiempo_muerto=1/self.cantidad_pasos
        
        self.pasos=15
        self.tiempo_muerto_angulos=1/self.pasos
        self.angulo_paso=(math.pi/2)/self.pasos
        
        
        #           [X,Y,Direccion]
        self.estado=[0,0,0]
        self.estadoAnterior=[0,0,0]
        self.sensorAdelanteTarget=0
        self.sensorAdelante=0
        self.sensorAtrasTarget=0
        self.sensorAtras=0
        self.sensorDerechaTarget=0
        self.sensorDerecha=0
        self.sensorIzquierdaTarget=0
        self.sensorIzquierda=0
        
        self.puede=True
        self.SpeechTranslator = Speech()
        #Conexión con v-rep
        
        sim.simxFinish(-1) # just in case, close all opened connections
        self.clientID=sim.simxStart('127.0.0.1',19997,True,True,5000,5) # Connect to V-REP
        
        if self.clientID!=-1:
            print ('Connected to remote API server')
        else:
            #print ('Failed Conection')
            sys.exit("Conexion Fallida")

        self.target=0
        self.errorCode=0
        #Obtener Posición Inicial del UAV
        #[x,y,z]
        self.posiciones=0
        self.indice=0

        
        #Obtener Orientación del UAV
        self.orientacion=0
        self.punto_cardinal=0

        self.reset()
        

#Girar Drone
    
    def girarDerecha(self):
    
        self.distancia_pasoX=0
        self.distancia_pasoY=0
        self.distancia_paso=0
        x=0
        while x<self.pasos:
            
            self.orientacion[2]=self.orientacion[2]-self.angulo_paso
            sim.simxSetObjectOrientation(self.clientID,self.target,-1,self.orientacion,sim.simx_opmode_oneshot)
            x=x+1
            time.sleep(self.tiempo_muerto_angulos)  
        #print("giro a la derecha")
        time.sleep(0.6)
    
    def girarIzquierda(self):

        self.distancia_pasoX=0
        self.distancia_pasoY=0
        self.distancia_paso=0
        x=0
        while x<self.pasos:
            
            self.orientacion[2]=self.orientacion[2]+self.angulo_paso
            sim.simxSetObjectOrientation(self.clientID,self.target,-1,self.orientacion,sim.simx_opmode_oneshot)
            x=x+1
            time.sleep(self.tiempo_muerto_angulos)  
        #print("giro a la izquierda")
        time.sleep(0.6)
    
    def obtenerDireccion(self):
        # #print(self.orientacion[2])
        
        self.orientacion=sim.simxGetObjectGroupData(self.clientID,0,6,sim.simx_opmode_blocking )
        self.orientacion=self.orientacion[3]
        self.orientacion=self.orientacion[(self.indice*3):(self.indice*3+3)]
        #print(self.orientacion[2])
        
        if(self.orientacion[2]<0.3 and self.orientacion[2]>(-0.3)):        
            return 0      
        elif(self.orientacion[2]>(1.45) and self.orientacion[2]<(1.65)):
            return 3      
        elif(self.orientacion[2]<(-1.45) and self.orientacion[2]>(-1.65)):     
            return 2       
        else:
            return 1
    #mover()
    
    
    # 0=Stop; 1=Up; 2=Turn Right; 3=Turn Left; 4=Down; 5=Right; 6:Left; 7=Go Forward; 8=Go Back
    def direccionar(self,operacion):

        self.distancia_pasoX=0
        self.distancia_pasoY=0
        self.distancia_paso=0
        #Parar
        if operacion==0:
            self.distancia_pasoX=0
            self.distancia_pasoY=0
            self.distancia_paso=0
        #Sube
        elif operacion==1:
            self.distancia_pasoX=0
            self.distancia_pasoY=0
            self.distancia_paso=1
        #G. Derecha
        elif operacion==2:
            self.girarDerecha()
        #G. Izquierda
        elif operacion==3:
            self.girarIzquierda()
        #Bajar
        elif operacion==4:
            self.distancia_pasoX=0
            self.distancia_pasoY=0
            self.distancia_paso=-1        
        else:
            if self.punto_cardinal==0:
                #Derecha
                if operacion==5:
                    self.distancia_pasoX=0
                    self.distancia_pasoY=-1
                #Izquierda
                elif operacion==6:
                    self.distancia_pasoX=0
                    self.distancia_pasoY=1
                #Avanza
                elif operacion==7:
                    self.distancia_pasoX=1
                    self.distancia_pasoY=0
                #Retrocede
                elif operacion==8:
                    self.distancia_pasoX=-1
                    self.distancia_pasoY=0
                    
            elif self.punto_cardinal==1:
                #Derecha
                if operacion==5:
                    self.distancia_pasoX=0
                    self.distancia_pasoY=1
                #Izquierda
                elif operacion==6:
                    self.distancia_pasoX=0
                    self.distancia_pasoY=-1
                #Avanza
                elif operacion==7:
                    self.distancia_pasoX=-1
                    self.distancia_pasoY=0
                #Retrocede
                elif operacion==8:
                    self.distancia_pasoX=1
                    self.distancia_pasoY=0
            
            elif self.punto_cardinal==2:
                #Derecha
                if operacion==5:
                    self.distancia_pasoX=-1
                    self.distancia_pasoY=0
                #Izquierda
                elif operacion==6:
                    self.distancia_pasoX=1
                    self.distancia_pasoY=0
                #Avanza
                elif operacion==7:
                    self.distancia_pasoX=0
                    self.distancia_pasoY=-1
                #Retrocede
                elif operacion==8:
                    self.distancia_pasoX=0
                    self.distancia_pasoY=1
                
            elif self.punto_cardinal==3:
                #Derecha
                if operacion==5:
                    self.distancia_pasoX=1
                    self.distancia_pasoY=0
                #Izquierda
                elif operacion==6:
                    self.distancia_pasoX=-1
                    self.distancia_pasoY=0
                #Avanza
                elif operacion==7:
                    self.distancia_pasoX=0
                    self.distancia_pasoY=1
                #Retrocede
                elif operacion==8:
                    self.distancia_pasoX=0
                    self.distancia_pasoY=-1
                
            else:
                print("Dirección no encontrada.")
        
    
        
    #---------------------------------------------------------------------------------------------        
        
    def action(self,op,rewardProbability = 0):
        # #print(op)
        if (self.puedeMover(op)):
            self.direccionar(op)
            self.mover()
        #print("Salió")
        self.state()
        rew=0
        
        if(rewardProbability>0):
            if(np.random.rand() >= rewardProbability):
                rew=self.reward()
            else:
                rew=self.rewardShaping()
        else:
            rew=self.reward()
            
        if(self.estado[1]==10):
            return self.estado,rew,True
        
        return self.estado,rew,False

    #Movimiento en Eje x,y,z if posiciones[2]>=0.5:
    
    def mover(self):
        
        contador=0
        while contador < self.cantidad_pasos:
            self.posiciones[0]=self.posiciones[0]+self.distancia_pasoX*(self.largo_paso)
            self.posiciones[1]=self.posiciones[1]+self.distancia_pasoY*(self.largo_paso)
            if self.posiciones[2]<=0.5 and self.distancia_paso==-1:
                contador=contador
            elif self.posiciones[2]>=2.0 and self.distancia_paso==1:
                contador=contador
            else:
                self.posiciones[2]=self.posiciones[2]+self.distancia_paso*(self.largo_paso)
            sim.simxSetObjectPosition(self.clientID,self.target,-1,self.posiciones,sim.simx_opmode_oneshot)
            time.sleep(self.tiempo_muerto)
            contador=contador+1
    
    
        
    def puedeMover(self,op):
        self.estadoAnterior=self.estado
        #self.state()
        self.puede=True
        if(op==5 and self.sensorDerecha):
            self.puede=False
        elif(op==6 and self.sensorIzquierda):
            self.puede=False
        elif(op==7 and self.sensorAdelante):
            self.puede=False
        elif(op==8 and self.sensorAtras):
            self.puede=False
            
        return self.puede
        
    def state(self):
        self.sensores()
        self.posicion()
        self.punto_cardinal=self.obtenerDireccion()
        
        #           [X,Y,Direccion]
        self.estado=[(int)(self.posiciones[0]),(int)(self.posiciones[1]),self.punto_cardinal]
               
    def posicion(self):
        #Obtener Posición Inicial del UAV
        #[x,y,z]
        self.posiciones=sim.simxGetObjectGroupData(self.clientID,0,3,sim.simx_opmode_blocking )
        self.indice=self.posiciones[1]
        self.indice=self.indice.index(self.target)
        self.posiciones=self.posiciones[3]
        self.posiciones=self.posiciones[(self.indice*3):(self.indice*3+3)]
        
        
    def sensores(self):    
        
        #SensorAtras
        errorCode,self.sensorAtrasTarget=sim.simxGetObjectHandle(self.clientID,'Proximity_sensor',sim.simx_opmode_blocking)
        self.sensorAtras=sim.simxReadProximitySensor(self.clientID,self.sensorAtrasTarget,sim.simx_opmode_streaming )
        self.sensorAtras=sim.simxReadProximitySensor(self.clientID,self.sensorAtrasTarget,sim.simx_opmode_buffer)
        self.sensorAtras=self.sensorAtras[1]

        #SensorAdelante
        errorCode,self.sensorAdelanteTarget=sim.simxGetObjectHandle(self.clientID,'Proximity_sensor2',sim.simx_opmode_blocking)
        self.sensorAdelante=sim.simxReadProximitySensor(self.clientID,self.sensorAdelanteTarget,sim.simx_opmode_streaming )
        self.sensorAdelante=sim.simxReadProximitySensor(self.clientID,self.sensorAdelanteTarget,sim.simx_opmode_buffer)
        self.sensorAdelante=self.sensorAdelante[1]
        
        #SensorIzquierda
        errorCode,self.sensorIzquierdaTarget=sim.simxGetObjectHandle(self.clientID,'Proximity_sensor0',sim.simx_opmode_blocking)
        self.sensorIzquierda=sim.simxReadProximitySensor(self.clientID,self.sensorIzquierdaTarget,sim.simx_opmode_streaming )
        self.sensorIzquierda=sim.simxReadProximitySensor(self.clientID,self.sensorIzquierdaTarget,sim.simx_opmode_buffer)
        self.sensorIzquierda=self.sensorIzquierda[1]

        #SensorDerecha
        errorCode,self.sensorDerechaTarget=sim.simxGetObjectHandle(self.clientID,'Proximity_sensor1',sim.simx_opmode_blocking)
        self.sensorDerecha=sim.simxReadProximitySensor(self.clientID,self.sensorDerechaTarget,sim.simx_opmode_streaming )
        self.sensorDerecha=sim.simxReadProximitySensor(self.clientID,self.sensorDerechaTarget,sim.simx_opmode_buffer)
        self.sensorDerecha=self.sensorDerecha[1]
        
    def reward(self):
        self.state()
        distanciaAnterior=math.sqrt((14-self.estadoAnterior[0])*(14-self.estadoAnterior[0])+(15-self.estadoAnterior[1])*(15-self.estadoAnterior[1]))
        distanciaActual=math.sqrt((14-self.estado[0])*(14-self.estado[0])+(15-self.estado[1])*(15-self.estado[1]))

        if(self.puede==False): #Cuando va a chocar con un objeto
            return -20
        elif(self.estado==self.estadoAnterior):#Cuando se aleja del objetivo final
            return -1
        elif(self.estado[1]>9):#Cuando llega al objetivo final
            return 10
        elif((distanciaAnterior-distanciaActual)>0):#Cuando se acerca al objetivo final
            return 1.5
        return -1 #Recompensa en caso de no caer en ningún bloque if
    
    
    def rewardShaping(self):
        self.state()
        distanciaAnterior=math.sqrt((14-self.estadoAnterior[0])*(14-self.estadoAnterior[0])+(15-self.estadoAnterior[1])*(15-self.estadoAnterior[1]))
        distanciaActual=math.sqrt((14-self.estado[0])*(14-self.estado[0])+(15-self.estado[1])*(15-self.estado[1]))

        if(self.puede==False):#Cuando va a chocar con un objeto
            return self.SpeechTranslator.Reward("So Bad")
        elif(self.estado==self.estadoAnterior)::#Cuando se aleja del objetivo final
            return self.SpeechTranslator.Reward("Bad")
        elif(self.estado[1]>9):#Cuando llega al objetivo final
            return self.SpeechTranslator.Reward("Perfect")
        elif((distanciaAnterior-distanciaActual)>0):#Cuando se acerca al objetivo final
            return self.SpeechTranslator.Reward("Not Bad")
        return self.SpeechTranslator.Reward("Bad") #Recompensa en caso de no caer en ningún bloque if
    
    def reset(self):
        # Restart the simulation
        stop=sim.simxStopSimulation(self.clientID, sim.simx_opmode_blocking)
        stop=sim.simxStopSimulation(self.clientID, sim.simx_opmode_blocking)
        start=sim.simxStartSimulation(self.clientID, sim.simx_opmode_blocking)
        start=sim.simxStartSimulation(self.clientID, sim.simx_opmode_blocking)


        self.errorCode,self.target=sim.simxGetObjectHandle(self.clientID,'Quadricopter_target',sim.simx_opmode_blocking)


        
        
        #Obtener Orientación del UAV
        self.orientacion=sim.simxGetObjectGroupData(self.clientID,0,6,sim.simx_opmode_blocking )
        self.orientacion=self.orientacion[3]
        self.orientacion=self.orientacion[(self.indice*3):(self.indice*3+3)]
        
        self.state()
        self.estadoAnterior=self.estado
        # return [(self.estado[0]/11),(self.estado[1]/11),(self.estado[2]/4)]
        return self.estado

        
