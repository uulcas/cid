
#
# Author: Alec S. Adair
# C/Id Lookup Table Object
#
# Creation Date: March 24, 2023
#

import sys, os, getpass, shutil, operator, collections, copy, re
#from os.path import expanduser
#from scipy import interpolate
import numpy as np
#import constants
#from mpl_toolkits.mplot3d import Axes3D
#import matplotlib.ticker as mticker
#from matplotlib import cm
#import matplotlib.tri as mtri
import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import pandas as pd
import math

#matplotlib.use('TKAgg')
#import matplotlib.pyplot as plt

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
        if tech not in self.techs:
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


class CIDTech:

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

class CIDCornerCollection:
    def __init__(self, collection_name, file_list=None, corner_list=None):
        self.collection_name = collection_name
        self.corners = []
        if corner_list != None:
            for corner in corner_list:
                self.corners.append(corner)
        if file_list != None:
            for file in file_list:
                self.add_corner_from_lut(corner_name=file, lut_csv=file, vdd=0)

    def add_corner_from_lut(self, corner_name, lut_csv, vdd):
        #corner = None
        #if corner_name not in self.corners:
        #    corner = CIDCorner(corner_name, lut_csv, vdd)
        #else:
        #    corner = self.corners[corner_name]
        #corner.import_lut(lut_csv, vdd)
        #self.corners[corner_name] = corner
        if os.path.exists(lut_csv):
            corner = CIDCorner(corner_name=corner_name, lut_csv=lut_csv, vdd=vdd)
            self.corners.append(corner)

    def magic_equation(self, gbw, cload, epsilon=5, show_plot=False, new_plot=True, ax1=None, fig1=None):
        kgm_min = 1e13
        ids_opt = 1e13
        first_corner = True
        color_list = ["blue", "orange", "green", "red", "purple", "brown", "pink", "gray", "olive", "cyan"]
        color_index = 0
        color_list_length = len(color_list)
        if ax1 == None or fig1 == None:
            ax1, fig1 = plt.subplots()
        for corner in self.corners:
            color = color_list[color_index]
            if first_corner == True:
                new_plot = True
            ids_opt, kgm_opt, ax1, fig1 = corner.magic_equation(gbw=gbw, cload=cload, show_plot=show_plot, new_plot=new_plot,
                                                     ax1=ax1, fig1=fig1, color=color)
            if abs(kgm_opt) < kgm_min:
                kgm_min = kgm_opt
            new_plot = False
            first_corner = False
            if(color_index == color_list_length - 1):
                color_index = 0
            else:
                color_index = color_index + 1
        max_id_corner = 0
        min_id_corner = 1e13
        kgm_step_size = kgm_min/100
        kgm_convergence = 0
        kgm_eval = kgm_min
        while kgm_eval > 0:
        #for i in reversed(range(0, kgm_min, kgm_step_size)):
            for corner in self.corners:
                #ids_opt, kgm_opt = corner.magic_equation(gbw=gbw, cload=cload, show_plot=show_plot, new_plot=new_plot,
                #                                         ax1=ax1, fig1=fig1)
                ids = abs(corner.evaluate_magic_function(gbw, cload, kgm_eval))
                if ids > max_id_corner:
                    max_id_corner = ids
                if ids < min_id_corner:
                    min_id_corner = ids
                percentage_diff = 100
                if min_id_corner != max_id_corner:
                    percentage_diff = (1 - (min_id_corner/max_id_corner))*100
                if percentage_diff < epsilon:
                    average_current = (max_id_corner + min_id_corner)/2
                    return average_current, kgm_eval
            kgm_eval = kgm_eval - kgm_step_size
        print("Device does not converge within " + str(epsilon) + "%")
        return -1, -1

    def plot_processes_params(self, param1, param2, norm_type="", show_plot=True, new_plot=True, fig1=None, ax1=None):
        corner_list = self.corners
        first_corner = True
        color_list = ['r-', 'b-', 'g-', 'c-', 'm-', 'y-', 'k-']
        color_list = ["blue", "orange", "green", "red", "purple", "brown", "pink", "gray", "olive", "cyan"]
        color_list_length = len(color_list)
        color_index = 0
        for corner in corner_list:
            color = color_list[color_index]
            corner_pdk = corner.pdk
            length_str = str(corner.length)
            corner_name = corner.corner_name
            legend_str = "PDK: " + corner_pdk + ", L: " + length_str + ", corner: " + corner_name
            if first_corner == True:
                fig1, ax1 = corner.plot_processes_params(param1=param1, param2=param2, norm_type=norm_type, show_plot=True,
                                                         new_plot=new_plot, fig1=fig1, ax1=ax1, color=color, legend_str=legend_str)
                first_corner = False
            else:
                fig1, ax1 = corner.plot_processes_params(param1=param1, param2=param2, norm_type=norm_type, show_plot=show_plot,
                                                         new_plot=False, fig1=fig1, ax1=ax1, color=color, legend_str=legend_str)
            if(color_index == color_list_length - 1):
                color_index = 0
            else:
                color_index = color_index + 1
        return 0

