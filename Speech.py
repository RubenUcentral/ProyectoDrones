# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 23:16:57 2020

@author: Rubenz
"""
import speech_recognition as sr
import pandas as pd 
import numpy as np
import threading
import time
from Levenshtein import distance as levenshtein_distance
import os
from random import randint

class Speech(object):
    
    def __init__(self):
        self.actions = pd.read_csv("instrucciones.csv") 
        self.rewards = pd.read_csv("reward.csv",encoding='latin-1') 
        self.palabra=""
        self.instruccion=-100
        self.directory='C:/Users/Rubenz/Desktop/Tesis/Tesis/Grabaciones/'
        self.reward_directory=self.directory+'Rewards/'
        self.action_directory=self.directory+'Actions/'


    def Reward(self,index):
        directorio = self.reward_directory+str(index)+'/'
        
        arr = os.listdir(directorio)
        
        # print(directorio+arr[randint(0, (len(arr)-1))])
        
        spanish,english=self.SpeechRecognition(directorio+arr[randint(0, (len(arr)-1))])
        return self.DistanceReward(spanish,english)
        
        
    def Action(self,index):
        
        directorio = self.action_directory+str(index)+'/'
        
        arr = os.listdir(directorio)
        # print(arr)
        
        # print(directorio+arr[randint(0, (len(arr)-1))])
        
        spanish,english=self.SpeechRecognition(directorio+arr[randint(0, (len(arr)-1))])
        return self.DistanceAction(spanish,english)
        
        
        
    def DistanceReward(self,text1,text2):
        # print(self.rewards)
        
        min_distance_spanish=1000000;
        action_spanish=1
        min_distance_english=1000000;
        action_english=1
        for i in range(0, len(self.rewards)):
            #Spanish
            l_d=levenshtein_distance(self.rewards['Instruccion'][i],text1)
            
            if(min_distance_spanish>l_d):
                min_distance_spanish=l_d
                action_spanish=self.rewards['Numero'][i]
                
            #English
            l_d=levenshtein_distance(self.rewards['Instruccion'][i],text2)
            
            if(min_distance_english>l_d):
                min_distance_english=l_d
                action_english=self.rewards['Numero'][i]
                
                
        # print(min_distance_spanish)
        # print(action_spanish)
        # print(min_distance_english)
        # print(action_english)
        
        if(min_distance_spanish<min_distance_english):
            print("Recompensa sugerida: ", action_spanish)
            return action_spanish
        print("Recompensa sugerida: ", action_spanish)
        return action_english
        
        
        
    def DistanceAction(self,text1,text2):
        
        # print(self.actions)
        
        min_distance_spanish=1000000;
        action_spanish=9
        min_distance_english=1000000;
        action_english=9
        for i in range(0, len(self.actions)):
            #Spanish
            l_d=levenshtein_distance(self.actions['Instruccion'][i],text1)
            
            if(min_distance_spanish>l_d):
                min_distance_spanish=l_d
                action_spanish=self.actions['Numero'][i]
                
            #English
            l_d=levenshtein_distance(self.actions['Instruccion'][i],text2)
            
            if(min_distance_english>l_d):
                min_distance_english=l_d
                action_english=self.actions['Numero'][i]
                
                
        # print(min_distance_spanish)
        # print(action_spanish)
        # print(min_distance_english)
        # print(action_english)
        
        if(min_distance_spanish<min_distance_english):
            print("Acción sugerida: ", action_spanish)
            return action_spanish
        print("Acción sugerida: ", action_english)
        return action_english
        
    def SpeechRecognition(self,wav):
        spanish=""
        r=sr.Recognizer()
        
        try:
            with sr.AudioFile(wav) as source:
                audio = r.record(source)

        except:
            print("Palabra español desconocida")
            
        try:    
            spanish=r.recognize_google(audio, language="es-MX")
        except:
            print("Palabra español desconocida")
            
        english = "" 
        e=sr.Recognizer()
        
        try:
            with sr.AudioFile(wav) as source:
                audio = e.record(source)
                            
        except:
            print("Palabra inglés desconocida")
            
        try:    
            english=r.recognize_google(audio)
        except:
            print("Palabra inglés desconocida")
            
        # print(spanish)
        # print(english)
            
        return spanish,english
        
    
    
# recognizer = Speech()

# #prueba = recognizer.SpeechRecognition(wav='C:/Users/Rubenz/Desktop/Tesis/Instrucciones/1/1.WAV')

# print("Acción sugerida: ", 3)

# # j= recognizer.DistanceAction("right","rig")
# # j= recognizer.DistanceReward("m mal", "m")
# # j = recognizer.Action(8)
# # print(j)

# j = recognizer.Reward("Bad")
# print(j)

# j = recognizer.Reward("So Bad")
# print(j)

# j = recognizer.Reward("Not Bad")
# print(j)

# j = recognizer.Reward("Perfect")
# print(j)