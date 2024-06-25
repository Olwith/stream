# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 19:39:47 2024

@author: Olwith
"""

#Declare Variables for current and previous units
current_meter_reading = 625 # in kwh
previous_meter_reading = 400 # in kwh

#Calculate Units of electricity consumed
#We will use basic arithmetic of substraction to get the difference

units_consumed = current_meter_reading - previous_meter_reading

#Display total units consumed

print(f"Total Units of Electricity Consumed is {units_consumed}kwh")