import sys, os, getpass, shutil, operator, collections, copy, re, math

sys.path.append('/home/aadair/Documents/GradSchoolGeneral/LCAS/ICU')
from cid import *


# Design function for Krummenacher OTA

def krummenechar_ota_stage1(av, bw, cload, cid_corner):
    gbw = bw * av * 2 * math.pi

    ids_min, kgm_opt = cid_corner.magic_equation(gbw=gbw, cload=cload, graph=True, new_plot=True)
    gm = kgm_opt * ids_min
    iden_input = cid_corner.lookup(param1="kgm", param2="iden", param1_val=kgm_opt)
    width_input = ids_min / iden_input
    ro_1 = cid_corner.lookup(param1="kgm", param2="ro", param1_val=kgm_opt)
    g_load = gm / av - 1 / ro_1
    r_load = 1 / g_load
    # This lookup needs to be for p type device
    kgm_load = cid_corner.lookup(param1="ro", param2="kgm", param1_val=r_load)
    iden_load = cid_corner.lookup(param1="kgm", param2="iden", param1_val=kgm_load)
    width_load = ids_min / iden_load
    print(str(ids_min) + " " + str(kgm_opt))
    kgm_input = kgm_opt
    return width_input, kgm_input, width_load, kgm_load


def krummenechar_ota_stage2(av, bw, cload, cid_corner):
    gbw = bw * av * 2 * math.pi
    ids_min, kgm_opt = cid_corner.magic_equation(gbw=gbw, cload=cload, graph=True, new_plot=True)
    gm = kgm_opt * ids_min
    iden_input = cid_corner.lookup(param1="kgm", param2="iden", param1_val=kgm_opt)
    width_input = ids_min / iden_input
    ro_1 = cid_corner.lookup(param1="kgm", param2="ro", param1_val=kgm_opt)
    g_load = gm / av - 1 / ro_1
    r_load = 1 / g_load
    # This lookup needs to be for p type device
    kgm_load = cid_corner.lookup(param1="ro", param2="kgm", param1_val=r_load)
    iden_load = cid_corner.lookup(param1="kgm", param2="iden", param1_val=kgm_load)
    width_load = ids_min / iden_load
    print(str(ids_min) + " " + str(kgm_opt))
    kgm_input = kgm_opt
    return width_input, kgm_input, width_load, kgm_load

    # Instantiate Corner Lookup


# cid_test_corner = CIDCorner(corner_name="tt28",
#                                lut_csv="/home/aadair/Documents/GradSchoolGeneral/LCAS/ICU/UU_github_release/lookup_tables/tsmc_n_lvt_100n_27c_tt.csv",
#                                vdd=0.9)

lookup_table_dir = "/home/ala1/Documents/CAD_Custom_Scripts/python/AHMA/lookuptables/"

sscold = CIDCorner(corner_name="nsscold_minl",
                   lut_csv=lookup_table_dir + "nfetsscold.csv",
                   vdd=0.9)
ttcold = CIDCorner(corner_name="nttcold_minl",
                   lut_csv=lookup_table_dir + "nfetttcold.csv",
                   vdd=0.9)
ffcold = CIDCorner(corner_name="nffcold_minl",
                   lut_csv=lookup_table_dir + "nfetffcold.csv",
                   vdd=0.9)
ssroom = CIDCorner(corner_name="nssroom_minl",
                   lut_csv=lookup_table_dir + "nfetssroom.csv",
                   vdd=0.9)
ttroom = CIDCorner(corner_name="nttroom_minl",
                   lut_csv=lookup_table_dir + "nfetttroom.csv",
                   vdd=0.9)
ffroom = CIDCorner(corner_name="nffroom_minl",
                   lut_csv=lookup_table_dir + "nfetffroom.csv",
                   vdd=0.9)
sshot = CIDCorner(corner_name="nsshot_minl",
                  lut_csv=lookup_table_dir + "nfetsshot.csv",
                  vdd=0.9)

# tthot = CIDCorner(corner_name="ntthot_minl",
#                                lut_csv=lookup_table_dir +"nfettthot.csv",
#                                vdd=0.9)
ffhot = CIDCorner(corner_name="nffhot_minl",
                  lut_csv=lookup_table_dir + "nfetffhot.csv",
                  vdd=0.9)

fig1, ax1 = plt.subplots()

# Choose Target Length
# Get Closest Length Available in LUT
# l = cid_test_corner.get_bucket_for_length("nfet", target_l)

# set specifications of amplifier
# noise to be added, all fixed length devices for now
av = 225
bw = 2e06
cload1 = 500e-15
cload2 = 500e-15
gbw = bw * av * 2 * math.pi


color_list = ['red', 'blue', 'green', 'yellow', 'magenta', 'black', 'purple']
corner_list = [sscold, ttcold, ffcold, ssroom, ttroom, ffroom, sshot, ffhot]
color_index = 0
cid_test_corner = corner_list[0]

cid_test_corner.plot_processes_params("kgm", "kcgs", show_plot=True)
cid_test_corner.plot_processes_params("kgm", "dkcgs", show_plot=True)

for i in range(len(corner_list)):
    if color_index >= len(color_list):
        color_index = 0
    corner = corner_list[i]
    corner.magic_equation(gbw=gbw, cload=cload1, show_plot=True, new_plot=False,
                          fig1=fig1, ax1=ax1, color=color_list[color_index])
    color_index = color_index + 1

plt.show()

w_in1, kgm_in1, w_load1, kgm_load1 = krummenechar_ota_stage1(av, bw, cload, corner_list)
w_in2, kgm_in2, w_load2, kgm_load2 = krummenechar_ota_stage2(av, bw, cload, corner_list)

cid_test_corner.plot_processes_params("kgm", "gm", show_plot=True)
cid_test_corner.plot_processes_params("kgm", "ft", show_plot=True)
cid_test_corner.plot_processes_params("kgm", "gmro", show_plot=True)
cid_test_corner.plot_processes_params("kgm", "iden", show_plot=True)
