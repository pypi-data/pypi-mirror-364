#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 23:07:52 2025

@author: md.waheduzzamanbasunianouman
"""

from scipy.optimize import fsolve,brentq
import matplotlib.pyplot as plt
import numpy as np
import warnings
import CoolProp.CoolProp as CP
import pandas as pd
import json
from CoolProp.CoolProp import PropsSI

from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.soo.nonconvex.de import DE
from pymoo.optimize import minimize


class ThermodynamicModel():
    
    def __init__(self):
        self.Point = {}
        self.Component = {}
        self.Connection = []
        self.Loops = {}
    
    def add_point(self,fluid, StatePointName,Mass_flowrate = None, **properties):
        Node = self.Prop(fluid = fluid, StatePointName = StatePointName,Mass_flowrate = Mass_flowrate, pro = properties)
        self.Point[Node.StatePointName] = Node

    def add_Connection(self,Comp_1,Comp_1_id, Comp_2,Comp_2_id,fluid, StatePointName,Mass_flowrate = None, **properties):
        Node = self.Prop(fluid = fluid, StatePointName = StatePointName,Mass_flowrate = Mass_flowrate, pro = properties)
        self.Point[Node.StatePointName] = Node
        self.Connection.append([Comp_1.ID,Comp_1_id, Comp_2.ID,Comp_2_id
                                ,StatePointName])
       
        self.Component[Comp_1.ID] = Comp_1
        self.Component[Comp_2.ID] = Comp_2
    
    def add_loop(self,loop_ID:str,loop,Mass_flowrate = None) -> None:
        loop.append(Mass_flowrate)
        self.Loops[loop_ID] = loop
        
    def _Create_Loop(self):
        _loop = []
        for key, value in self.Loops.items(): 
            lp = []
            for ID in value[:-1]:
                if ID[0] in self.Component:
                    if len(ID) == 2:
                        lp.append([self.Component[ID[0]],ID[1]])
                    else:
                        lp.append([self.Component[ID[0]]])
            
            lp.append(value[-1])
            _loop.append(lp)
        return _loop
    
    
    def solve(self):
        for _ in range(3):
            for key,value in self.Component.items():
                    try:
                        value.Cal()
                    except:
                        pass
                
    def Point_print(self):
        data_list = []
        for key,value in self.Point.items():
            data_list.append(vars(value))
        df = pd.DataFrame(data_list)
        df.drop(columns=['properties', 'Points','S','Cp','D'],inplace=True)
        df["T"] = df["T"] - 273.15
        df = df.iloc[:, [2,0,1,3,4,5,6]]
        df.columns = ['StatePoint','Fluid','Flowrate(kg/s)','Pressure(Pa)','Temperature(C)','Enthalpy(kj/kg)','Qaulity']
        print(df.to_string())
        return df
    
    def Component_print(self):
        
        for comp in self.Component:
            c = self.Component[comp].ID
            try:
                print( self.Component[comp],'\n')
            except:
                print(f"{c} is not solved\n")
        
    def __str__(self):
        self.Component_print()
        self.Point_print()
        return ' '
    
    class Source:
        
        def __init__(self,Model,ID,Out_state,Calculate = False):
            self.ID = ID
            self.Model = Model
            self.Out = Model.Point[Out_state]
            self.Out_state = Out_state
            self.Solution_Status = False
            self.energy_supply = None
            self.Model.Component[ID] = self
            if Calculate:
                self.Cal()
            
        def Cal(self):
            if self.Out.Mass_flowrate != None and self.Out.H != None:
                Mass_flowrate = self.Out.Mass_flowrate
                self.energy_supply = self.Out.H * Mass_flowrate
                self.Solution_Status = True
            else:
                raise ValueError(f'Mass flowrate of {self.ID} is not given')
            
            
        def __str__(self):
            return (
                f"{self.ID} Data:\n"
                f"Energy Supply: {self.energy_supply}\n"
                f"Solution status: {self.Solution_Status}"
                )
        
    class Sink:
        
        def __init__(self,Model,ID,In_state,Calculate = False):
            self.ID = ID
            self.Model = Model
            self.In = Model.Point[In_state]
            self.energy_supply = None
            self.In_state = In_state
            self.Solution_Status = False
            self.energy_supply = None
            self.Model.Component[ID] = self
            if Calculate:
                self.Cal()
            
        def Cal(self):
            if self.In.Mass_flowrate != None and self.In.H != None:
                Mass_flowrate = self.In.Mass_flowrate
                self.energy_supply = self.In.H * Mass_flowrate
                self.Solution_Status = True
            else:
                raise ValueError(f'Mass flowrate of {self.ID} is not given')
            
        def __str__(self):
            return (
                f"{self.ID} Data:\n"
                f"Energy Supply: {self.energy_supply}\n"
                f"Solution status: {self.Solution_Status}"
                )
            
    class Turbine:
        
        def __init__(self,Model,ID,In_state ,Out_state, n_isen = 1, n_mech = 1,work = 0,Calculate = False):
            self.n_isen = n_isen
            self.n_mech = n_mech
            self.work = work
            self.ID = ID
            self.In_state = In_state
            self.Out_state = Out_state
            self.Solution_Status = False
            self.Model = Model
            self.Model.Component[ID] = self
            if Calculate:
                self.Cal()
            
        def Cal(self):
            self.In = self.Model.Point[self.In_state]
            self.Out = self.Model.Point[self.Out_state]
            if (self.Out.Mass_flowrate == None and self.In.Mass_flowrate != None):
                Mass_flowrate = self.In.Mass_flowrate
                self.Out.Mass_flowrate = self.In.Mass_flowrate
                
            elif (self.Out.Mass_flowrate != None and self.In.Mass_flowrate == None):
                Mass_flowrate = self.Out.Mass_flowrate
                self.In.Mass_flowrate = self.Out.Mass_flowrate
            elif (self.Out.Mass_flowrate == self.In.Mass_flowrate):
                Mass_flowrate = self.Out.Mass_flowrate
            elif(self.Out.Mass_flowrate != self.In.Mass_flowrate):
                raise ValueError(f'Mass flowrate at inlet and outlet of {self.ID} is not equal')
            else:
                raise ValueError(f'Mass flowrate of {self.ID} is not given')
                
            if self.Out.H == None:
                h_isen = self.Model.Prop(self.In.fluid,P = self.Out.P,S = self.In.S,
                                               StatePointName = 'h_isen')
                h_out = self.In.H - (self.In.H - h_isen.H )*self.n_isen
                self.Out  = self.Model.Prop(self.In.fluid,P = self.Out.P,H = h_out,
                                                  StatePointName = self.Out.StatePointName,Mass_flowrate = Mass_flowrate)
                
            elif self.In.H == None:
                def inlet(h_in):
                    h_in = h_in[0]
                    _inlet  = self.Model.Prop(self.In.fluid,P = self.In.P,H = h_in,
                                                     StatePointName = self.In.StatePointName)
                    h_isen = self.Model.Prop(self.In.fluid,P = self.Out.P,S = _inlet.S,
                                                   StatePointName = 'h_isen')
                    return self.Out.H -  h_in + (h_in - h_isen.H)*self.n_isen
                h_in = fsolve(inlet,[self.Out.H] )
                self.In  = self.Model.Prop(self.In.fluid,P = self.In.P,H = h_in[0],
                                                 StatePointName = self.In.StatePointName,Mass_flowrate = Mass_flowrate)
                
            w =  self.In.H -self.Out.H
            self.work = w*Mass_flowrate*self.n_mech
            self.Solution_Status = True
            self.Model.Point[self.In_state] = self.In
            self.Model.Point[self.Out_state] = self.Out
            
        def __str__(self):
            return (
                f"{self.ID} Data:\n"
                f"Inlet Pressure: {self.In.P/1e5} Bar\n"
                f"Outlet Pressure : {self.Out.P/1e5:.2f} Bar\n"
                f"Isentropic Efficiency : {self.n_isen*100:.2f} %\n"
                f"Mechanical Efficincey: {self.n_mech*100:.2f} %\n"
                f"Work: {self.work:.2f} W\n"
                f"Solution status: {self.Solution_Status}"
                )  
    
    class Pump:
        def __init__(self,Model,ID,In_state ,Out_state ,n_isen = 1, n_mech = 1,work = 0,Compressibility = 'Compressible',Calculate = False):
            self.Model = Model
            self.n_isen = n_isen
            self.n_mech = n_mech
            self.work = work
            self.ID = ID
            self.In_state = In_state
            self.Out_state = Out_state
            self.Solution_Status = False
            self.Model.Component[ID] = self
            self.Compressibility = Compressibility
            if Calculate:
                self.Cal()
    
        def Cal(self):
            mass_flowrate_flag = False
            self.In = self.Model.Point[self.In_state]
            self.Out = self.Model.Point[self.Out_state]
            if (self.Out.Mass_flowrate == None and self.In.Mass_flowrate != None):
                Mass_flowrate = self.In.Mass_flowrate
                self.Out.Mass_flowrate = self.In.Mass_flowrate
            elif (self.Out.Mass_flowrate != None and self.In.Mass_flowrate == None):
                Mass_flowrate = self.Out.Mass_flowrate
                self.In.Mass_flowrate = self.Out.Mass_flowrate
            elif (self.Out.Mass_flowrate == self.In.Mass_flowrate):
                if self.Out.Mass_flowrate == None:
                    mass_flowrate_flag = True
                    Mass_flowrate = 1
                    warnings.warn(f'Mass flowate through {self.ID} set 1kg/s')
                else:
                    Mass_flowrate = self.Out.Mass_flowrate
            elif(self.Out.Mass_flowrate != self.In.Mass_flowrate):
                raise ValueError(f'Mass flowrate at inlet and outlet of {self.ID} is not equal')
            else:
                raise ValueError(f'Mass flowrate of {self.ID} is not given')
            
            if self.Compressibility == 'Compressible':
                if self.Out.H == None:
                    h_isen = self.Model.Prop(self.In.fluid,P = self.Out.P,S = self.In.S,
                                                   StatePointName = 'h_isen',Mass_flowrate = Mass_flowrate)
                    
                    h_out = self.In.H + (h_isen.H - self.In.H)/self.n_isen
                    self.Out  = self.Model.Prop(self.In.fluid,P = self.Out.P,H = h_out,
                                                      StatePointName = self.Out.StatePointName,Mass_flowrate = Mass_flowrate)
                    
                    
                elif self.In.H == None:
                    def inlet(h_in):
                        h_in = h_in[0]
                        inlet  = self.Model.Prop(self.In.fluid,P = self.In.P,H = h_in,
                                                         StatePointName = self.In.StatePointName)
                        h_isen = self.Model.Prop(self.In.fluid,P = self.Out.P,S = inlet.S,
                                                       StatePointName = 'h_isen')
                        return self.Out.H -  h_in - (h_isen.H - h_in)/self.n_isen
                    h_in = fsolve(inlet,[self.Out.H] )
                    self.In  = self.Model.Prop(self.In.fluid,P = self.In.P,H = h_in[0],
                                                     StatePointName = self.In.StatePointName,Mass_flowrate = Mass_flowrate)
                   
                w =  self.Out.H -self.In.H
            elif self.Compressibility == 'Incompressible':
                D = self.In.D
                w_out = (self.Out.P - self.In.P)/D
                w = w_out/self.n_isen
                self.Out.H = self.In.H + w
                self.Out.T = self.Model.Prop(self.In.fluid,P = self.Out.P,H = self.In.H + w,StatePointName = self.Out.StatePointName ).T
            else:
                raise ValueError("Valid input for Compressibility in {self.ID} are Compressible and Incompressible ")
            
            
            self.work = w*Mass_flowrate/self.n_mech
            self.Solution_Status = True
            if mass_flowrate_flag:
                self.In.Mass_flowrate = None
                self.Out.Mass_flowrate = None
            self.Model.Point[self.In_state] = self.In
            self.Model.Point[self.Out_state] = self.Out
        def __str__(self):
            return (
                f"{self.ID} Data:\n"
                f"Inlet Pressure: {self.In.P/1e5} Bar\n"
                f"Outlet Pressure : {self.Out.P/1e5:.2f} Bar\n"
                f"Isentropic Efficiency : {self.n_isen*100:.2f} %\n"
                f"Mechanical Efficincey: {self.n_mech*100:.2f} %\n"
                f"Work: {self.work:.2f} W\n"
                f"Solution status: {self.Solution_Status}"
            )         
        
    class Expansion_valve:
        
        def __init__(self,Model,ID,In_state ,Out_state,Calculate = False):
            self.Model = Model
            self.ID = ID
            self.In_state = In_state
            self.Out_state = Out_state
            self.Solution_Status = False
            self.Model.Component[ID] = self
            if Calculate:
                self.Cal()
        
        def Cal(self):
            self.In = self.Model.Point[self.In_state]
            self.Out = self.Model.Point[self.Out_state]
            if (self.Out.Mass_flowrate == None and self.In.Mass_flowrate != None):
                Mass_flowrate = self.In.Mass_flowrate
                self.Out.Mass_flowrate = self.In.Mass_flowrate
                
            elif (self.Out.Mass_flowrate != None and self.In.Mass_flowrate == None):
                Mass_flowrate = self.Out.Mass_flowrate
                self.In.Mass_flowrate = self.Out.Mass_flowrate
            elif (self.Out.Mass_flowrate == self.In.Mass_flowrate):
                Mass_flowrate = self.Out.Mass_flowrate
            elif(self.Out.Mass_flowrate != self.In.Mass_flowrate):
                raise ValueError(f'Mass flowrate at inlet and outlet of {self.ID} is not equal')
            else:
                raise ValueError(f'Mass flowrate of {self.ID} is not given')
                
            if self.In.H == None: 
                self.In = self.Model.Prop(self.In.fluid, StatePointName = self.In.StatePointName
                                    , P = self.In.P, H = self.Out.H)
            elif self.Out.H == None: 
                
                self.Out = self.Model.Prop(self.Out.fluid, StatePointName = self.Out.StatePointName
                                    , P = self.Out.P, H = self.In.H)
            self.Solution_Status = True
            self.Model.Point[self.In_state] = self.In
            self.Model.Point[self.Out_state] = self.Out
            
        def __str__(self):
            return (
                f"{self.ID} Data:\n"
                f"Inlet Pressure: {self.In.P/1e5} Bar\n"
                f"Outlet Pressure : {self.Out.P/1e5:.2f} Bar\n"
                f"Solution status: {self.Solution_Status}"
                )
        
    class Pipe:
        
        def __init__(self,Model,ID,In_state ,Out_state ,Pressure_drop = 0,Temperature_drop = 0,Calculate = False):
            self.Model = Model
            self.ID = ID
            self.In_state = In_state
            self.Out_state = Out_state
            self.Pressure_drop = Pressure_drop
            self.Temperature_drop = Temperature_drop
            self.Solution_Status = False
            self.Model.Component[ID] = self
            if Calculate:
                self.Cal()
            
        def Cal(self):
            self.In = self.Model.Point[self.In_state]
            self.Out = self.Model.Point[self.Out_state]
            if (self.Out.Mass_flowrate == None and self.In.Mass_flowrate != None):
                self.Out.Mass_flowrate = self.In.Mass_flowrate
                
            elif (self.Out.Mass_flowrate != None and self.In.Mass_flowrate == None):
                self.In.Mass_flowrate = self.Out.Mass_flowrate
                
            elif(self.Out.Mass_flowrate != self.In.Mass_flowrate):
                raise ValueError(f'Mass flowrate at inlet and outlet of {self.ID} is not equal')
            else:
                raise ValueError(f'Mass flowrate of {self.ID} is not given')
                
            if self.In.P == None:
                self.In.P = self.Out.P + self.Pressure_drop
                self.In.T = self.Out.T + self.Temperature_drop
            elif self.Out.P == None:
                self.Out.P = self.In.P - self.Pressure_drop
                self.Out.T = self.In.T - self.Temperature_drop
            else:
                self.Pressure_drop =  self.In.P - self.Out.P
                self.Temperature_drop = self.In.T - self.Out.T
            self.Solution_Status = True
            self.Model.Point[self.In_state] = self.In
            self.Model.Point[self.Out_state] = self.Out
        def __str__(self):
            return (
                f"{self.ID} Data:\n"
                f"Inlet Pressure: {self.In.P/1e5} Bar\n"
                f"Outlet Pressure : {self.Out.P/1e5:.2f} Bar\n"
                f'Pressure Drop : {self.Pressure_drop/1e5:.2f} Bar\n' 
                f'Temperature Drop : {self.Temperature_drop:.2f} K\n'
                f"Solution status: {self.Solution_Status}"
                )
        
    class PCM:
        
        def __init__(self,Model,ID,PPT,Charge,T_melt,Hot_In_state,Hot_Out_state,Cold_In_state,
                     Cold_Out_state,Charging_time ,Discharging_time,per_loss,Capacity = None,Calculate = False):
            self.ID = ID
            self.T_melt = T_melt
            self.Model = Model
            self.per_loss = per_loss
            self.Hot_In_state = Hot_In_state
            self.Hot_Out_state = Hot_Out_state
            self.Cold_In_state = Cold_In_state
            self.Cold_Out_state  = Cold_Out_state
            self.Charging_time = Charging_time
            self.Discharging_time = Discharging_time
            self.Charge = Charge
            self.Capacity = Capacity
            self.PPT = PPT
            self.Solution_Status = False
            self.Model.Component[ID] = self
            self.Charging_Power = None
            self.Discharging_Power = None
            if Calculate:
                self.Cal()
            
        def PCM_Prop(self,H = None,T = None):
            pass
            
        def Cal(self):
            self.Hot_In = self.Model.Point[self.Hot_In_state] if self.Hot_In_state != None else None
            self.Hot_Out = self.Model.Point[self.Hot_Out_state] if self.Hot_Out_state != None else None
            self.Cold_In = self.Model.Point[self.Cold_In_state] if self.Cold_In_state != None else None
            self.Cold_Out  = self.Model.Point[self.Cold_Out_state] if self.Cold_Out_state != None else None
            
            
            
            if self.Hot_Out != None or self.Hot_In != None:
                if (self.Hot_Out.Mass_flowrate == None and self.Hot_In.Mass_flowrate != None):    
                    self.Hot_Out.Mass_flowrate = self.Hot_In.Mass_flowrate
                    self.Hot_Mass_flowrate = self.Hot_In.Mass_flowrate
                
                elif (self.Hot_Out.Mass_flowrate != None and self.Hot_In.Mass_flowrate == None):    
                    self.Hot_In.Mass_flowrate = self.Hot_Out.Mass_flowrate
                    self.Hot_Mass_flowrate = self.Hot_Out.Mass_flowrate
                
                elif (self.Hot_Out.Mass_flowrate == self.Hot_In.Mass_flowrate):    
                    self.Hot_Mass_flowrate = self.Hot_In.Mass_flowrate
                    
                elif (self.Hot_Out.Mass_flowrate != self.Hot_In.Mass_flowrate):    
                    raise ValueError(f'Hot side fluid Mass flowrate of {self.ID}is not match ')
            else:
                self.Hot_Mass_flowrate = None
             
            if self.Cold_Out != None or self.Cold_In != None:    
                if (self.Cold_Out.Mass_flowrate == None and self.Cold_In.Mass_flowrate != None): 
                    
                    self.Cold_Out.Mass_flowrate = self.Cold_In.Mass_flowrate
                    self.Cold_Mass_flowrate = self.Cold_In.Mass_flowrate
                
                elif (self.Cold_Out.Mass_flowrate != None and self.Cold_In.Mass_flowrate == None):    
                    self.Cold_In.Mass_flowrate = self.Cold_Out.Mass_flowrate
                    self.Cold_Mass_flowrate = self.Cold_Out.Mass_flowrate
                elif (self.Cold_Out.Mass_flowrate == self.Cold_In.Mass_flowrate):  
                    self.Cold_Mass_flowrate = self.Cold_Out.Mass_flowrate
                elif (self.Cold_Out.Mass_flowrate != self.Cold_In.Mass_flowrate):    
                    raise ValueError(f'Cold side fluid Mass flowrate of {self.ID} is not match ')
            else:
                self.Cold_Mass_flowrate = None
                
            if self.Charge == 'Discharging':
                if self.Capacity != None:
                    self.CapacityD  = self.Capacity*(1-self.per_loss)
                if(self.Cold_In.H != None and self.Cold_Out.H == None and self.Capacity == None):
                    if self.PPT< (self.T_melt-self.Cold_In.T):
                        self.Cold_Out = self.Model.Prop(self.Cold_Out.fluid, StatePointName = self.Cold_Out.StatePointName,  P = self.Cold_Out.P ,T = self.T_melt - self.PPT,Mass_flowrate=self.Cold_Mass_flowrate)
                        self.CapacityD = (self.Cold_Out.H - self.Cold_In.H)*self.Cold_In.Mass_flowrate*self.Discharging_time*3600
                    else:
                        raise ValueError(f"(PCM Tempeture-PPT) is lower then Inlet Temperture in {self.ID}")
               
                elif(self.Cold_In.H == None and self.Cold_Out.H != None and self.CapacityD == None):
                    raise ValueError("For calculating Coldfluid inlet temperature in {self.ID} CapacityD should given")
               
               
                elif(self.Cold_In.H != None and self.Cold_Out.H != None and self.CapacityD == None):
                     if self.Cold_In.Mass_flowrate == self.Cold_Out.Mass_flowrate:
                         self.CapacityD = (self.Cold_Out.H - self.Cold_In.H)*self.Cold_In.Mass_flowrate*self.Discharging_time*3600
                     else:
                         raise ValueError(f'Cold fluid mass flowrate at inlet and outlet is not equal in {self.ID}')
                         
                elif(self.Cold_In.H == None and self.Cold_Out.H == None and self.CapacityD != None):       
                    self.Cold_Out = self.Model.Prop(self.Cold_Out.fluid, StatePointName = self.Cold_Out.StatePointName,Mass_flowrate=self.Cold_Mass_flowrate, P = self.Cold_Out.P ,T = self.T_melt - self.PPT)
                    H = self.Cold_Out.H - self.CapacityD/(self.Cold_Out.Mass_flowrate*self.Discharging_time*3600)
                    self.Cold_In = self.Model.Prop(self.Cold_In.fluid, StatePointName = self.Cold_In.StatePointName,  P = self.Cold_In.P ,H = H,Mass_flowrate=self.Cold_Mass_flowrate)
                
                elif(self.Cold_In.H != None and self.Cold_Out.H == None and self.CapacityD != None):
                    H = self.Cold_In.H + self.CapacityD/(self.Cold_In.Mass_flowrate*self.Discharging_time*3600)
                    self.Cold_Out = self.Model.Prop(self.Cold_Out.fluid, StatePointName = self.Cold_Out.StatePointName,  P = self.Cold_Out.P ,H = H,Mass_flowrate=self.Cold_Mass_flowrate)
                    if self.PPT > (self.T_melt-self.Cold_Out.T): 
                        raise ValueError(f"(PCM Tempeture-PPT) is lower then Outlet Temperturein {self.ID}")        
                
                elif(self.Cold_In.H == None and self.Cold_Out.H != None and self.CapacityD != None):
                    if self.PPT <= (self.T_melt-self.Cold_Out.T):
                        H = self.Cold_Out.H - self.CapacityD/(self.Cold_Out.Mass_flowrate*self.Discharging_time*3600)
                        self.Cold_In = self.Model.Prop(self.Cold_In.fluid, StatePointName = self.Cold_In.StatePointName,  P = self.Cold_In.P ,H = H,Mass_flowrate=self.Cold_Mass_flowrate)
                    else:
                        raise ValueError(f"(PCM Tempeture-PPT) is lower then Outlet Temperturein {self.ID}")
                
                else:
                    pass
                self.Discharging_Power = self.CapacityD/(self.Discharging_time*3600)
                
            elif self.Charge == 'Charging':
                if(self.Hot_In.H != None and self.Hot_Out.H == None and self.Capacity == None):
                    if self.PPT< (self.Hot_In.T - self.T_melt):
                        self.Hot_Out = self.Model.Prop(self.Hot_Out.fluid, StatePointName = self.Hot_Out.StatePointName,  P = self.Hot_Out.P ,T = self.T_melt + self.PPT,Mass_flowrate=self.Hot_Mass_flowrate)
                        self.Capacity = (self.Hot_In.H - self.Hot_Out.H)*self.Hot_In.Mass_flowrate*self.Charging_time*3600
                    else:
                        raise ValueError(f"(PCM Tempeture+PPT) is higher then Inlet Temperture in {self.ID}")
                elif(self.Hot_In.H == None and self.Hot_Out.H != None and self.Capacity == None):
                     raise ValueError("For calculating Hot fluid inlet temperature of {self.ID}, capacity should given")
                
                elif(self.Hot_In.H != None and self.Hot_Out.H != None and self.Capacity == None):
                     if self.Hot_In.Mass_flowrate == self.Hot_Out.Mass_flowrate:
                         self.Capacity = (self.Hot_In.H - self.Hot_Out.H)*self.Hot_In.Mass_flowrate*self.Charging_time*3600
                     else:
                         raise ValueError(f'Hot fluid mass flowrate at inlet and outlet is not equal in {self.ID}')
                         
                elif(self.Hot_In.H == None and self.Hot_Out.H == None and self.Capacity != None):       
                     self.Hot_Out = self.Model.Prop(self.Hot_Out.fluid, StatePointName = self.Hot_Out.StatePointName,  P = self.Hot_Out.P ,T = self.T_melt + self.PPT,Mass_flowrate=self.Hot_Mass_flowrate)
                     H = self.Hot_Out.H + self.Capacity/(self.Hot_Out.Mass_flowrate*self.Charging_time*3600)
                     self.Hot_In = self.Model.Prop(self.Hot_In.fluid, StatePointName = self.Hot_In.StatePointName,  P = self.Hot_In.P ,H = H,Mass_flowrate=self.Hot_Mass_flowrate)    
   
                elif(self.Hot_In.H != None and self.Hot_Out.H == None and self.Capacity != None):
                    H = self.Hot_In.H - self.Capacity/(self.Hot_In.Mass_flowrate*self.Charging_time*3600)
                    self.Hot_Out = self.Model.Prop(self.Hot_Out.fluid, StatePointName = self.Hot_Out.StatePointName,  P = self.Hot_Out.P ,H = H,Mass_flowrate=self.Hot_Mass_flowrate)
                    if self.PPT <= (self.Hot_Out.T - self.T_melt): 
                        raise ValueError(f"(PCM Tempeture+PPT) is higher then Outlet Temperture in {self.ID}") 
                
                elif(self.Hot_In.H == None and self.Hot_Out.H != None and self.Capacity != None):
                    if self.PPT <= (self.Hot_Out.T - self.T_melt):
                        H = self.Hot_Out.H + self.Capacity/(self.Hot_Out.Mass_flowrate*self.Charging_time*3600)
                        self.Hot_In = self.Model.Prop(self.Hot_In.fluid, StatePointName = self.Hot_In.StatePointName,  P = self.Hot_In.P ,H = H,Mass_flowrate=self.Hot_Mass_flowrate)
                    else:
                        raise ValueError(f"(PCM Tempeture+PPT) is higher then Outlet Temperturein {self.ID}")
                self.Charging_Power = self.Capacity/(self.Charging_time*3600)
            else:
                raise ValueError(f'Invalid input for Charge parameter (Charging or Disharging) for {self.ID}')
            self.Solution_Status = True
            if self.Hot_In_state != None: self.Model.Point[self.Hot_In_state] =  self.Hot_In 
            if self.Hot_Out_state != None: self.Model.Point[self.Hot_Out_state] = self.Hot_Out 
            if self.Cold_In_state != None: self.Model.Point[self.Cold_In_state] = self.Cold_In 
            if self.Cold_Out_state != None: self.Model.Point[self.Cold_Out_state] =  self.Cold_Out 
        def __str__(self):
      
              print(
                  f"{self.ID} Data:\n"
                  f"Hot Inlet Temp: {self.Hot_In.T} C\n"
                  f"Hot Outlet Temp : {self.Hot_Out.T} C\n"
                  f"Hot Mass Flowrate:{self.Hot_Mass_flowrate} kg/s\n"
                   f"Cold Inlet Temp: {self.Cold_In.T } C\n"
                   f"Cold Outlet Temp : {self.Cold_Out.T} C\n"
                   f"Cold Mass Flowrate: {self.Cold_Mass_flowrate} kg/s\n"
                   f"Heat Loss: {self.Capacity-self.CapacityD} Js ({(self.Capacity-self.CapacityD)*100/self.Capacity:0.2f})%\n"
                  f"Charging Power: {self.Charging_Power} W\n"
                  f"Disharging Power: {self.Discharging_Power} W\n"
                  f"PCM store solution status: {self.Solution_Status}"
                  )
       
              return ''
                   
    class HeatExchanger():
        
        def __init__(self,Model,ID,PPT,HEX_type,Hot_In_state,Hot_Out_state,Cold_In_state,
                     Cold_Out_state,UA = None,effectiveness = None,Q = None,div_N=200,PPT_graph = False,Calculate = False):
            self.Model = Model
            self.Hot_In_state = Hot_In_state
            self.Hot_Out_state = Hot_Out_state
            self.Cold_In_state = Cold_In_state
            self.Cold_Out_state  = Cold_Out_state
            self.HEX_type = HEX_type
            self.div_N = div_N
            self.PPT = PPT
            self.PPT_graph = PPT_graph
            self.ID = ID
            self.Hot_to_Cold = None
            self.Q = Q
            self.Hot_Mass_flowrate = None
            self.Cold_Mass_flowrate = None
            self.Solution_Status = False
            self.effectiveness = effectiveness
            self.Model.Component[ID] = self
            self.Calculate = Calculate
            self.UA = UA
            if self.Calculate:
                self.Cal()
            
        def Cal(self):
            self.Hot_In = self.Model.Point[self.Hot_In_state] if self.Hot_In_state != None else None
            self.Hot_Out = self.Model.Point[self.Hot_Out_state] if self.Hot_Out_state != None else None
            self.Cold_In = self.Model.Point[self.Cold_In_state] if self.Cold_In_state != None else None
            self.Cold_Out  = self.Model.Point[self.Cold_Out_state] if self.Cold_Out_state != None else None
            
            
            
            if self.Hot_Out != None or self.Hot_In != None:
                if (self.Hot_Out.Mass_flowrate == None and self.Hot_In.Mass_flowrate != None):    
                    self.Hot_Out.Mass_flowrate = self.Hot_In.Mass_flowrate
                    self.Hot_Mass_flowrate = self.Hot_In.Mass_flowrate
                
                elif (self.Hot_Out.Mass_flowrate != None and self.Hot_In.Mass_flowrate == None):    
                    self.Hot_In.Mass_flowrate = self.Hot_Out.Mass_flowrate
                    self.Hot_Mass_flowrate = self.Hot_Out.Mass_flowrate
                
                elif (self.Hot_Out.Mass_flowrate == self.Hot_In.Mass_flowrate):    
                    self.Hot_Mass_flowrate = self.Hot_In.Mass_flowrate
                    
                elif (self.Hot_Out.Mass_flowrate != self.Hot_In.Mass_flowrate):    
                    raise ValueError(f'Hot side fluid Mass flowrate of {self.ID}is not match ')
            else:
                self.Hot_Mass_flowrate = None
             
            if self.Cold_Out != None or self.Cold_In != None: 
                if (self.Cold_Out.Mass_flowrate == None and self.Cold_In.Mass_flowrate != None):    
                    self.Cold_Out.Mass_flowrate = self.Cold_In.Mass_flowrate
                    self.Cold_Mass_flowrate = self.Cold_In.Mass_flowrate
                    
                
                elif (self.Cold_Out.Mass_flowrate != None and self.Cold_In.Mass_flowrate == None):    
                    self.Cold_In.Mass_flowrate = self.Cold_Out.Mass_flowrate
                    self.Cold_Mass_flowrate = self.Cold_Out.Mass_flowrate
                elif (self.Cold_Out.Mass_flowrate == self.Cold_In.Mass_flowrate):  
                    self.Cold_Mass_flowrate = self.Cold_Out.Mass_flowrate
                elif (self.Cold_Out.Mass_flowrate != self.Cold_In.Mass_flowrate):    
                    raise ValueError(f'Cold side fluid Mass flowrate of {self.ID} is not match ')
            else:
                self.Cold_Mass_flowrate = None
            Th = np.zeros(self.div_N + 1)
            Tc = np.zeros(self.div_N + 1)
            dT = np.zeros(self.div_N + 1)
            h_h = np.zeros(self.div_N + 1)
            h_c = np.zeros(self.div_N + 1)
            
            if self.HEX_type != 'SimpleHEX':
                delta_P_c = self.Cold_In.P - self.Cold_Out.P
                delta_P_h = self.Hot_In.P - self.Hot_Out.P
                
                if (self.Hot_In.H != None and self.Hot_Out.H != None):      
                    if (self.Hot_Mass_flowrate != None and self.Cold_Mass_flowrate != None):
                        Q = (self.Hot_In.H - self.Hot_Out.H)*self.Hot_Mass_flowrate
                        
                        if self.Cold_Out.H == None:
                            HCO = self.Cold_In.H + Q/self.Cold_Mass_flowrate
                            self.Cold_Out = self.Model.Prop(self.Cold_Out.fluid, StatePointName = self.Cold_Out.StatePointName, 
                                                    H = HCO, P = self.Cold_Out.P,Mass_flowrate=self.Cold_Mass_flowrate)
                            self.PPT_Hot_Out()
                        elif self.Cold_In.H == None:
                            HCI = self.Cold_Out.H - Q/self.Cold_Mass_flowrate
                            self.Cold_In = self.Model.Prop(self.Cold_In.fluid, StatePointName = self.Cold_In.StatePointName, 
                                                    H = HCI, P = self.Cold_In.P,Mass_flowrate=self.Cold_Mass_flowrate)
                            self.PPT_Hot_In()
                        
                        q = Q/self.div_N
                        Th[0] = self.Hot_Out.T
                        Tc[0] = self.Cold_In.T
                        dT[0] = Th[0] - Tc[0]
                        h_h[0] = self.Hot_Out.H
                        h_c[0] = self.Cold_In.H
                        
                        for n in range(1,self.div_N+1):
                            
                            h_h[n] = h_h[n-1] + q/self.Hot_Mass_flowrate
                            h_c[n] = h_c[n-1] + q/self.Cold_Mass_flowrate
                            Ph = self.Hot_Out.P + (delta_P_h/self.div_N)*n
                            Pc = self.Cold_In.P - (delta_P_c/self.div_N)*n
                            Th[n] =  self.Model.Prop(self.Hot_In.fluid, StatePointName='Hot I', H = h_h[n],
                                             P = Ph).T
                                             
                            Tc[n] = self.Model.Prop(self.Cold_In.fluid, StatePointName='Cold I', H = h_c[n],
                                             P = Pc).T
                            dT[n] = Th[n] - Tc[n]
                            
                    
                        # if min(dT) < self.PPT:
                        #     warnings.warn(f"Pinch occur. Pinch Point Temp: {min(dT)} K")
                          
                        if(self.PPT_graph):   
                            
                            plt.plot(range(0,self.div_N+1),Th-273.15,color = 'red')
                            plt.plot(range(0,self.div_N+1),Tc-273.15,color = 'blue')
                            plt.legend(['hot','cold'])
                            y1,y2 = (min(min(Tc),min(Th))-273.15-10,max(max(Tc),max(Th))-273.15+10)
                            plt.arrow(np.argmin(dT),(Tc[np.argmin(dT)]+Th[np.argmin(dT)])/2-273.15,-10,-(Tc[np.argmin(dT)]-273.15-y1)*0.6,head_width=2, head_length=5)
                            plt.text(np.argmin(dT)-40, y1+1.5, f"PPT = {min(dT):.2f}\n {self.ID}", fontsize=12, color='blue')
                            plt.ylim((y1,y2))
                            plt.show()
                        
                    else:
                        if self.Cold_Out.H == None:
                            self.PPT_Hot_Out()
                            def f(T):
                                Q = self.Hot_In.H - self.Hot_Out.H
                                if self.HEX_type == 'double_pipe' or self.HEX_type == 'Condenser' :
                                    self.Cold_Out = self.Model.Prop(self.Cold_Out.fluid, StatePointName = self.Cold_Out.StatePointName,
                                                            T = T,
                                                            P = self.Cold_Out.P)
                                
                                elif self.HEX_type == 'Evaporator' : 
                                    Cold_Out_sat = self.Model.Prop(self.Cold_In.fluid, StatePointName = "Cold_out_sat"
                                                           , P = self.Cold_Out.P,Q = 1)
                                    self.Cold_Out = self.Model.Prop(self.Cold_In.fluid, StatePointName = self.Cold_Out.StatePointName,
                                                            T = Cold_Out_sat.T+T,
                                                            P = self.Cold_Out.P)
                                    
                            
                                m_c = Q/(self.Cold_Out.H - self.Cold_In.H)
                                q = Q/self.div_N
                                Th[0] = self.Hot_Out.T
                                Tc[0] = self.Cold_In.T
                                dT[0] = Th[0] - Tc[0]
                                h_h[0] = self.Hot_Out.H
                                h_c[0] = self.Cold_In.H
                                  
                                for n in range(1,self.div_N+1):
                                    h_h[n] = h_h[n-1] + q
                                    h_c[n] = h_c[n-1] + q/m_c
                                    Ph = self.Hot_Out.P + (delta_P_h/self.div_N)*n
                                    Pc = self.Cold_In.P - (delta_P_c/self.div_N)*n
                                    Th[n] =  self.Model.Prop(self.Hot_In.fluid, StatePointName='Hot I', H = h_h[n],
                                                     P = Ph).T
                                                     
                                    Tc[n] = self.Model.Prop(self.Cold_In.fluid, StatePointName='Cold I', H = h_c[n],
                                                     P = Pc).T
                                    dT[n] = Th[n] - Tc[n]
                                dTemp = min(dT) - self.PPT
                                
                                return dTemp
                                
                            try:
                        
                                if self.HEX_type == 'double_pipe' or self.HEX_type == 'Condenser':
                                    T_c_out = brentq(f,self.Cold_In.T+0.0000001,self.Hot_In.T,xtol=0.001,rtol = 0.001)
                                    self.Cold_Out = self.Model.Prop(self.Cold_In.fluid, StatePointName = self.Cold_Out.StatePointName, 
                                                            T = T_c_out, P = self.Cold_Out.P,Mass_flowrate=self.Cold_Mass_flowrate)
                                    
                                elif self.HEX_type == 'Evaporator' : 
                                    T_c_sat = self.Model.Prop(self.Cold_Out.fluid, StatePointName = 'cold out', Q = 1,
                                                      P = self.Cold_Out.P).T
                                    T_sup = brentq(f,0.001,CP.PropsSI("TMAX", self.Cold_Out.fluid)-T_c_sat,xtol=0.001,rtol = 0.001)
                                    
                                    T_c_out = T_c_sat + T_sup
                                    self.Cold_Out = self.Model.Prop(self.Cold_In.fluid, StatePointName = self.Cold_Out.StatePointName, 
                                                            T = T_c_out, P = self.Cold_Out.P)
                                
                                
                                if(self.PPT_graph):   
                                    
                                    plt.plot(range(0,self.div_N+1),Th-273.15,color = 'red')
                                    plt.plot(range(0,self.div_N+1),Tc-273.15,color = 'blue')
                                    plt.legend(['hot','cold'])
                                    y1,y2 = (min(min(Tc),min(Th))-273.15-10,max(max(Tc),max(Th))-273.15+10)
                                    plt.arrow(np.argmin(dT),(Tc[np.argmin(dT)]+Th[np.argmin(dT)])/2-273.15,-10,-(Tc[np.argmin(dT)]-273.15-y1)*0.6,head_width=2, head_length=5)
                                    plt.text(np.argmin(dT)-40, y1+1.5, f"PPT = {min(dT):.2f}\n {self.ID}", fontsize=12, color='blue')
                                    plt.ylim((y1,y2))
                                    plt.show()
                                    
                    
                            except Exception as e:
                                print(f"An unexpected error occurred: {e}")
                                if(self.PPT_graph):   
                                   
                                   plt.plot(range(0,self.div_N+1),Th-273.15,color = 'red')
                                   plt.plot(range(0,self.div_N+1),Tc-273.15,color = 'blue')
                                   plt.legend(['hot','cold'])
                                   y1,y2 = (min(min(Tc),min(Th))-273.15-10,max(max(Tc),max(Th))-273.15+10)
                                   plt.arrow(np.argmin(dT),(Tc[np.argmin(dT)]+Th[np.argmin(dT)])/2-273.15,-10,-(Tc[np.argmin(dT)]-273.15-y1)*0.6,head_width=2, head_length=5)
                                   plt.text(np.argmin(dT)-40, y1+1.5, f"PPT = {min(dT):.2f}\n {self.ID}", fontsize=12, color='blue')
                                   plt.ylim((y1,y2))
                                   plt.show()
                                return "Check the parameters"
                            
                        elif self.Cold_In.H == None:
                            self.PPT_Hot_In()
                            def f(T):
                                Q = self.Hot_In.H - self.Hot_Out.H
                                self.Cold_In = self.Model.Prop(self.Cold_In.fluid, StatePointName = self.Cold_In.StatePointName,
                                                            T = T,
                                                            P = self.Cold_In.P)
                                
                                m_c = Q/(self.Cold_Out.H - self.Cold_In.H)
                                q = Q/self.div_N
                                Th[0] = self.Hot_Out.T
                                Tc[0] = self.Cold_In.T
                                dT[0] = Th[0] - Tc[0]
                                h_h[0] = self.Hot_Out.H
                                h_c[0] = self.Cold_In.H
                                  
                                for n in range(1,self.div_N+1):
                                    h_h[n] = h_h[n-1] + q
                                    h_c[n] = h_c[n-1] + q/m_c
                                    Ph = self.Hot_Out.P + (delta_P_h/self.div_N)*n
                                    Pc = self.Cold_In.P - (delta_P_c/self.div_N)*n
                                    Th[n] =  self.Model.Prop(self.Hot_In.fluid, StatePointName='Hot I', H = h_h[n],
                                                     P = Ph).T
                                                     
                                    Tc[n] = self.Model.Prop(self.Cold_In.fluid, StatePointName='Cold I', H = h_c[n],
                                                     P = Pc).T
                                    dT[n] = Th[n] - Tc[n]
                                dTemp = min(dT) - self.PPT
                            
                                return dTemp
                                
                            try:
                        
                                if self.HEX_type == 'double_pipe' or self.HEX_type == 'Condenser' :
                                    T_c_in = brentq(f,CP.PropsSI("TMIN", self.Cold_In.fluid),self.Hot_In.T,xtol=0.001,rtol = 0.001)
                                    self.Cold_In = self.Model.Prop(self.Cold_In.fluid, StatePointName = self.Cold_In.StatePointName, 
                                                            T = T_c_in, P = self.Cold_In.P,Mass_flowrate=self.Cold_Mass_flowrate)
                                    
                                elif self.HEX_type == 'Evaporator' : 
                                    raise ValueError(f'Mass flowrates are required for calculating cold fluid inlet state for {self.ID}')
                                
                                if(self.PPT_graph):   
                                    
                                    plt.plot(range(0,self.div_N+1),Th-273.15,color = 'red')
                                    plt.plot(range(0,self.div_N+1),Tc-273.15,color = 'blue')
                                    plt.legend(['hot','cold'])
                                    y1,y2 = (min(min(Tc),min(Th))-273.15-10,max(max(Tc),max(Th))-273.15+10)
                                    plt.arrow(np.argmin(dT),(Tc[np.argmin(dT)]+Th[np.argmin(dT)])/2-273.15,-10,-(Tc[np.argmin(dT)]-273.15-y1)*0.6,head_width=2, head_length=5)
                                    plt.text(np.argmin(dT)-40, y1+1.5, f"PPT = {min(dT):.2f}\n {self.ID}", fontsize=12, color='blue')
                                    plt.ylim((y1,y2))
                                    plt.show()
                                    
                    
                            except Exception as e:
                                print(f"An unexpected error occurred: {e}")
                                if(self.PPT_graph):   
                                    
                                    plt.plot(range(0,self.div_N+1),Th-273.15,color = 'red')
                                    plt.plot(range(0,self.div_N+1),Tc-273.15,color = 'blue')
                                    plt.legend(['hot','cold'])
                                    y1,y2 = (min(min(Tc),min(Th))-273.15-10,max(max(Tc),max(Th))-273.15+10)
                                    plt.arrow(np.argmin(dT),(Tc[np.argmin(dT)]+Th[np.argmin(dT)])/2-273.15,-10,-(Tc[np.argmin(dT)]-273.15-y1)*0.6,head_width=2, head_length=5)
                                    plt.text(np.argmin(dT)-40, y1+1.5, f"PPT = {min(dT):.2f}\n {self.ID}", fontsize=12, color='blue')
                                    plt.ylim((y1,y2))
                                    plt.show()
                                return "Check the parameters"
                            
                            
                elif (self.Cold_In.H != None and self.Cold_Out.H != None):
                    
                    if (self.Hot_Mass_flowrate != None and self.Cold_Mass_flowrate != None):
                        
                        Q = (self.Cold_Out.H - self.Cold_In.H)*self.Cold_Mass_flowrate
                        if self.Hot_In.H != None:
                            HHO = self.Hot_In.H - Q/self.Hot_Mass_flowrate
                            self.Hot_Out = self.Model.Prop(self.Hot_In.fluid, StatePointName = self.Hot_Out.StatePointName, 
                                                H = HHO, P = self.Hot_Out.P,Mass_flowrate=self.Hot_Mass_flowrate)
                            self.PPT_Hot_In()
                            
                        elif self.Hot_Out.H !=None:
                            HHI = self.Hot_Out.H + Q/self.Hot_Mass_flowrate
                            self.Hot_In = self.Model.Prop(self.Hot_In.fluid, StatePointName = self.Hot_In.StatePointName, 
                                                H = HHI, P = self.Hot_In.P,Mass_flowrate=self.Hot_Mass_flowrate)
                            self.PPT_Hot_Out()
                        
                        q = Q/self.div_N
                        Th[0] = self.Hot_In.T
                        Tc[0] = self.Cold_Out.T
                        dT[0] = Th[0] - Tc[0]
                        h_c[0] = self.Cold_Out.H
                        h_h[0] = self.Hot_In.H
                        for n in range(1,self.div_N+1):
                            h_h[n] = h_h[n-1] - q/self.Hot_Mass_flowrate
                            h_c[n] = h_c[n-1] - q/self.Cold_Mass_flowrate
                            Ph = self.Hot_In.P - (delta_P_h/self.div_N)*n
                            Pc = self.Cold_Out.P + (delta_P_c/self.div_N)*n
                        
                            Th[n] =  self.Model.Prop(self.Hot_In.fluid, StatePointName='Hot I', H = h_h[n],
                                             P = Ph).T
                                             
                            Tc[n] = self.Model.Prop(self.Cold_In.fluid, StatePointName='Cold I', H = h_c[n],
                                             P = Pc).T
                            dT[n] = Th[n] - Tc[n]
                            
                        if min(dT) < self.PPT:
                            warnings.warn(f"Pinch occur. Pinch Point Temp: {min(dT)} C")
                           
                        if(self.PPT_graph):   
                            Th = np.flip(Th)
                            Tc = np.flip(Tc)
                            dT = np.flip(dT)
                            
                            plt.plot(range(0,self.div_N+1),Th-273.15,color = 'red')
                            plt.plot(range(0,self.div_N+1),Tc-273.15,color = 'blue')
                            plt.legend(['hot','cold'])
                            y1,y2 = (min(min(Tc),min(Th))-273.15-10,max(max(Tc),max(Th))-273.15+10)
                            plt.arrow(np.argmin(dT),(Tc[np.argmin(dT)]+Th[np.argmin(dT)])/2-273.15,-10,-(Tc[np.argmin(dT)]-273.15-y1)*0.6,head_width=2, head_length=5)
                            plt.text(np.argmin(dT)-40, y1+1.5, f"PPT = {min(dT):.2f}\n {self.ID}", fontsize=12, color='blue')
                            plt.ylim((y1,y2))
                            plt.show()
                            
                        
                        
                    else:
                        
                        if self.Hot_Out.H == None:
                            self.PPT_Hot_In()
                            def f(T):
                            
                                Q = self.Cold_Out.H - self.Cold_In.H
                                if self.HEX_type == 'double_pipe' or self.HEX_type == 'Evaporator':
                                    self.Hot_Out = self.Model.Prop(self.Hot_In.fluid, StatePointName = self.Hot_Out.StatePointName,
                                                            T = T,
                                                            P = self.Hot_Out.P,Mass_flowrate=self.Hot_Mass_flowrate)
                                elif self.HEX_type == 'Condenser': 
                                    Hot_Out_sat = self.Model.Prop(self.Hot_In.fluid, StatePointName = "Hot_out_sat"
                                                           , P = self.Hot_Out.P,Q = 1)
                                    self.Hot_Out = self.Model.Prop(self.Hot_In.fluid, StatePointName = self.Hot_Out.StatePointName,
                                                            T = Hot_Out_sat.T-T,
                                                            P = self.Hot_Out.P,Mass_flowrate=self.Hot_Mass_flowrate)
                                
                                
                                m_h = Q/(self.Hot_In.H - self.Hot_Out.H)
                                q = Q/self.div_N
                                Th[0] = self.Hot_In.T
                                Tc[0] = self.Cold_Out.T
                                dT[0] = Th[0] - Tc[0]
                                h_c[0] = self.Cold_Out.H
                                h_h[0] = self.Hot_In.H
                                
                                for n in range(1,self.div_N+1):
                                    h_h[n] = h_h[n-1] - q/m_h
                                    h_c[n] = h_c[n-1] - q
                                    Ph = self.Hot_In.P - (delta_P_h/self.div_N)*n
                                    Pc = self.Cold_Out.P + (delta_P_c/self.div_N)*n
                                
                                    Th[n] =  self.Model.Prop(self.Hot_In.fluid, StatePointName='Hot I', H = h_h[n],
                                                     P = Ph).T
                                                     
                                    Tc[n] = self.Model.Prop(self.Cold_In.fluid, StatePointName='Cold I', H = h_c[n],
                                                     P = Pc).T
                                    dT[n] = Th[n] - Tc[n]
                                    
                                dTemp = min(dT) - self.PPT
                                
                            
                                return dTemp
                                
                            try:
                        
                                if self.HEX_type == 'double_pipe' or self.HEX_type == 'Evaporator':
                                    T_h_out = brentq(f,self.Cold_In.T,self.Hot_In.T-0.001,xtol=0.001,rtol = 0.001)
                                    self.Hot_Out = self.Model.Prop(self.Hot_In.fluid, StatePointName = self.Hot_Out.StatePointName, 
                                                            T = T_h_out, P = self.Hot_Out.P,Mass_flowrate=self.Hot_Mass_flowrate)
                                    
                                elif self.HEX_type == 'Condenser':
                                    T_sup = brentq(f,0.1,100,xtol=0.001,rtol = 0.001)
                                    T_h_out = self.Model.Prop(self.Hot_Out.fluid, StatePointName = 'Hot out', Q = 1,
                                                      P = self.Hot_Out.P).T - T_sup
                                    self.Hot_Out = self.Model.Prop(self.Hot_Out.fluid, StatePointName = self.Hot_Out.StatePointName, 
                                                            T = T_h_out, P = self.Hot_Out.P,Mass_flowrate=self.Hot_Mass_flowrate)
                                
                                if(self.PPT_graph):   
                                    
                                    plt.plot(range(0,self.div_N+1),Th-273.15,color = 'red')
                                    plt.plot(range(0,self.div_N+1),Tc-273.15,color = 'blue')
                                    plt.legend(['hot','cold'])
                                    y1,y2 = (min(min(Tc),min(Th))-273.15-10,max(max(Tc),max(Th))-273.15+10)
                                    plt.arrow(np.argmin(dT),(Tc[np.argmin(dT)]+Th[np.argmin(dT)])/2-273.15,-10,-(Tc[np.argmin(dT)]-273.15-y1)*0.6,head_width=2, head_length=5)
                                    plt.text(np.argmin(dT)-40, y1+1.5, f"PPT = {min(dT):.2f}\n {self.ID}", fontsize=12, color='blue')
                                    plt.ylim((y1,y2))
                                    plt.show()
                                    
                    
                            except Exception as e:
                                print(f"An unexpected error occurred: {e}")
                                if(self.PPT_graph):   
                                    
                                    plt.plot(range(0,self.div_N+1),Th-273.15,color = 'red')
                                    plt.plot(range(0,self.div_N+1),Tc-273.15,color = 'blue')
                                    plt.legend(['hot','cold'])
                                    y1,y2 = (min(min(Tc),min(Th))-273.15-10,max(max(Tc),max(Th))-273.15+10)
                                    plt.arrow(np.argmin(dT),(Tc[np.argmin(dT)]+Th[np.argmin(dT)])/2-273.15,-10,-(Tc[np.argmin(dT)]-273.15-y1)*0.6,head_width=2, head_length=5)
                                    plt.text(np.argmin(dT)-40, y1+1.5, f"PPT = {min(dT):.2f}\n {self.ID}", fontsize=12, color='blue')
                                    plt.ylim((y1,y2))
                                    plt.show()
                                    
                                    print("Check the parameters")
                        elif self.Hot_In.H == None:
                            self.PPT_Hot_Out()
                            def f(T):
                                
                                Q = self.Cold_Out.H - self.Cold_In.H
                                self.Hot_In = self.Model.Prop(self.Hot_In.fluid, StatePointName = self.Hot_In.StatePointName,
                                                            T = T,
                                                            P = self.Hot_In.P,Mass_flowrate=self.Hot_Mass_flowrate)
                               
                                m_h = Q/(self.Hot_In.H - self.Hot_Out.H)
                                q = Q/self.div_N
                                Th[0] = self.Hot_In.T
                                Tc[0] = self.Cold_Out.T
                                dT[0] = Th[0] - Tc[0]
                                h_c[0] = self.Cold_Out.H
                                h_h[0] = self.Hot_In.H
                                
                                for n in range(1,self.div_N+1):
                                    h_h[n] = h_h[n-1] - q/m_h
                                    h_c[n] = h_c[n-1] - q
                                    Ph = self.Hot_In.P - (delta_P_h/self.div_N)*n
                                    Pc = self.Cold_Out.P + (delta_P_c/self.div_N)*n
                                
                                    Th[n] =  self.Model.Prop(self.Hot_In.fluid, StatePointName='Hot I', H = h_h[n],
                                                     P = Ph).T
                                                     
                                    Tc[n] = self.Model.Prop(self.Cold_In.fluid, StatePointName='Cold I', H = h_c[n],
                                                     P = Pc).T
                                    dT[n] = Th[n] - Tc[n]
                                    
                                dTemp = min(dT) - self.PPT
                                
                            
                                return dTemp
                                
                            try:
                        
                                if self.HEX_type == 'double_pipe' or self.HEX_type == 'Evaporator':
                                    T_h_in = brentq(f,self.Hot_Out.T+0.001,CP.PropsSI("TMAX", self.Hot_In.fluid),xtol=0.001,rtol = 0.001)
                                    
                                    self.Hot_In = self.Model.Prop(self.Hot_In.fluid, StatePointName = self.Hot_In.StatePointName, 
                                                            T = T_h_in, P = self.Hot_In.P,Mass_flowrate=self.Hot_Mass_flowrate)
                                    
                                elif self.HEX_type =='Condenser':
                                    raise ValueError(f'Mass flowrates are required for calculating Hot fluid inlet state for {self.ID}')
                                if(self.PPT_graph):   
                                    Th = np.flip(Th)
                                    Tc = np.flip(Tc)
                                    dT = np.flip(dT)
                                    
                                    plt.plot(range(0,self.div_N+1),Th-273.15,color = 'red')
                                    plt.plot(range(0,self.div_N+1),Tc-273.15,color = 'blue')
                                    plt.legend(['hot','cold'])
                                    y1,y2 = (min(min(Tc),min(Th))-273.15-10,max(max(Tc),max(Th))-273.15+10)
                                    plt.arrow(np.argmin(dT),(Tc[np.argmin(dT)]+Th[np.argmin(dT)])/2-273.15,-10,-(Tc[np.argmin(dT)]-273.15-y1)*0.6,head_width=2, head_length=5)
                                    plt.text(np.argmin(dT)-40, y1+1.5, f"PPT = {min(dT):.2f}\n {self.ID}", fontsize=12, color='blue')
                                    plt.ylim((y1,y2))
                                    plt.show()
                                    
                    
                            except Exception as e:
                                print(f"An unexpected error occurred: {e}")
                                if(self.PPT_graph):   
                                    
                                    plt.plot(range(0,self.div_N+1),Th-273.15,color = 'red')
                                    plt.plot(range(0,self.div_N+1),Tc-273.15,color = 'blue')
                                    plt.legend(['hot','cold'])
                                    y1,y2 = (min(min(Tc),min(Th))-273.15-10,max(max(Tc),max(Th))-273.15+10)
                                    plt.arrow(np.argmin(dT),(Tc[np.argmin(dT)]+Th[np.argmin(dT)])/2-273.15,-10,-(Tc[np.argmin(dT)]-273.15-y1)*0.6,head_width=2, head_length=5)
                                    plt.text(np.argmin(dT)-40, y1+1.5, f"PPT = {min(dT):.2f}\n {self.ID}", fontsize=12, color='blue')
                                    plt.ylim((y1,y2))
                                    plt.show()
                                    
                                    print("Check the parameters")
                                    
                elif (self.Cold_In.H != None and self.Hot_In.H != None and 
                      self.effectiveness !=None and self.Cold_Out.H == None and self.Hot_Out.H == None):
                    
                    if (self.Hot_Mass_flowrate != None and self.Cold_Mass_flowrate != None):
                        Ch = self.Hot_Mass_flowrate*self.Hot_In.Cp
                        Cc = self.Cold_Mass_flowrate*self.Cold_In.Cp
                        while True:
                            Cmin = min(Ch,Cc)
                            self.Q = self.effectiveness*Cmin*(self.Hot_In.T - self.Cold_In.T)
                            hh = self.Hot_In.H -self. Q/self.Hot_Mass_flowrate
                            hc = self.Cold_In.H + self.Q/self.Cold_Mass_flowrate
                            
                            self.Hot_Out = self.Model.Prop(self.Hot_Out.fluid, StatePointName = self.Hot_Out.StatePointName, P = self.Hot_Out.P,H = hh,Mass_flowrate=self.Hot_Mass_flowrate)
                            self.Cold_Out = self.Model.Prop(self.Cold_Out.fluid, StatePointName = self.Cold_Out.StatePointName, P = self.Cold_Out.P,H = hc,Mass_flowrate=self.Cold_Mass_flowrate)
                            ch_avg = (self.Hot_In.Cp+self.Hot_Out.Cp)*self.Hot_Mass_flowrate/2
                            cc_avg = (self.Cold_In.Cp+self.Cold_Out.Cp)*self.Cold_Mass_flowrate/2
                            if (abs(Ch-ch_avg)/ch_avg<0.001 and abs(Cc-cc_avg)/cc_avg<0.001):
                                break
                            
                            Ch = ch_avg
                            Cc = cc_avg
                            
                    else:
                        raise ValueError(f"Hot and Cold fluid mass flow rate is required for {self.ID}")
                                
            elif (self.HEX_type == 'SimpleHEX'):
                # print(self.ID,self.Hot_In,self.Hot_Out,self.Hot_Mass_flowrate)
                # print (self.ID,self.Cold_In == None , self.Cold_Out == None , self.Q == None , self.self.Cold_Mass_flowrate == None
                #     , self.Hot_In == None , self.Hot_Out == None)
                if (self.Cold_In != None and self.Cold_Out.H == None and self.Q != None and self.Cold_Mass_flowrate != None
                    and self.Hot_In == None and self.Hot_Out == None):
                    H = self.Q/self.Cold_Mass_flowrate + self.Cold_In.H
                    self.Cold_Out = self.Model.Prop(self.Cold_Out.fluid, StatePointName = self.Cold_Out.StatePointName, P = self.Cold_Out.P, H= H,Mass_flowrate=self.Cold_Mass_flowrate)
                    
                elif (self.Cold_Out != None and self.Cold_In.H  == None and self.Q != None and self.Cold_Mass_flowrate != None
                      and self.Hot_In  == None and self.Hot_Out  == None):
                    H = self.Cold_Out.H - self.Q/self.Cold_Mass_flowrate
                    self.Cold_In = self.Model.Prop(self.Cold_In.fluid, StatePointName = self.Cold_In.StatePointName, P = self.Cold_In.P, H= H,Mass_flowrate=self.Cold_Mass_flowrate)
                    
                elif (self.Cold_Out  != None and self.Cold_In  != None and self.Q == None and self.Cold_Mass_flowrate != None
                      and self.Hot_In  == None and self.Hot_Out  == None):
                    self.Q = (self.Cold_Out.H - self.Cold_In.H)*self.Cold_Mass_flowrate
                    
                elif (self.Hot_In  != None and self.Hot_Out.H  == None and self.Q != None and self.Hot_Mass_flowrate != None
                    and self.Cold_In  == None and self.Cold_Out  == None):
                    H = self.Hot_In.H - self.Q/self.Hot_Mass_flowrate
                    self.Hot_Out = self.Model.Prop(self.Hot_Out.fluid, StatePointName = self.Hot_Out.StatePointName, P = self.Hot_Out.P, H= H,Mass_flowrate=self.Hot_Mass_flowrate)
                
                elif (self.Hot_Out != None and self.Hot_In.H == None and self.Q != None and self.Hot_Mass_flowrate != None
                      and self.Cold_In == None and self.Cold_Out  == None):
                    H = self.Hot_Out.H  + self.Q/self.Hot_Mass_flowrate
                    self.Hot_In = self.Model.Prop(self.Hot_In.fluid, StatePointName = self.Hot_In.StatePointName, P = self.Hot_In.P, H= H,Mass_flowrate=self.Hot_Mass_flowrate)
                    
                elif (self.Hot_Out  != None and self.Hot_In  != None and self.Q == None and self.Hot_Mass_flowrate != None
                      and self.Cold_In  == None and self.Cold_Out  == None):
                    self.Q = (self.Hot_In.H - self.Hot_Out.H)*self.Hot_Mass_flowrate
                else:
                    raise ValueError("Invalid Input. Following sets of inputs is expexted: \n"
                                     '1. Cold fluid Massflow rate and any 2 of the following parameters (Cold Input,Cold Output, Heat Added)\n'
                                     '2. Hot fluid Massflow rate and any 2 of the following parameters (Hot Input,Hot Output, Heat Rejected)\n')
           
            else:
                raise ValueError('Invalid HEX type. Valid HEX = [Evaporator, Condenser, double_pipe, SimpleHEX')
            
            if self.HEX_type != 'SimpleHEX':
                
                self.Hot_to_Cold = (self.Cold_Out.H - self.Cold_In.H)/(self.Hot_In.H - self.Hot_Out.H)
            
                if self.Cold_Mass_flowrate == None and self.Hot_Mass_flowrate  != None:
                    self.Cold_Mass_flowrate = self.Hot_Mass_flowrate/self.Hot_to_Cold
                    self.Cold_In.Mass_flowrate = self.Cold_Mass_flowrate
                    self.Cold_Out.Mass_flowrate = self.Cold_Mass_flowrate
                elif self.Hot_Mass_flowrate  == None and self.Cold_Mass_flowrate != None :
                    self.Hot_Mass_flowrate = self.Cold_Mass_flowrate *self.Hot_to_Cold
                    self.Hot_In.Mass_flowrate = self.Hot_Mass_flowrate
                    self.Hot_Out.Mass_flowrate = self.Hot_Mass_flowrate
                elif self.Hot_Mass_flowrate  == None and self.Cold_Mass_flowrate == None :
                    raise ValueError('Atlest one fluid (Hot or Cold) flowrate is expected')
            if self.Hot_Mass_flowrate != None:
                self.Q = (self.Hot_In.H-self.Hot_Out.H)*self.Hot_Mass_flowrate
            elif self.Cold_Mass_flowrate != None:
                self.Q = (self.Cold_Out.H-self.Cold_In.H)*self.Cold_Mass_flowrate
                
            if self.HEX_type != 'SimpleHEX':
                dT1 = self.Hot_In.T - self.Cold_Out.T
                dT2 = self.Hot_Out.T  - self.Cold_In.T
                
                if (dT1>0 and dT2>0):
                    if dT1 == dT2:
                        LMTD = dT1
                    else:
                        LMTD = (dT1-dT2)/np.log(dT1/dT2)
                    self.UA = self.Q/LMTD
                    
                else:
                    print('Incrise Inlet temperature of hot fluid or mass flow rate of cold fluid ')
                    self.UA = None
            
            self.Solution_Status = True
            if self.Hot_In_state != None: self.Model.Point[self.Hot_In_state] =  self.Hot_In
            if self.Hot_Out_state != None: self.Model.Point[self.Hot_Out_state] = self.Hot_Out
            if self.Cold_In_state != None: self.Model.Point[self.Cold_In_state] = self.Cold_In
            if self.Cold_Out_state != None: self.Model.Point[self.Cold_Out_state] =  self.Cold_Out
        
        
        def PPT_Hot_In(self):
           if (self.Hot_In.T - self.Cold_Out.T) == self.PPT:
               self.PPT =  self.PPT - 0.001
               print('PPT is 0.001K reduced')
           elif (self.Hot_In.T - self.Cold_Out.T) < self.PPT:
               # raise ValueError(f'Pinch already occure in {self.ID} at Hot inlet side')
               print(f'Pinch already occure in {self.ID} at Hot inlet side')
            
        def PPT_Hot_Out(self):
            if (self.Hot_Out.T - self.Cold_In.T) == self.PPT:
                self.PPT =  self.PPT - 0.001
                print('PPT is 0.001K reduced')
            elif (self.Hot_Out.T - self.Cold_In.T) < self.PPT:
                raise ValueError(f'Pinch already occure in {self.ID} at Hot Outlet side PPT = {self.Hot_Out.T - self.Cold_In.T}')
        
       
        
        def optimize(self,fuction,no_of_variable,no_of_obj,upper_lim,lower_lim):
            # fuction = Data['fuction']
            # no_of_variable = Data['no_of_variable']
            # no_of_obj = Data['no_of_obj']
            # upper_lim = Data['upper_lim']
            # lower_lim = Data['lower_lim']
            
            class MyProblem(ElementwiseProblem):
                
                
            
                def __init__(self):
                    super().__init__(n_var=no_of_variable,
                                     n_obj=no_of_obj,
                                     n_ieq_constr=0,
                                     xl=np.array(upper_lim),
                                     xu=np.array(lower_lim))
            
                def _evaluate(self, x, out, *args, **kwargs):
                    
                    
                    result = fuction(x)
                    f1 =  result
                    out["F"] = [f1]
            
            
            problem = MyProblem()
            
            
            algorithm = DE(
                pop_size=10
            )
            
        
            res = minimize(problem,
                           algorithm,
                           seed=10,
                           verbose=False)
        
            return res
        
        def get_outlet(self,T_l,T_h):
            self.Hot_In = self.Model.Point[self.Hot_In_state] if self.Hot_In_state != None else None
            self.Hot_Out = self.Model.Point[self.Hot_Out_state] if self.Hot_Out_state != None else None
            self.Cold_In = self.Model.Point[self.Cold_In_state] if self.Cold_In_state != None else None
            self.Cold_Out  = self.Model.Point[self.Cold_Out_state]  if self.Cold_Out_state != None else None
            # print(self.ID)
            def equations(Vars):
                Vars = Vars[0]
                try:
                    if Case == 1:
                        HHO = Vars
                        self.Hot_Out = self.Model.Prop(self.Hot_Out.fluid,StatePointName = self.Hot_Out.StatePointName,P = self.Hot_Out.P,
                                                       H = HHO,Mass_flowrate = self.Hot_Out.Mass_flowrate)
                        Q = self.Hot_Mass_flowrate*(self.Hot_In.H - Vars)
                        HCO = Q/self.Cold_Mass_flowrate + self.Cold_In.H
                        self.Cold_Out = self.Model.Prop(self.Cold_Out.fluid,StatePointName = self.Cold_Out.StatePointName,P = self.Cold_Out.P,
                                                       H = HCO,Mass_flowrate = self.Cold_Out.Mass_flowrate)
                        
                    elif Case == 2:
                        HHO = Vars
                        self.Hot_Out = self.Model.Prop(self.Hot_Out.fluid,StatePointName = self.Hot_Out.StatePointName,P = self.Hot_Out.P,
                                                       H = HHO,Mass_flowrate = self.Hot_Out.Mass_flowrate)
                        Q = self.Hot_Mass_flowrate*(self.Hot_In.H - Vars)
                        HCI =  self.Cold_Out.H - Q/self.Cold_Mass_flowrate
                       
                        self.Cold_In = self.Model.Prop(self.Cold_In.fluid,StatePointName = self.Cold_In.StatePointName,P = self.Cold_In.P,
                                                       H = HCI,Mass_flowrate = self.Cold_In.Mass_flowrate)
                    elif Case == 3:
                        HHI = Vars
                      
                        self.Hot_In = self.Model.Prop(self.Hot_In.fluid,StatePointName = self.Hot_In.StatePointName,P = self.Hot_In.P,
                                                       H = HHI,Mass_flowrate = self.Hot_In.Mass_flowrate)
                        Q = self.Hot_Mass_flowrate*( Vars - self.Hot_Out.H)
                        HCO = Q/self.Cold_Mass_flowrate + self.Cold_In.H
                        
                        self.Cold_Out = self.Model.Prop(self.Cold_Out.fluid,StatePointName = self.Cold_Out.StatePointName,P = self.Cold_Out.P,
                                                       H = HCO,Mass_flowrate = self.Cold_Out.Mass_flowrate)
                        
                    elif Case == 4:
                        HHI = Vars
                           
                        self.Hot_In = self.Model.Prop(self.Hot_In.fluid,StatePointName = self.Hot_In.StatePointName,P = self.Hot_In.P,
                                                       H = HHI,Mass_flowrate = self.Hot_In.Mass_flowrate)
                        Q = self.Hot_Mass_flowrate*( Vars - self.Hot_Out.H)
                        
                        self.Cold_In = self.Model.Prop(self.Cold_In.fluid,StatePointName = self.Cold_In.StatePointName,P = self.Cold_In.P,
                                                       H =HCI,Mass_flowrate = self.Cold_In.Mass_flowrate)
                    
                   
    
                    Th_in  = self.Hot_In.T
                    Th_out = self.Hot_Out.T
                    Tc_in  = self.Cold_In.T
                    Tc_out = self.Cold_Out.T
    
                    dT1 = Th_in - Tc_out
                    dT2 = Th_out - Tc_in
                    
                    if np.isclose(dT1, dT2):
                        delta_T_lm = dT1
                    elif (dT1> 0 and dT2>0):
                        delta_T_lm = (dT1 - dT2) / np.log(dT1 / dT2)
                    else:
                        delta_T_lm = 1000
                        
                    Q_UA = self.UA * delta_T_lm
                    res = Q - Q_UA 
                    # print(res)
                    return  abs( res)
                except:
                    # print(self.ID,'FAILED')
                    return 99999999
            
                  
            if (self.Hot_In.H != None and self.Hot_Out.H == None and 
                self.Cold_In.H != None and self.Cold_Out.H == None):
                Case = 1
                H_min =  self.Model.Prop(self.Hot_Out.fluid, StatePointName = 'demo1', P = self.Hot_Out.P, T =  T_l)
                H_max =  self.Model.Prop(self.Hot_Out.fluid, StatePointName = 'demo2', P = self.Hot_Out.P, T =  T_h)
              
                
            elif (self.Hot_In.H != None and self.Hot_Out.H == None and 
                self.Cold_In.H == None and self.Cold_Out.H != None):
                Case = 2
                H_min =  self.Model.Prop(self.Hot_Out.fluid, StatePointName = 'demo1', P = self.Hot_Out.P, T =  T_l)
                H_max =  self.Model.Prop(self.Hot_Out.fluid, StatePointName = 'demo2', P = self.Hot_Out.P, T = T_h)
               

            elif (self.Hot_In.H == None and self.Hot_Out.H != None and 
                self.Cold_In.H != None and self.Cold_Out.H == None):
                Case = 3
                H_min =  self.Model.Prop(self.Hot_In.fluid, StatePointName = 'demo1', P = self.Hot_In.P, T =  PropsSI('TMIN', self.Hot_In.fluid)+5)
                H_max =  self.Model.Prop(self.Hot_In.fluid, StatePointName = 'demo2', P = self.Hot_In.P, T =  PropsSI('TMAX', self.Hot_In.fluid))
             
            elif  (self.Hot_In.H == None and self.Hot_Out.H != None and 
                self.Cold_In.H == None and self.Cold_Out.H != None):
                 Case = 4
                 H_min =  self.Model.Prop(self.Hot_In.fluid, StatePointName = 'demo1', P = self.Hot_In.P, T =  PropsSI('TMIN', self.Hot_In.fluid))
                 H_max =  self.Model.Prop(self.Hot_In.fluid, StatePointName = 'demo2', P = self.Hot_In.P, T =  PropsSI('TMAX', self.Hot_In.fluid))
                 
            else:
                 raise ValueError("Exactly two enthalpy values (1 is form hot side and other is from cold side) must be unknown (set to None).")

            H0 = (H_min.H+H_max.H)/2
            solution = fsolve(equations, H0) 
            
            self.Q = (self.Hot_In.H - self.Hot_Out.H)*self.Hot_Mass_flowrate
            if self.Hot_In_state != None: self.Model.Point[self.Hot_In_state] =  self.Hot_In
            if self.Hot_Out_state != None: self.Model.Point[self.Hot_Out_state] = self.Hot_Out
            if self.Cold_In_state != None: self.Model.Point[self.Cold_In_state] = self.Cold_In
            if self.Cold_Out_state != None: self.Model.Point[self.Cold_Out_state] =  self.Cold_Out
            # if self.ID == 'Pre_heater': print(self.ID, self.Hot_In.T, self.Hot_Out.T,  self.Cold_In.T , self.Cold_Out.T ,self.Solution_Status)
        def __str__(self):
            if self.HEX_type == 'SimpleHEX':
                if self.Cold_In != None and self.Hot_In == None:
                    T_in = self.Cold_In.T-273.15
                    T_out = self.Cold_Out.T - 273.15
                
                elif self.Hot_In != None:
                    T_in = self.Hot_In.T-273.15
                    T_out = self.Hot_Out.T - 273.15
                    
                return (
                    f"{self.ID} Data:\n"
                    f"Inlet Temperature: {T_in} C\n"
                    f"Outlet Temperature: {T_out} C\n"
                    f"Heat Exchanged: {self.Q} J\n"
                    f"HEX solution status: {self.Solution_Status}"
                    )
            else:
                try: 
                    return (
                      
                        f"{self.ID} Data:\n"
                        f"Hot Inlet Temp: {self.Hot_In.T - 273.15:.2f} C\n"
                        f"Hot Outlet Temp : {self.Hot_Out.T - 273.15:.2f} C\n"
                        f"Hot Mass Flowrate:{self.Hot_Mass_flowrate} kg/s\n"
                        f"Cold Inlet Temp: {self.Cold_In.T - 273.15:.2f} C\n"
                        f"Cold Outlet Temp : {self.Cold_Out.T - 273.15:.2f} C\n"
                        f"Cold Mass Flowrate: {self.Cold_Mass_flowrate} kg/s\n"
                        f"Heat Exchanged: {self.Q} W\n"
                        f"UA: {self.UA} W/K \n"
                        f"Solution status: {self.Solution_Status}"
                        
                        )
                except:
                    return (
                      
                        f"{self.ID} Data:\n"
                        f"Hot Inlet Temp: {self.Hot_In.T } K\n"
                        f"Hot Outlet Temp : {self.Hot_Out.T} K\n"
                        f"Hot Mass Flowrate:{self.Hot_Mass_flowrate} kg/s\n"
                        f"Cold Inlet Temp: {self.Cold_In.T} K\n"
                        f"Cold Outlet Temp : {self.Cold_Out.T } K\n"
                        f"Cold Mass Flowrate: {self.Cold_Mass_flowrate} kg/s\n"
                        f"Heat Exchanged: {self.Q} W\n"
                        f"UA: {self.UA} W/K \n"
                        f"Solution status: {self.Solution_Status}"
                        
                        )

    class Prop:
        def __init__(self, fluid, StatePointName, Mass_flowrate = None, **properties):
            self.fluid = fluid
            self.Mass_flowrate = Mass_flowrate
            if list(properties.keys())[0] == 'pro':
                properties = properties['pro']            
            self.properties = {k: v for k, v in properties.items() if v is not None}
            self.StatePointName = StatePointName
            self.Points = {}
            # Validate input: ensure exactly two properties are provided
            if len(self.properties) > 2:
                print(self.properties)
                raise ValueError("You must provide exactly two properties out of pressure, temperature, enthalpy, or entropy.")

            # Initialize all attributes
            self.P = None
            self.T = None
            self.H = None
            self.S = None
            self.Q = None
            self.D = None
            self.Cp = None
            
            # Set the known properties
            for key, value in self.properties.items():
                if key not in ['P', 'T', 'H', 'S','Q','D']:
                    raise ValueError(f"Invalid property: {key}")
                setattr(self, key, value)
            
            
            if self.fluid == 'Therminol66' and  len(self.properties) == 2:
                self.Therminol66_cal()
            else:
                # Calculate the missing properties
                if len(self.properties) == 2:
                    self.calculate_missing_properties()
             
            
        def is_near_saturation(self, pressure, temperature):

            T_sat = CP.PropsSI("T", "P", pressure, "Q", 0, self.fluid)
            if abs(temperature - T_sat)/T_sat < 1e-4:
                warnings.warn(f'State point {self.StatePointName} is near saturation point.Try other parameters (Q,H or S)')
            return abs(temperature - T_sat)/T_sat < 1e-4
            
        def calculate_missing_properties(self):
            """
            Calculate the missing thermodynamic properties using CoolProp.
            """
            # Get the keys and values of the provided properties
            prop1, prop2 = list(self.properties.keys())
            value1, value2 = list(self.properties.values())
            check = False

            if prop1 == "P" and prop2 == "T":
                pressure = value1
                temperature = value2
                check = self.is_near_saturation(pressure, temperature)
            elif prop1 == "T" and prop2 == "P":
                pressure = value2
                temperature = value1
                check = self.is_near_saturation(pressure, temperature)
                
            if check:
                # Handle two-phase region (assume saturated liquid or vapor)
                self.T = CP.PropsSI("T", "P", pressure, "Q", 0, self.fluid)
                self.P = pressure
                self.H = CP.PropsSI("H", "P", pressure, "Q", 0, self.fluid)
                self.S = CP.PropsSI("S", "P", pressure, "Q", 0, self.fluid)
                self.Cp = CP.PropsSI("C", "P", pressure, "Q", 0, self.fluid)
                return

            try:
                
                # Calculate the missing properties
                self.P = CP.PropsSI("P", prop1.upper(), value1, prop2.upper(), value2, self.fluid) if self.P is None else self.P
                self.T = CP.PropsSI("T", prop1.upper(), value1, prop2.upper(), value2, self.fluid) if self.T is None else self.T
                self.H = CP.PropsSI("H", prop1.upper(), value1, prop2.upper(), value2, self.fluid) if self.H is None else self.H
                self.S = CP.PropsSI("S", prop1.upper(), value1, prop2.upper(), value2, self.fluid) if self.S is None else self.S
                self.Q = CP.PropsSI("Q", prop1.upper(), value1, prop2.upper(), value2, self.fluid) if self.Q is None else self.Q
                self.D = CP.PropsSI("D", prop1.upper(), value1, prop2.upper(), value2, self.fluid) if self.D is None else self.D
                self.Cp = CP.PropsSI("C", prop1.upper(), value1, prop2.upper(), value2, self.fluid) if self.Cp is None else self.Cp
                
                
                if self.H < CP.PropsSI("H", "P", self.P, "Q", 0, self.fluid): 
                    T = CP.PropsSI("T", "P", self.P, "Q", 0, self.fluid) - self.T
                    self.Q = f"S.Cooled ({T:.2f})"
                elif self.H > CP.PropsSI("H", "P", self.P, "Q", 1, self.fluid): 
                    T = self.T - CP.PropsSI("T", "P", self.P, "Q", 0, self.fluid)
                    self.Q = f"S.Heated ({T:.2f})"
            except Exception as e:
                raise ValueError(f"Error calculating properties: {e}")
        
        def Therminol66_cal(self):
            
            with open("T66.json", "r") as f:
                prop = json.load(f)
            data = prop["fluids"]["T66"]
            h_mean = prop["h_normalization"]["h_mean"]
            h_std = prop["h_normalization"]["h_std"]
            prop1, prop2 = list(self.properties.keys())
            value1, value2 = list(self.properties.values())
          
            if (prop1 == 'T' and prop2 == 'P'):
                self.T = value1
                self.P = value2
            elif (prop2 == 'T' and prop1 == 'P'):
                self.T = value2
                self.P = value1
            elif (prop1 == 'H' and prop2 == 'P'):
                self.H = value1
                self.P = value2
            elif (prop2 == 'H' and prop1 == 'P'):
                self.H = value2
                self.P = value1
            else:
                raise ValueError("Pressure and temperature/enthalpy are the valid input parameter for Therminol66")
            density_coeffs = data["density"]["coeffs"]
            cp_coeffs = data["specific_heat"]["coeffs"]
            conductivity_coeffs = data["conductivity"]["coeffs"]
            viscosity_coeffs = data["viscosity"]["coeffs"]
            enthalpy_coeffs = data["enthalpy"]["coeffs"]
            # entropy_coeffs = data["entropy"]["coeffs"]
            inverse_enthalpy_coeffs = data["inverse_enthalpy"]["coeffs"]

            # Function to get all properties at a given temperature
            if self.T != None:
                T_K = self.T
                self.D = np.polyval(density_coeffs, T_K)
                self.Cp = np.polyval(cp_coeffs, T_K)
                # k = conductivity_interp(T_K)
                # mu = viscosity_interp(T_K)
                self.H = np.polyval(enthalpy_coeffs, T_K)
                # self.S =  np.polyval(entropy_coeffs, T_K)
              
            
            elif self.H != None:
                H_normal = (self.H - h_mean)/h_std
                self.T = np.polyval(inverse_enthalpy_coeffs, H_normal)
                T_K = self.T
               
                self.D = np.polyval(density_coeffs, T_K)
                self.Cp = np.polyval(cp_coeffs, T_K)
                # k = conductivity_interp(T_K)
                # mu = viscosity_interp(T_K)
                self.H = np.polyval(enthalpy_coeffs, T_K)
                # self.S =  np.polyval(entropy_coeffs, T_K)
        def Prop_update(self,**properties):
            if list(properties.keys())[0] == 'pro':
                properties = properties['pro']            
            self.properties = {k: v for k, v in properties.items() if v is not None}
            self.properties['P'] = self.P
            if len(self.properties) > 2:
                print(self.properties)
                raise ValueError("You must provide exactly two properties out of pressure, temperature, enthalpy, or entropy.")

            # Initialize all attributes
            self.T = None
            self.H = None
            self.S = None
            self.Q = None
            self.D = None
            self.Cp = None
            
            # Set the known properties
            for key, value in self.properties.items():
                if key not in ['P', 'T', 'H', 'S','Q','D']:
                    raise ValueError(f"Invalid property: {key}")
                setattr(self, key, value)
            
            
            if self.fluid == 'Therminol66' and  len(self.properties) == 2:
                self.Therminol66_cal()
            else:
                # Calculate the missing properties
                if len(self.properties) == 2:
                    self.calculate_missing_properties()
            
        def __str__(self):
            try:
                return (
                    f"Thermodynamic State of {self.StatePointName}:\n"
                    f"Fluid: {self.fluid}\n"
                    f"Pressure: {self.P:.2f} Pa\n"
                    f"Temperature: {self.T-273.15:.2f} degC\n"
                    f"Enthalpy: {self.H:.2f} J/kg\n"
                    f"Entropy: {self.S:.2f} J/kg.K\n"
                    f"Quality: {self.Q} \n"
                    f"Mass flowrate: {self.Mass_flowrate} kg/s\n"
                    
                )
            except:
                return (
                    f"Thermodynamic State of {self.StatePointName}:\n"
                    f"Fluid: {self.fluid}\n"
                    f"Pressure: {self.P} Pa\n"
                    f"Temperature: {self.T} K\n"
                    f"Enthalpy: {self.H} J/kg\n"
                    f"Entropy: {self.S} J/kg.K\n"
                    f"Quality: {self.Q} \n"
                    f"Mass flowrate: {self.Mass_flowrate} kg/s\n"
                ) 