class CIDDevice:

    def __init__(self, device_name, vdd=0.0, lut_directory=None, corner_list=None):
        self.device_name = device_name
        self.vdd = vdd
        self.corners = []
        self.length = 0
        self.pdk = 0
        if corner_list != None:
            for corner in corner_list:
                self.corners.append(corner)
        if lut_directory != None and os.path.exists(lut_directory):
            i = 0
            base_corner_name = ""
            for filename in os.listdir(lut_directory):
                filename_parse = filename.split(".")
                lut_file = os.path.join(lut_directory, filename)
                corner_name = base_corner_name + filename_parse[0]
                corner = CIDCorner(corner_name=corner_name,
                                   lut_csv=lut_file,
                                   vdd=vdd)
                self.corners.append(corner)
                i = i + 1
        if len(self.corners) != 0:
            pdk_col = self.corners[0].df["pdk"]
            l_col = self.corners[0].df["L"]
            self.pdk = pdk_col[0]
            self.length = l_col[0]

    def add_corner_from_lut(self, corner_name, lut_csv, vdd):
        #corner = None
        #if corner_name not in self.corners:
        #    corner = CIDCorner(corner_name, lut_csv, vdd)
        #else:
        #    corner = self.corners[corner_name]
        #corner.import_lut(lut_csv, vdd)
        #self.corners[corner_name] = corner
        if os.path.exists(lut_csv):
            corner = CIDCorner(corner_name=corner_name, lut_csv=lut_csv, vdd=vdd)
            self.corner_list.append(corner)

    def magic_equation(self, gbw, cload, epsilon=10, show_plot=False, new_plot=True, ax1=None, fig1=None):
        kgm_min = 1e13
        ids_opt = 1e13
        first_corner = True
        color_list = ["blue", "orange", "green", "red", "purple", "brown", "pink", "gray", "olive", "cyan"]
        color_index = 0
        color_list_length = len(color_list)
        if ax1 == None or fig1 == None and show_plot == True and new_plot == False:
            ax1, fig1 = plt.subplots()
        for corner in self.corners:
            color = color_list[color_index]
            if first_corner == True:
                new_plot = True
            ids_opt, kgm_opt, ax1, fig1 = corner.magic_equation(gbw=gbw, cload=cload, show_plot=show_plot, new_plot=new_plot,
                                                     ax1=ax1, fig1=fig1, color=color)
            if abs(kgm_opt) < kgm_min:
                kgm_min = kgm_opt
            new_plot = False
            first_corner = False
            if(color_index == color_list_length - 1):
                color_index = 0
            else:
                color_index = color_index + 1
        max_id_corner = 0
        min_id_corner = 1e13
        kgm_step_size = kgm_min/100
        kgm_convergence = 0
        kgm_eval = kgm_min
        while kgm_eval > 0:
        #for i in reversed(range(0, kgm_min, kgm_step_size)):
            for corner in self.corners:
                #ids_opt, kgm_opt = corner.magic_equation(gbw=gbw, cload=cload, show_plot=show_plot, new_plot=new_plot,
                #                                         ax1=ax1, fig1=fig1)
                ids = abs(corner.evaluate_magic_function(gbw, cload, kgm_eval))
                if ids > max_id_corner:
                    max_id_corner = ids
                if ids < min_id_corner:
                    min_id_corner = ids
                percentage_diff = 100
                if min_id_corner != max_id_corner:
                    percentage_diff = (1 - (min_id_corner/max_id_corner))*100
                if percentage_diff < epsilon:
                    average_current = (max_id_corner + min_id_corner)/2
                    return average_current, kgm_eval
            kgm_eval = kgm_eval - kgm_step_size
        print("Device does not converge within " + str(epsilon) + "% Across PVT")
        return -1, -1

    def plot_processes_params(self, param1, param2, norm_type="", show_plot=True, new_plot=True, fig1=None, ax1=None):
        corner_list = self.corners
        first_corner = True
        color_list = ['r-', 'b-', 'g-', 'c-', 'm-', 'y-', 'k-']
        color_list = ["blue", "orange", "green", "red", "purple", "brown", "pink", "gray", "olive", "cyan"]
        color_list_length = len(color_list)
        color_index = 0
        for corner in corner_list:
            color = color_list[color_index]
            corner_pdk = corner.pdk
            length_str = str(corner.length)
            corner_name = corner.corner_name
            legend_str = "PDK: " + corner_pdk + ", L: " + length_str + ", corner: " + corner_name
            if first_corner == True:
                fig1, ax1 = corner.plot_processes_params(param1=param1, param2=param2, norm_type=norm_type, show_plot=True,
                                                         new_plot=new_plot, fig1=fig1, ax1=ax1, color=color, legend_str=legend_str)
                first_corner = False
            else:
                fig1, ax1 = corner.plot_processes_params(param1=param1, param2=param2, norm_type=norm_type, show_plot=show_plot,
                                                         new_plot=False, fig1=fig1, ax1=ax1, color=color, legend_str=legend_str)
            if(color_index == color_list_length - 1):
                color_index = 0
            else:
                color_index = color_index + 1
        return 0





