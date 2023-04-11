
import sys, os, getpass, shutil, operator, collections, copy, re, math
sys.path.append('/home/aadair/Documents/GradSchoolGeneral/LCAS/ICU')
from c_id_release import *


#Design function for Krummenacher OTA

def krummenechar_ota(av, bw, cload, cid_corner):
    gbw = bw*av*2*math.pi

    kcgs = cid_corner.lookup(param1="kgm", param2="kcgs", param1_val=15)
    min_ids, kgm_opt = cid_corner.magic_equation(gbw=gbw, cload=cload)
    gm = kgm_opt*min_ids
    i_kgm = cid_corner.lookup(param1="kgm", param2="ids", param1_val=kgm_opt)
    w  = cid_corner.lookup(param1="kgm", param2="W", param1_val=kgm_opt)
    iden = i_kgm/w
    w = min_ids/iden
    ro_1 = cid_corner.lookup(param1="kgm", param2="ro", param1_val=kgm_opt)
    g_load = gm/av - 1/ro_1
    r_load = 1/g_load
    #This lookup needs to be for p type device
    kgm_2 = cid_corner.lookup(param1="ro", param2="kgm", param1_val=r_load)
    print(str(min_ids) + " " + str(kgm_opt))
    print("Hello Finland")
    print("EXITING")


    # Instantiate Corner Lookup
cid_test_corner = CIDCorner(corner_name="tt28",
                                lut_csv="/home/aadair/Documents/GradSchoolGeneral/LCAS/ICU/UU_github_release/lookup_tables/tsmc_n_lvt_100n_27c_tt.csv",
                                vdd=0.9)

# Choose Target Length
target_l = 80e-9

# Get Closest Length Available in LUT
#l = cid_test_corner.get_bucket_for_length("nfet", target_l)

# set specifications of amplifier
# noise to be added, all fixed length devices for now
av = 225
bw = 2e06
cload = 500e-15

transistor_sizes = krummenechar_ota(av, bw, cload, cid_test_corner)