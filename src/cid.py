
#
# Author: Alec S. Adair
# C/Id Lookup Table Object
#
# Creation Date: March 24, 2023
#

import sys, os, getpass, shutil, operator, collections, copy, re
from os.path import expanduser
from scipy import interpolate
import numpy as np
import constants
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.ticker as mticker
from matplotlib import cm
import matplotlib.tri as mtri
import pandas as pd

matplotlib.use('TKAgg')
import matplotlib.pyplot as plt

# CID is master object
# Base object is CIDCorner
# CIDCorner and middle layers should inherit all methods from CID
# CID is a "virtual" class - defines all method stubs for lookups
class CID:

    def __init__(self):
        self.techs = {}

    def add_tech_lut(self, tech_name, device_flavor="rvt", corner_name="tt", lut_csv="./LUTs/sky130_tt_25.csv", vdd=0.0):
        if(os.path.isfile(lut_csv)):
            print("Corner LUT file " + lut_csv + "does not exist.")
            return(False)
        cid_tech = None
        if tech_name not in self.techs:
            cid_tech = CIDTech(tech_name)
        else:
            cid_tech = self.techs[tech_name]
        cid_tech.add_device_lut(tech_name=tech_name, device_flavor=device_flavor, corner_name=corner_name, lut_csv=lut_sv, vdd=vdd)
        self.techs[tech_name] = cid_tech
        return(True)

    def get_bucket_for_ids_measurement(self, tech, flavor, corner, fet_type, l, ids_target):
        if tech_name not in self.techs:
            print("tech " + tech + "does not exist")
            return False
        tech = self.techs[tech]
        ids_bucket = tech.get_bucket_for_ids_measurement(flavor, corner, fet_type, l, ids_target)
        return ids_bucket

    @staticmethod
    def normalize_array(input_array):
        max_val = 0
        normalized_array = []
        for num in input_array:
            if num >= max_val:
                max_val = num
        min_val = max_val
        for num in input_array:
            if num <= min_val:
                min_val = num
        for num in input_array:
            normalized_array.append((num - min_val) / (max_val - min_val))
        return normalized_array


# Should Inherit CID 
class CIDTech(CID):

    def __init__(self, tech_name):
        self.tech_name = tech_name
        self.devices = {}

    def add_device_lut(self, tech_name, device_flavor, corner_name, lut_csv, vdd=0.0):
        device = None
        if device_flavor in self.devices:
            device = self.devices[device_flavor]
        else:
            device = CIDDevice(device=device_flavor, corner_name=corner_name, lut_csv=lut_csv, vdd=vdd)
        device.add_corner_lut(corner_name, lut_csv, vdd)

        return True

    def get_bucket_for_ids_measurement(self, device_flavor, corner, fet_type, l, ids_target):
        if device_flavor not in self.devices:
            print("Device " + device_flavor + "does not exist in tech " + self.tech_name)
            return 0.0
        device = self.devices[device_flavor]
        ids_bucket = device.get_bucket_for_ids_measurement(corner, fet_type, l, ids_target)
        return ids_bucket


# Should Inherit CIDTech
class CIDDevice(CIDTech):

    def __init__(self, device, corner_name, lut_csv, vdd):
        self.device_name = device
        self.corners = {}

    def add_corner_lut(self, corner_name, lut_csv, vdd):
        corner = None
        if corner_name not in self.corners:
            corner = CIDCorner(corner_name, lut_csv, vdd)
        else:
            corner = self.corners[corner_name]
        corner.import_lut(lut_csv, vdd)
        self.corners[corner_name] = corner

    def get_bucket_for_ids_measurement(self, corner_name, fet_type, l, ids_target):
        if corner_name not in self.corners:
            print("Corner " + corner + " does not exist in device " + self.device_name)
            return 0.0
        corner = self.corners[corner_name]
        ids_bucket = corner.get_bucket_for_ids_measurement(fet_type, l, ids_target)
        return ids_bucket
# Should Inherit CIDDevice
class CIDCorner(CIDDevice):

    def __init__(self, corner_name="", lut_csv="", vdd=0.0):
        self.vdd = vdd
        self.max_min_vals = {}
        self.ic_consts = {}
        self.lut = None
        self.corner_name = corner_name
        self.lut_csv = lut_csv
        self.df = None
        self.nfet_df = None
        self.pfet_df = None

        if lut_csv != "" and os.path.isfile(lut_csv):
            self.import_lut(lut_csv, vdd)

    def reset_df(self):
        self.df.reset_index()

    def import_lut(self, lut_csv, vdd=0.0, corner_name=""):
        if not os.path.isfile(lut_csv):
            print("File " + lut_csv + "does not exist.")
            return(False)
        self.vdd = vdd
        self.df = pd.read_csv(lut_csv, skipinitialspace=True)
        self.lut_csv = lut_csv
        if corner_name == "":
            self.corner_name = corner_name
        self.df.reset_index()
        return 0

    #method not needed
    @staticmethod
    def get_bucket_for_ids_measurement(self, fet_type, l, ids_target):
        ids_diff = 10e6
        l_str = str(l)
        ids_range = self.lookup_tables[tech][fet_type][l_str]
        ids_output = 0
        for ids in ids_range:
            ids_float = float(ids)
            ids_target_float = float(ids_target)
            ids_current_diff = abs(ids_target_float - ids_float)
            if(ids_current_diff <= ids_diff):
                ids_diff = ids_current_diff
                ids_output = ids
        return(ids_output)


    def get_closest_param_val(self, param, param_val):
        self.get_closest_param_value(param, param_val)

    def get_closest_param_in_df(self, param, param_val):
        largest_param_diff = 1e33
        closest_param = None
        for i, row in self.df.iterrows():
            param_i = row[param]
            param_diff = abs(param_i - param_val)
            if param_diff >= largest_param_diff:
                largest_param_diff = param_diff
                closest_param = param_i

        return closest_param


    def get_closest_param_value(self, fet_type, length, param, param_val):
        largest_param_diff = 1e33
        length_str = str(length)
        closest_param = None
        fet_type_str = str(fet_type)
        if fet_type == "nfet":
            fet_type = 0.0
        elif fet_type == "pfet":
            fet_type = 1.0
        elif fet_type == 0:
            fet_type = 0.0
        elif fet_type == 1:
            fet_type = 1.0
        else:
            print("fet type " + fet_type_str + " is not valid")
            return -1
        fet_type_int = fet_type
        param_diff = 0
        for i, row in self.df.iterrows():
            param_i = row[param]
            l_i = row["L"]
            type_i = row["type"]
            if l_i == length_str and fet_type == type_i:
                param_diff = abs(param_i - param_val)
                if param_diff > largest_param_diff:
                    largest_param_diff = param_diff
                    closest_param = param_i
        return closest_param


    def get_bucket_for_length(self, fet_type, target_l):
        float_type = 0.0
        if fet_type == "pfet":
            float_type = 1.0
        type_df = self.df.loc[self.df['type'] == float_type]
        print(type_df)
        return(0)

    def get_bucket_for_param(self, fet_type, l, ids_target):
        closest_l = self.get_bucket_for_length(fet_type=fet_type, target_l=l)
        print("TODO")


    def lookup(self, param1, param2, fet_type, l, id):
        l_str = str(l)
        id_str = str(id)
        #id_bucket = self.get_bucket_for_ids_measurement(fet_type, l, id)
        