class CIDCorner():

    def __init__(self, corner_name="", lut_csv="", vdd=0.0):
        self.vdd = vdd
        self.max_min_vals = {}
        self.ic_consts = {}
        self.lut = None
        self.corner_name = corner_name
        self.lut_csv = lut_csv
        self.df = None
        self.length = 0
        self.nfet_df = None
        self.pfet_df = None
        self.pdk = ""

        if lut_csv != "" and os.path.isfile(lut_csv):
            self.import_lut(lut_csv, vdd, corner_name=corner_name)
        else:
            print("LUT CSV File " + lut_csv + " does not exist")
            return None

    def reset_df(self):
        self.df.reset_index()

    def import_lut(self, lut_csv, vdd=0.0, corner_name=""):
        if not os.path.isfile(lut_csv):
            print("File " + lut_csv + "does not exist.")
            return(False)
        self.vdd = vdd
        self.df = pd.read_csv(lut_csv, skipinitialspace=True)
        pdk_col = self.df["pdk"]
        self.pdk = pdk_col[0]
        self.lut_csv = lut_csv
        length_col = self.df["L"]
        self.length = length_col[0]
        if corner_name == "":
            self.corner_name = corner_name
        self.df.reset_index()
        if not self.check_if_param_exists("ft"):
            ft_array = []
            cgg_col = self.df["cgg"]
            gm_col = self.df["gm"]
            for i in range(len(cgg_col)):
                cgg = cgg_col[i]
                gm = gm_col[i]
                ft = gm/(2*math.pi*cgg)
                ft_array.append(ft)
            self.df["ft"] = ft_array
        if not self.check_if_param_exists("gmro"):
            gmro_array = []
            gds_gm_array = []
            gm_col = self.df["gm"]
            ro_col = self.df["ro"]
            for i in range(len(gm_col)):
                gm = gm_col[i]
                ro = ro_col[i]
                gmro = gm*ro
                gds_gm = 1/gmro
                gmro_array.append(gmro)
                gds_gm_array.append(gds_gm)
            self.df["gmro"] = gmro_array
            self.df["gm/gds"] = gmro_array
            self.df["gds/gm"] = gds_gm_array
        if not self.check_if_param_exists("iden"):
            iden_array = []
            ids_col = self.df["ids"]
            width = self.df["W"][0]
            for i in range(len(ids_col)):
                ids = ids_col[i]
                iden = ids/width
                iden_array.append(iden)
            self.df["iden"] = iden_array
        if not self.check_if_param_exists("kgmft"):
            kgmft_array = []
            kgm_col = self.df["kgm"]
            ft_col = self.df["ft"]
            for i in range(len(kgm_col)):
                kgm = kgm_col[i]
                ft = ft_col[i]
                kgmft = kgm*ft
                kgmft_array.append(kgmft)
            self.df["kgmft"] = kgmft_array
            self.df["gmidft"] = kgmft_array
        if not self.check_if_param_exists("vds"):
            vds_array = []
            vds_col = self.df["VDS"]
            for i in range(len(vds_col)):
                vds = vds_col[i]
                vds_array.append(vds)
            self.df["vds"] = vds_array
        if not self.check_if_param_exists("vgs"):
            vgs_array = []
            vgs_col = self.df["VGS"]
            for i in range(len(vgs_col)):
                vgs = vgs_col[i]
                vgs_array.append(vgs)
            self.df["vgs"] = vgs_array
        """
        if not self.check_if_param_exists("dkcgs"):
            kcgs_col = self.df["kcgs"]
            kgm_col = self.df["kgm"]
            num = np.diff(kcgs_col)
            denom = np.diff(kgm_col)
            dkcgs_array = np.diff(kcgs_col)/np.diff(kgm_col)
            dkcgs_array = np.append(dkcgs_array, 0.0)
            self.df["dkcgs"] = dkcgs_array
        """
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
        smallest_param_diff = 1e33
        closest_param = None
        index = 0
        param_col = self.df[param]
        for i in range(0, len(param_col)):
        #for i, row in self.df.iterrows():
            param_i = param_col[i]
            param_diff = abs(param_i - param_val)
            if param_diff <= smallest_param_diff:
                smallest_param_diff = param_diff
                closest_param = param_i
                index = i
        return closest_param, index


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


    def lookup2(self):
        print("TODO")


    def lookup3(self, param1, param2, fet_type, l, norm_type="",):
        print("TODO")


    def bucket_lookup_val(self, param, val):
        print("TODO")


    def lookup(self, param1, param2, param1_val):
        if not self.check_if_param_exists(param1) and self.check_if_param_exists(param2):
            return None
        closest_value = self.df[param1].values[np.abs(self.df[param1].values - param1_val).argmin()]
        result = self.df.loc[self.df[param1] == closest_value, param2].values[0]
        return result

    def check_if_param_exists(self, param):
        if param in self.df.columns:
            return True
        else:
            return False

    def get_max_val_for_param(self, param):
        if not self.check_if_param_exists(param):
            return None
        max_value = self.df[param].max()
        # get the row number of the maximum value
        row_number = self.df.loc[self.df[param] == max_value].index[0]
        return max_value, row_number

    def get_min_val_for_param(self, param):
        if not self.check_if_param_exists(param):
            return None
        min_value = self.df[param].min()
        # get the row number of the minimum value
        row_number = self.df.loc[self.df[param] == min_value].index[0]
        return min_value, row_number

    def take_deriv_for_param(self, param):
        if not self.check_if_param_exists(param):
            return None
        deriv = self.df[param].diff()
        return deriv

    def get_param_values(self, param):
        if not self.check_if_param_exists(param):
            return None
        vals = self.df[param].values
        return vals

    def magic_equation(self, gbw, cload, show_plot=False, new_plot=True, ax1=None, fig1=None, color="blue", legend_str=""):
        legend_str = "PDK: " + self.pdk + ", L: " + str(self.length) + ", corner: " + self.corner_name
        graph_data_x = []
        graph_data_y = []
        #graph = show_plot
        min_ids = 1000000000
        kgm_col  = self.df["kgm"]
        cgg_col = self.df["cgg"]
        kcgd_col = self.df["kcgd"]
        ids_col = self.df["ids"]
        #print(kcgd_col)
        #print(self.df)
        kgm_opt = 0
        for i in range(len(kgm_col)):
            kcgd = kcgd_col[i]
            #cgg = cgg_col[i]
            kgm = kgm_col[i]
            strong_inv = 2*math.pi*gbw*cload/kgm
            #weak_inv = (1 - (2*math.pi*(kcgd/kgm)))*kgm
            weak_inv = 1/(1 - (2*math.pi*gbw*kcgd)/kgm)
            ids = strong_inv*weak_inv
            #if show_plot:
            if ids >= 0:
                graph_data_y.append(ids)
                graph_data_x.append(kgm)
            if ids <= min_ids and ids > 0:
                min_ids = ids
                kgm_opt = kgm
        if show_plot:
            if new_plot:
                fig1, ax1 = plt.subplots()
                plt.plot(graph_data_x, graph_data_y, color=color, label=legend_str)
                if show_plot == True:
                    plt.show()
                #plt.savefig("magic_equation.png")
            else:
                ax1.plot(graph_data_x, graph_data_y, color=color, label=legend_str)
            ax1.set_xlabel("kgm")
            ax1.set_ylabel("id")
            ax1.set_title(self.pdk + " GBW = " + str(gbw) + " CLoad = " + str(cload))
            legend = ax1.legend()
            #legend = ax1.legend(bbox_to_anchor=(1.0, 0.5), loc="center left", fontsize='small')
        return min_ids, kgm_opt, ax1, fig1

    def evaluate_magic_function(self, gbw, cload, kgm):
        min_ids = 1000000000
        kgm_col  = self.df["kgm"]
        cgg_col = self.df["cgg"]
        kcgd_col = self.df["kcgd"]
        closest_kgm, index = self.get_closest_param_in_df("kgm", kgm)
        kcgd = kcgd_col[index]
        kgm = kgm_col[index]
        strong_inv = 2*math.pi*gbw*cload/kgm
        weak_inv = 1/(1 - (2*math.pi*gbw*kcgd)/kgm)
        ids = strong_inv*weak_inv
        return ids


    def plot_processes_params(self, param1, param2, norm_type="", show_plot=True, new_plot=True, fig1=None, ax1=None, color=None, legend_str=None):
        color_list = ['r-', 'b-', 'g-', 'c-', 'm-', 'y-', 'k-']
        color_list_length = len(color_list)
        color_index = 0
        if new_plot == True:
            fig1, ax1 = plt.subplots()
        lines = []
        #for process in tech_list:
        #vdda = self.vdda_dictionary[process]
        #half_vdda = str(vdda/2)

        #for length in self.lookup_tables[process][fet_type]:
        #lookup_table_for_length = self.lookup_tables[process][fet_type][length]
        length = self.length
        steps_counter = 0
        steps_stop = 0
        #if(fet_type == "nfet"):
        #    steps_stop = 2
        #else:
        #    steps_stop = 6
        params1_all = self.df[param1]
        params2_all = self.df[param2]
        kgm_col = self.df["kgm"]
        params1 = []
        params2 = []
        for i in range(len(params1_all)):
            kgm_col_i = kgm_col[i]
            if kgm_col_i > 0.5 and kgm_col_i < 40:
                params1.append(params1_all[i])
                params2.append(params2_all[i])
        col1 = []
        #for item in col1:
            #vgs = float(vgs_str)
            #half_vdda=self.get_bucket_for_vds_measurement(tech=process, fet_type=fet_type, vgs=vgs_str,l=length, vds_target=half_vdda)
            #if(steps_counter > steps_stop):
                #param_one = lookup_table_for_length[vgs_str][half_vdda]["0.0"][param1]
                #param_two = lookup_table_for_length[vgs_str][half_vdda]["0.0"][param2]
                #params1.append(param_one)
                #params2.append(param_two)
            #steps_counter = steps_counter + 1
        #if(legend_str == None):
        #    legend_str = "L=" + str(length) + "um " + self.corner_name
        params1_normalized = []
        params2_normalized = []
        params1_max = 0
        for num in params1:
            if num >= params1_max:
                params1_max = num
        params1_min = params1_max
        for num in params1:
            if num <= params1_min:
                params1_min = num
        params2_max = 0
        for num in params2:
            if num >= params2_max:
                params2_max = num
        params2_min = params2_max
        for num in params2:
            if num <= params2_min:
                params2_min = num

        for num in params1:
            params1_normalized.append((num - params1_min) / (params1_max - params1_min))
        for num in params2:
            params2_normalized.append((num - params2_min) / (params2_max - params2_min))
        color_string = ""
        if color == None:
            color = color_list[color_index]
        if (norm_type == "xnorm"):
            ax1.plot(params1_normalized, params2, color, label=legend_str)
            lines.append(params1_normalized)
            lines.append(params2)
        elif (norm_type == "ynorm"):
            ax1.plot(params1, params2_normalized, color, label=legend_str)
            lines.append(params1)
            lines.append(params2_normalized)
        elif (norm_type == "norm"):
            ax1.plot(params1_normalized, params2_normalized, color, label=legend_str)
            lines.append(params1_normalized)
            lines.append(params2_normalized)
        else:
            ax1.plot(params1, params2, color, label=legend_str)
            lines.append(params1)
            lines.append(params2)
        if(color_index == color_list_length - 1):
            color_index = 0
        else:
            color_index = color_index + 1

        ax1.set_xlabel(param1)
        ax1.set_ylabel(param2)
        graph_title_string = self.pdk + " " + param2 + " vs " + param1
        ax1.set_title(graph_title_string)
        plt.grid(True)
        legend = ax1.legend(bbox_to_anchor=(1.0, 0.5), loc="center left", fontsize='small')
        lined = {}
        for legline, origline in zip(legend.get_lines(), lines):
            legline.set_picker(True)
            lined[legline] = origline
        #fig1.canvas.mpl_connect('pick_event', self.on_pick)
        plt.subplots_adjust(right=0.7)
        if(show_plot == True):
            plt.show()
        return((fig1, ax1))