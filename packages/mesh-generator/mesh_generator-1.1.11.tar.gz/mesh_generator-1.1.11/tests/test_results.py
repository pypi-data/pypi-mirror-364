"""
Unittest adjusted mesh and legacy mesh dictionary results.
Used for unit testing in test.unit_test.py.
Update this file every time you add an extra test to the unittest collection or adjust the src mesh functions.
Latest update: June 16th, 2020. (Opal)
"""

import numpy

theta_test_1_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.4,
            "ds0": numpy.Infinity,
            "ds1": 0.04,
            "var_ds_ratio": 1.06,
            "ratio": 0.9433962264150942
        },
        {
            "s0": 0.4,
            "s1": 1.1,
            "ds0": 0.04,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 1.1,
            "s1": 1.4,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 1.4,
            "s1": 1.9,
            "ds0": 0.01,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 1.9,
            "s1": 2.8,
            "ds0": 0.02,
            "ds1": 0.04,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 2.8,
            "s1": 3.141592653589793,
            "ds0": 0.04,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.06,
            "ratio": 1.06
        }
    ]
}

theta_test_1_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.4,
            "ratio": 0.5583947769151176,
            "num_points": 10
        },
        {
            "s0": 0.4,
            "s1": 1.1,
            "ratio": 0.32522615237693164,
            "num_points": 38
        },
        {
            "s0": 1.1,
            "s1": 1.4,
            "ratio": 1.0,
            "num_points": 30
        },
        {
            "s0": 1.4,
            "s1": 1.749403232925598,
            "ratio": 2.0,
            "num_points": 24
        },
        {
            "s0": 1.749403232925598,
            "s1": 1.9,
            "ratio": 1.0,
            "num_points": 8
        },
        {
            "s0": 1.9,
            "s1": 2.5988064658511965,
            "ratio": 2.0,
            "num_points": 24
        },
        {
            "s0": 2.5988064658511965,
            "s1": 2.8,
            "ratio": 1.0,
            "num_points": 6
        },
        {
            "s0": 2.8,
            "s1": 3.141592653589793,
            "ratio": 1.5036302589913606,
            "num_points": 7
        }
    ]
}
theta_test_2_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.1,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.873363,
            "ds0": numpy.Infinity,
            "ds1": 0.02,
            "var_ds_ratio": 1.1,
            "ratio": 0.9090909090909091
        },
        {
            "s0": 0.873363,
            "s1": 1.32374,
            "ds0": 0.02,
            "ds1": 0.002,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 1.32374,
            "s1": 1.36787,
            "ds0": 0.002,
            "ds1": 0.0005,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 1.36787,
            "s1": 1.40546,
            "ds0": 0.0005,
            "ds1": 0.0005,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 1.40546,
            "s1": 1.43835,
            "ds0": 0.0005,
            "ds1": 0.002,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 1.43835,
            "s1": 1.79756,
            "ds0": 0.002,
            "ds1": 0.005,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 1.79756,
            "s1": 1.91009,
            "ds0": 0.005,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 1.91009,
            "s1": 2.12372,
            "ds0": 0.01,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 2.12372,
            "s1": 3.141592653589793,
            "ds0": 0.02,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.1,
            "ratio": 1.1
        }
    ]
}

theta_test_2_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.1,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.873363,
            "ratio": 0.14864362802414358,
            "num_points": 20
        },
        {
            "s0": 0.873363,
            "s1": 1.32374,
            "ratio": 0.11904737434049815,
            "num_points": 72
        },
        {
            "s0": 1.32374,
            "s1": 1.36787,
            "ratio": 0.2723717824774795,
            "num_points": 44
        },
        {
            "s0": 1.36787,
            "s1": 1.40546,
            "ratio": 1.0,
            "num_points": 76
        },
        {
            "s0": 1.40546,
            "s1": 1.4564075147841873,
            "ratio": 4.0,
            "num_points": 47
        },
        {
            "s0": 1.4564075147841873,
            "s1": 1.5579055614957698,
            "ratio": 2.5,
            "num_points": 31
        },
        {
            "s0": 1.5579055614957698,
            "s1": 1.79756,
            "ratio": 1.0,
            "num_points": 48
        },
        {
            "s0": 1.79756,
            "s1": 1.972261616462799,
            "ratio": 2.0,
            "num_points": 24
        },
        {
            "s0": 1.972261616462799,
            "s1": 2.12372,
            "ratio": 1.4685337134515648,
            "num_points": 13
        },
        {
            "s0": 2.12372,
            "s1": 3.141592653589793,
            "ratio": 8.14027493868399,
            "num_points": 22
        }
    ]
}

theta_test_3_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.0,
            "ds0": numpy.Infinity,
            "ds1": 0.04,
            "var_ds_ratio": 1.06,
            "ratio": 0.9433962264150942
        },
        {
            "s0": 1.0,
            "s1": 1.5,
            "ds0": 0.04,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 1.5,
            "s1": 2.0,
            "ds0": 0.02,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 2.0,
            "s1": 3.141592653589793,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        }
    ]
}

theta_test_3_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.0,
            "ratio": 0.3713644185969563,
            "num_points": 17
        },
        {
            "s0": 1.0,
            "s1": 1.5,
            "ratio": 0.570286026811925,
            "num_points": 19
        },
        {
            "s0": 1.5,
            "s1": 1.650596767074402,
            "ratio": 1.0,
            "num_points": 8
        },
        {
            "s0": 1.650596767074402,
            "s1": 2.0,
            "ratio": 0.5,
            "num_points": 24
        },
        {
            "s0": 2.0,
            "s1": 3.141592653589793,
            "ratio": 1.0,
            "num_points": 115
        }
    ]
}

theta_test_4_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.5,
            "ds0": numpy.Infinity,
            "ds1": 0.02,
            "var_ds_ratio": 1.06,
            "ratio": 0.9433962264150942
        },
        {
            "s0": 0.5,
            "s1": 0.7,
            "ds0": 0.02,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 0.7,
            "s1": 0.9615517727939964,
            "ds0": 0.02,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0582810139630818,
            "ratio": 1.0582810139630818
        },
        {
            "s0": 0.9615517727939964,
            "s1": 1.0,
            "ds0": numpy.Infinity,
            "ds1": 0.033,
            "var_ds_ratio": 1.0333871376793413,
            "ratio": 0.9676915490216782
        },
        {
            "s0": 1.0,
            "s1": 1.5,
            "ds0": 0.033,
            "ds1": 0.033,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 1.5,
            "s1": 1.75,
            "ds0": 0.033,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0536220287124196,
            "ratio": 1.0536220287124196
        },
        {
            "s0": 1.75,
            "s1": 2.0,
            "ds0": numpy.Infinity,
            "ds1": 0.033,
            "var_ds_ratio": 1.0536220287124196,
            "ratio": 0.9491069593733262
        },
        {
            "s0": 2.0,
            "s1": 2.5,
            "ds0": 0.033,
            "ds1": 0.033,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 2.5,
            "s1": 3.141592653589793,
            "ds0": 0.033,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.06,
            "ratio": 1.06
        }
    ]
}

theta_test_4_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.5,
            "ratio": 0.3936462837127737,
            "num_points": 16
        },
        {
            "s0": 0.5,
            "s1": 0.7,
            "ratio": 1.0,
            "num_points": 10
        },
        {
            "s0": 0.7,
            "s1": 0.9615517727939964,
            "ratio": 1.7620168109298184,
            "num_points": 10
        },
        {
            "s0": 0.9615517727939964,
            "s1": 1.0,
            "ratio": 0.9364269340479751,
            "num_points": 2
        },
        {
            "s0": 1.0,
            "s1": 1.5,
            "ratio": 1.0,
            "num_points": 16
        },
        {
            "s0": 1.5,
            "s1": 1.75,
            "ratio": 1.4414311221513314,
            "num_points": 7
        },
        {
            "s0": 1.75,
            "s1": 2.0,
            "ratio": 0.6937549665970187,
            "num_points": 7
        },
        {
            "s0": 2.0,
            "s1": 2.5,
            "ratio": 1.0,
            "num_points": 16
        },
        {
            "s0": 2.5,
            "s1": 3.141592653589793,
            "ratio": 2.1329282601456847,
            "num_points": 13
        }
    ]
}

theta_test_5_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.0,
            "ds0": numpy.Infinity,
            "ds1": 0.055,
            "var_ds_ratio": 1.06,
            "ratio": 0.9433962264150942
        },
        {
            "s0": 1.0,
            "s1": 1.5,
            "ds0": 0.055,
            "ds1": 0.055,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 1.5,
            "s1": 1.5783818880092364,
            "ds0": 0.055,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0406923135454675,
            "ratio": 1.0406923135454675
        },
        {
            "s0": 1.5783818880092364,
            "s1": 2.0,
            "ds0": numpy.Infinity,
            "ds1": 0.035,
            "var_ds_ratio": 1.054614975233193,
            "ratio": 0.9482133513028138
        },
        {
            "s0": 2.0,
            "s1": 2.5,
            "ds0": 0.035,
            "ds1": 0.035,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 2.5,
            "s1": 3.141592653589793,
            "ds0": 0.035,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.06,
            "ratio": 1.06
        }
    ]
}

theta_test_5_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.0,
            "ratio": 0.468839022242453,
            "num_points": 13
        },
        {
            "s0": 1.0,
            "s1": 1.5,
            "ratio": 1.0,
            "num_points": 10
        },
        {
            "s0": 1.5,
            "s1": 1.5783818880092364,
            "ratio": 1.0830404914726177,
            "num_points": 2
        },
        {
            "s0": 1.5783818880092364,
            "s1": 2.0,
            "ratio": 0.5875714171114402,
            "num_points": 10
        },
        {
            "s0": 2.0,
            "s1": 2.5,
            "ratio": 1.0,
            "num_points": 15
        },
        {
            "s0": 2.5,
            "s1": 3.141592653589793,
            "ratio": 2.1329282601456847,
            "num_points": 13
        }
    ]
}

theta_test_6_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.09,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.0,
            "ds0": numpy.Infinity,
            "ds1": 0.07,
            "var_ds_ratio": 1.09,
            "ratio": 0.9174311926605504
        },
        {
            "s0": 1.0,
            "s1": 1.5,
            "ds0": 0.07,
            "ds1": 0.05308884812052621,
            "var_ds_ratio": 1.09,
            "ratio": 0.9174311926605504
        },
        {
            "s0": 1.5,
            "s1": 2.0,
            "ds0": numpy.Infinity,
            "ds1": 0.01,
            "var_ds_ratio": 1.0870516138252697,
            "ratio": 0.9199195210989658
        },
        {
            "s0": 2.0,
            "s1": 2.5,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 2.5,
            "s1": 3.141592653589793,
            "ds0": 0.01,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.09,
            "ratio": 1.09
        }
    ]
}

theta_test_6_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.09,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.0,
            "ratio": 0.4224108068956889,
            "num_points": 10
        },
        {
            "s0": 1.0,
            "s1": 1.2464495509212417,
            "ratio": 1.0,
            "num_points": 4
        },
        {
            "s0": 1.2464495509212417,
            "s1": 1.5,
            "ratio": 0.7584121160075172,
            "num_points": 4
        },
        {
            "s0": 1.5,
            "s1": 2.0,
            "ratio": 0.18836347658734778,
            "num_points": 20
        },
        {
            "s0": 2.0,
            "s1": 2.5,
            "ratio": 1.0,
            "num_points": 50
        },
        {
            "s0": 2.5,
            "s1": 3.141592653589793,
            "ratio": 6.6586004331974,
            "num_points": 22
        }
    ]
}

theta_test_7_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.4,
            "ds0": 0.03,
            "ds1": 0.03,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 0.4,
            "s1": 0.6141909440046182,
            "ds0": 0.03,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0596888254261791,
            "ratio": 1.0596888254261791
        },
        {
            "s0": 0.6141909440046182,
            "s1": 1.0,
            "ds0": numpy.Infinity,
            "ds1": 0.02,
            "var_ds_ratio": 1.0596593158960013,
            "ratio": 0.9436995315371186
        },
        {
            "s0": 1.0,
            "s1": 1.2,
            "ds0": 0.02,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 1.2,
            "s1": 1.4358090559953818,
            "ds0": 0.02,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0598282462614539,
            "ratio": 1.0598282462614539
        },
        {
            "s0": 1.4358090559953818,
            "s1": 1.5,
            "ds0": numpy.Infinity,
            "ds1": 0.03,
            "var_ds_ratio": 1.0399426355049504,
            "ratio": 0.9615915011643349
        },
        {
            "s0": 1.5,
            "s1": 2.4,
            "ds0": 0.03,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 2.4,
            "s1": 3.141592653589793,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        }
    ]
}

theta_test_7_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.4,
            "ratio": 1.0,
            "num_points": 14
        },
        {
            "s0": 0.4,
            "s1": 0.6141909440046182,
            "ratio": 1.4160224145730922,
            "num_points": 6
        },
        {
            "s0": 0.6141909440046182,
            "s1": 1.0,
            "ratio": 0.47080234027768286,
            "num_points": 13
        },
        {
            "s0": 1.0,
            "s1": 1.2,
            "ratio": 1.0,
            "num_points": 10
        },
        {
            "s0": 1.2,
            "s1": 1.4358090559953818,
            "ratio": 1.6870168109298171,
            "num_points": 9
        },
        {
            "s0": 1.4358090559953818,
            "s1": 1.5,
            "ratio": 0.8891434811329817,
            "num_points": 3
        },
        {
            "s0": 1.5,
            "s1": 1.6980826959009994,
            "ratio": 1.0,
            "num_points": 7
        },
        {
            "s0": 1.6980826959009994,
            "s1": 2.4,
            "ratio": 0.33333333333333337,
            "num_points": 38
        },
        {
            "s0": 2.4,
            "s1": 3.141592653589793,
            "ratio": 1.0,
            "num_points": 75
        }
    ]
}

theta_test_8_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.2,
            "ds0": 0.2,
            "ds1": 0.2,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 1.2,
            "s1": 1.5999999999999999,
            "ds0": 0.2,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0566635302914318,
            "ratio": 1.0566635302914318
        },
        {
            "s0": 1.5999999999999999,
            "s1": 2.0,
            "ds0": numpy.Infinity,
            "ds1": 0.2,
            "var_ds_ratio": 1.0566635302914318,
            "ratio": 0.9463750487576649
        },
        {
            "s0": 2.0,
            "s1": 3.141592653589793,
            "ds0": 0.2,
            "ds1": 0.2,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        }
    ]
}

theta_test_8_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.2,
            "ratio": 1.0,
            "num_points": 6
        },
        {
            "s0": 1.2,
            "s1": 1.5999999999999999,
            "ratio": 1.1165378162479516,
            "num_points": 2
        },
        {
            "s0": 1.5999999999999999,
            "s1": 2.0,
            "ratio": 0.8956257329110726,
            "num_points": 2
        },
        {
            "s0": 2.0,
            "s1": 3.141592653589793,
            "ratio": 1.0,
            "num_points": 6
        }
    ]
}

theta_test_9_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.1,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.8473725097896048,
            "ds0": numpy.Infinity,
            "ds1": 0.02,
            "var_ds_ratio": 1.1,
            "ratio": 0.9090909090909091
        },
        {
            "s0": 0.8473725097896048,
            "s1": 1.1356989345533366,
            "ds0": 0.02,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 1.1356989345533366,
            "s1": 1.3532502198056797,
            "ds0": 0.01,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 1.3532502198056797,
            "s1": 1.4283274775004602,
            "ds0": 0.001,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 1.4283274775004602,
            "s1": 1.5916809800055658,
            "ds0": 0.001,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 1.5916809800055658,
            "s1": 2.06673071910115,
            "ds0": 0.01,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 2.06673071910115,
            "s1": 3.141592653589793,
            "ds0": 0.02,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.1,
            "ratio": 1.1
        }
    ]
}

theta_test_9_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.1,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.8473725097896048,
            "ratio": 0.16350799082655795,
            "num_points": 19
        },
        {
            "s0": 0.8473725097896048,
            "s1": 1.1356989345533366,
            "ratio": 0.4636947274385045,
            "num_points": 26
        },
        {
            "s0": 1.1356989345533366,
            "s1": 1.3532502198056797,
            "ratio": 0.1339888686275986,
            "num_points": 68
        },
        {
            "s0": 1.3532502198056797,
            "s1": 1.4283274775004602,
            "ratio": 1.0,
            "num_points": 76
        },
        {
            "s0": 1.4283274775004602,
            "s1": 1.733822261566491,
            "ratio": 10.0,
            "num_points": 78
        },
        {
            "s0": 1.733822261566491,
            "s1": 2.06673071910115,
            "ratio": 2.032794106460404,
            "num_points": 24
        },
        {
            "s0": 2.06673071910115,
            "s1": 3.141592653589793,
            "ratio": 6.115909044841464,
            "num_points": 19
        }
    ]
}

theta_test_10_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.1,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.3,
            "ds0": 0.08,
            "ds1": 0.001,
            "var_ds_ratio": 1.1,
            "ratio": 0.9090909090909091
        },
        {
            "s0": 1.3,
            "s1": 1.42,
            "ds0": 0.001,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 1.42,
            "s1": 3.141592653589793,
            "ds0": 0.001,
            "ds1": 0.08,
            "var_ds_ratio": 1.1,
            "ratio": 1.1
        }
    ]
}

theta_test_10_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.1,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.4692437028639339,
            "ratio": 1.0,
            "num_points": 6
        },
        {
            "s0": 0.4692437028639339,
            "s1": 1.3,
            "ratio": 0.0125,
            "num_points": 46
        },
        {
            "s0": 1.3,
            "s1": 1.42,
            "ratio": 1.0,
            "num_points": 120
        },
        {
            "s0": 1.42,
            "s1": 2.250756297136066,
            "ratio": 80.0,
            "num_points": 46
        },
        {
            "s0": 2.250756297136066,
            "s1": 3.141592653589793,
            "ratio": 1.0,
            "num_points": 12
        }
    ]
}

theta_test_11_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 3.141592653589793,
            "ds0": 0.03,
            "ds1": 0.03,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        }
    ]
}

theta_test_11_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 3.141592653589793,
            "ratio": 1.0,
            "num_points": 105
        }
    ]
}

theta_test_12_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.02,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.3953275896083537,
            "ds0": numpy.Infinity,
            "ds1": 0.01,
            "var_ds_ratio": 1.02,
            "ratio": 0.9803921568627451
        },
        {
            "s0": 0.3953275896083537,
            "s1": 0.7317766020409957,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.04,
            "ratio": 1.0
        },
        {
            "s0": 0.7317766020409957,
            "s1": 1.2364501206899585,
            "ds0": 0.01,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0199926635419443,
            "ratio": 1.0199926635419443
        },
        {
            "s0": 1.2364501206899585,
            "s1": 1.6906562874740247,
            "ds0": 0.019993861596057025,
            "ds1": 0.07,
            "var_ds_ratio": 1.04,
            "ratio": 1.04
        },
        {
            "s0": 1.6906562874740247,
            "s1": 1.8168246671362658,
            "ds0": 0.07,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0176897183538118,
            "ratio": 1.0176897183538118
        },
        {
            "s0": 1.8168246671362658,
            "s1": 2.61589107166379,
            "ds0": 0.07249846539901428,
            "ds1": 0.09,
            "var_ds_ratio": 1.04,
            "ratio": 1.04
        },
        {
            "s0": 2.61589107166379,
            "s1": 3.141592653589793,
            "ds0": 0.09,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.02,
            "ratio": 1.02
        }
    ]
}

theta_test_12_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 3.141592653589793,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.02,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.3953275896083537,
            "ratio": 0.5520708889799112,
            "num_points": 30
        },
        {
            "s0": 0.3953275896083537,
            "s1": 0.7317766020409957,
            "ratio": 1.0,
            "num_points": 34
        },
        {
            "s0": 0.7317766020409957,
            "s1": 1.2364501206899585,
            "ratio": 1.9993861596057037,
            "num_points": 35
        },
        {
            "s0": 1.2364501206899585,
            "s1": 1.6906562874740247,
            "ratio": 1.947900495556281,
            "num_points": 17
        },
        {
            "s0": 1.6906562874740247,
            "s1": 1.8168246671362658,
            "ratio": 1.0726586704514425,
            "num_points": 4
        },
        {
            "s0": 1.8168246671362658,
            "s1": 2.61589107166379,
            "ratio": 1.8009435055069165,
            "num_points": 15
        },
        {
            "s0": 2.61589107166379,
            "s1": 3.141592653589793,
            "ratio": 1.14868566764928,
            "num_points": 7
        }
    ]
}

theta_test_13_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.09,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.4,
      "ds0": 0.03,
      "ds1": 0.03,
      "var_ds_ratio": 1.04,
      "ratio": 1.0
    },
    {
      "s0": 0.4,
      "s1": 0.7500000000000001,
      "ds0": 0.03,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0383962012441699,
      "ratio": 1.0383962012441699
    },
    {
      "s0": 0.7500000000000001,
      "s1": 1.1,
      "ds0": numpy.Infinity,
      "ds1": 0.03,
      "var_ds_ratio": 1.0383962012441699,
      "ratio": 0.9630235538244796
    },
    {
      "s0": 1.1,
      "s1": 1.8,
      "ds0": 0.03,
      "ds1": 0.03,
      "var_ds_ratio": 1.04,
      "ratio": 1.0
    },
    {
      "s0": 1.8,
      "s1": 1.9225163415448583,
      "ds0": 0.03,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0378405900938028,
      "ratio": 1.0378405900938028
    },
    {
      "s0": 1.9225163415448583,
      "s1": 2.3,
      "ds0": numpy.Infinity,
      "ds1": 0.02,
      "var_ds_ratio": 1.0376261888871385,
      "ratio": 0.9637382042877186
    },
    {
      "s0": 2.3,
      "s1": 2.8,
      "ds0": 0.02,
      "ds1": 0.02,
      "var_ds_ratio": 1.04,
      "ratio": 1.0
    },
    {
      "s0": 2.8,
      "s1": 3.141592653589793,
      "ds0": 0.02,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.09,
      "ratio": 1.09
    }
  ]
}


theta_test_13_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.09,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.4,
      "ratio": 1.0,
      "num_points": 14
    },
    {
      "s0": 0.4,
      "s1": 0.7500000000000001,
      "ratio": 1.4575749867882828,
      "num_points": 10
    },
    {
      "s0": 0.7500000000000001,
      "s1": 1.1,
      "ratio": 0.6860710488751358,
      "num_points": 10
    },
    {
      "s0": 1.1,
      "s1": 1.8,
      "ratio": 1.0,
      "num_points": 24
    },
    {
      "s0": 1.8,
      "s1": 1.9225163415448583,
      "ratio": 1.1601726096106777,
      "num_points": 4
    },
    {
      "s0": 1.9225163415448583,
      "s1": 2.3,
      "ratio": 0.5746271383620938,
      "num_points": 15
    },
    {
      "s0": 2.3,
      "s1": 2.8,
      "ratio": 1.0,
      "num_points": 25
    },
    {
      "s0": 2.8,
      "s1": 3.141592653589793,
      "ratio": 2.58042640530541,
      "num_points": 11
    }
  ]
}


theta_test_14_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.02,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.7317766020409957,
      "ds0": 0.09,
      "ds1": 0.07999386159605702,
      "var_ds_ratio": 1.04,
      "ratio": 0.9615384615384615
    },
    {
      "s0": 0.7317766020409957,
      "s1": 1.2364501206899585,
      "ds0": numpy.Infinity,
      "ds1": 0.07,
      "var_ds_ratio": 1.0192478480176306,
      "ratio": 0.9811156353628154
    },
    {
      "s0": 1.2364501206899585,
      "s1": 1.6906562874740247,
      "ds0": 0.07,
      "ds1": 0.012498465399014263,
      "var_ds_ratio": 1.04,
      "ratio": 0.9615384615384615
    },
    {
      "s0": 1.6906562874740247,
      "s1": 1.8168246671362658,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.018758841839532,
      "ratio": 0.9815865727303433
    },
    {
      "s0": 1.8168246671362658,
      "s1": 2.61589107166379,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.04,
      "ratio": 1.0
    },
    {
      "s0": 2.61589107166379,
      "s1": 3.141592653589793,
      "ds0": 0.01,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.02,
      "ratio": 1.02
    }
  ]
}


theta_test_14_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.02,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.7317766020409957,
      "ratio": 0.5774750828218054,
      "num_points": 14
    },
    {
      "s0": 0.7317766020409957,
      "s1": 1.2364501206899585,
      "ratio": 0.7512819457029271,
      "num_points": 15
    },
    {
      "s0": 1.2364501206899585,
      "s1": 1.6906562874740247,
      "ratio": 0.4057263333178869,
      "num_points": 23
    },
    {
      "s0": 1.6906562874740247,
      "s1": 1.8168246671362658,
      "ratio": 0.8000982265221682,
      "num_points": 12
    },
    {
      "s0": 1.8168246671362658,
      "s1": 2.61589107166379,
      "ratio": 1.0,
      "num_points": 80
    },
    {
      "s0": 2.61589107166379,
      "s1": 3.141592653589793,
      "ratio": 2.08068509059002,
      "num_points": 37
    }
  ]
}


theta_test_15_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.07,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.73,
      "ds0": 0.06,
      "ds1": 0.03279956478269298,
      "var_ds_ratio": 1.02,
      "ratio": 0.9803921568627451
    },
    {
      "s0": 0.73,
      "s1": 1.2,
      "ds0": numpy.Infinity,
      "ds1": 0.001,
      "var_ds_ratio": 1.0694274054288024,
      "ratio": 0.9350798333048473
    },
    {
      "s0": 1.2,
      "s1": 1.69,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 1.69,
      "s1": 3.141592653589793,
      "ds0": 0.001,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.07,
      "ratio": 1.07
    }
  ]
}

theta_test_15_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.07,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.73,
      "ratio": 0.6864307597702183,
      "num_points": 19
    },
    {
      "s0": 0.73,
      "s1": 1.2,
      "ratio": 0.03048820942062189,
      "num_points": 52
    },
    {
      "s0": 1.2,
      "s1": 1.69,
      "ratio": 1.0,
      "num_points": 490
    },
    {
      "s0": 1.69,
      "s1": 3.141592653589793,
      "ratio": 99.56274975773735,
      "num_points": 68
    }
  ]
}

theta_test_16_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.07,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 1.9,
      "ds0": numpy.Infinity,
      "ds1": 0.001,
      "var_ds_ratio": 1.07,
      "ratio": 0.9345794392523364
    },
    {
      "s0": 1.9,
      "s1": 2.3,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 2.3,
      "s1": 2.5,
      "ds0": 0.001,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0691974954604775,
      "ratio": 1.0691974954604775
    },
    {
      "s0": 2.5,
      "s1": 3.141592653589793,
      "ds0": 0.014531729694762982,
      "ds1": 0.07,
      "var_ds_ratio": 1.02,
      "ratio": 1.02
    }
  ]
}

theta_test_16_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.07,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 1.9,
      "ratio": 0.00766245622889941,
      "num_points": 72
    },
    {
      "s0": 1.9,
      "s1": 2.3,
      "ratio": 1.0,
      "num_points": 400
    },
    {
      "s0": 2.3,
      "s1": 2.5,
      "ratio": 14.531729694763,
      "num_points": 40
    },
    {
      "s0": 2.5,
      "s1": 3.141592653589793,
      "ratio": 1.8845405921011302,
      "num_points": 32
    }
  ]
}

theta_test_17_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.04,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.5193418749836787,
      "ds0": 0.1,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 0.5193418749836787,
      "s1": 1.1164846652654585,
      "ds0": 0.02,
      "ds1": 0.0015,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 1.1164846652654585,
      "s1": 1.242461236299751,
      "ds0": 0.0015,
      "ds1": 0.001,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 1.242461236299751,
      "s1": 1.3403353414879318,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 1.3403353414879318,
      "s1": 1.4469309015938716,
      "ds0": 0.001,
      "ds1": 0.0015,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 1.4469309015938716,
      "s1": 2.009257090100789,
      "ds0": 0.0015,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 2.009257090100789,
      "s1": 3.141592653589793,
      "ds0": 0.02,
      "ds1": 0.1,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    }
  ]
}

theta_test_17_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 3.141592653589793,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.04,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.5193418749836787,
      "ratio": 0.553675754186335,
      "num_points": 20
    },
    {
      "s0": 0.5193418749836787,
      "s1": 1.1164846652654585,
      "ratio": 0.0764119795266582,
      "num_points": 87
    },
    {
      "s0": 1.1164846652654585,
      "s1": 1.2251198798852925,
      "ratio": 1.0,
      "num_points": 73
    },
    {
      "s0": 1.2251198798852925,
      "s1": 1.242461236299751,
      "ratio": 0.6666666666666666,
      "num_points": 14
    },
    {
      "s0": 1.242461236299751,
      "s1": 1.3403353414879318,
      "ratio": 1.0,
      "num_points": 98
    },
    {
      "s0": 1.3403353414879318,
      "s1": 1.3576766979023902,
      "ratio": 1.5,
      "num_points": 14
    },
    {
      "s0": 1.3576766979023902,
      "s1": 1.4469309015938716,
      "ratio": 1.0,
      "num_points": 60
    },
    {
      "s0": 1.4469309015938716,
      "s1": 2.080222553310361,
      "ratio": 13.333333333333334,
      "num_points": 88
    },
    {
      "s0": 2.080222553310361,
      "s1": 3.141592653589793,
      "ratio": 2.575082755685113,
      "num_points": 32
    }
  ]
}



r_test_1_adj = {
    "lower_bnd": 1.0,
    "upper_bnd": 2.5,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.03,
    "segment_list": [
        {
            "s0": 1.0,
            "s1": 1.009,
            "ds0": 0.0003,
            "ds1": 0.0003,
            "var_ds_ratio": 1.02,
            "ratio": 1.0
        },
        {
            "s0": 1.009,
            "s1": 1.0172,
            "ds0": 0.0003,
            "ds1": 0.00075,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 1.0172,
            "s1": 1.1,
            "ds0": 0.00075,
            "ds1": 0.002,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 1.1,
            "s1": 1.4,
            "ds0": 0.002,
            "ds1": 0.005,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 1.4,
            "s1": 2.0,
            "ds0": 0.005,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 2.0,
            "s1": 2.5,
            "ds0": 0.02,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        }
    ]
}

r_test_1_legacy = {
    "lower_bnd": 1.0,
    "upper_bnd": 2.5,
    "periodic": False,
    "phi_shift": 0.0,
    "BG_RATIO": 1.03,
    "segment_list": [
        {
            "s0": 1.0,
            "s1": 1.009,
            "ratio": 1.0,
            "num_points": 30
        },
        {
            "s0": 1.009,
            "s1": 1.0242247070067372,
            "ratio": 2.5000000000000004,
            "num_points": 31
        },
        {
            "s0": 1.0242247070067372,
            "s1": 1.0681686043614185,
            "ratio": 2.6666666666666665,
            "num_points": 34
        },
        {
            "s0": 1.0681686043614185,
            "s1": 1.1,
            "ratio": 1.0,
            "num_points": 16
        },
        {
            "s0": 1.1,
            "s1": 1.2014980467115826,
            "ratio": 2.5,
            "num_points": 31
        },
        {
            "s0": 1.2014980467115826,
            "s1": 1.4,
            "ratio": 1.0,
            "num_points": 40
        },
        {
            "s0": 1.4,
            "s1": 1.9094751478418743,
            "ratio": 4.0,
            "num_points": 47
        },
        {
            "s0": 1.9094751478418743,
            "s1": 2.0,
            "ratio": 1.0,
            "num_points": 5
        },
        {
            "s0": 2.0,
            "s1": 2.5,
            "ratio": 1.7535060530771016,
            "num_points": 19
        }
    ]
}
r_test_2_adj = {
  "lower_bnd": 1.0,
  "upper_bnd": 3.0,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.09,
  "segment_list": [
    {
      "s0": 1.0,
      "s1": 1.2,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 1.2,
      "s1": 1.5,
      "ds0": 0.01,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 1.5,
      "s1": 1.7790098263129142,
      "ds0": 0.02,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0821465867930526,
      "ratio": 1.0821465867930526
    },
    {
      "s0": 1.7790098263129142,
      "s1": 2.0,
      "ds0": numpy.Infinity,
      "ds1": 0.025,
      "var_ds_ratio": 1.084266017791361,
      "ratio": 0.9222828933041635
    },
    {
      "s0": 2.0,
      "s1": 2.5,
      "ds0": 0.025,
      "ds1": 0.025,
      "var_ds_ratio": 1.06,
      "ratio": 1.0
    },
    {
      "s0": 2.5,
      "s1": 3.0,
      "ds0": 0.025,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.09,
      "ratio": 1.09
    }
  ]
}

r_test_2_legacy = {
  "lower_bnd": 1.0,
  "upper_bnd": 3.0,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.09,
  "segment_list": [
    {
      "s0": 1.0,
      "s1": 1.2,
      "ratio": 1.0,
      "num_points": 20
    },
    {
      "s0": 1.2,
      "s1": 1.5,
      "ratio": 1.9161034088607822,
      "num_points": 22
    },
    {
      "s0": 1.5,
      "s1": 1.7869804544876364,
      "ratio": 2.1824072265530807,
      "num_points": 10
    },
    {
      "s0": 1.7869804544876364,
      "s1": 2.0,
      "ratio": 0.5978404196668514,
      "num_points": 7
    },
    {
      "s0": 2.0,
      "s1": 2.5,
      "ratio": 1.0,
      "num_points": 20
    },
    {
      "s0": 2.5,
      "s1": 3.0,
      "ratio": 2.812664781782897,
      "num_points": 12
    }
  ]
}


r_test_3_adj = {
  "lower_bnd": 1.0,
  "upper_bnd": 2.5,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 1.0,
      "s1": 1.02,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 1.02,
      "s1": 1.2,
      "ds0": 0.001,
      "ds1": 0.01,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 1.2,
      "s1": 1.5,
      "ds0": 0.01,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 1.5,
      "s1": 1.792904527997691,
      "ds0": 0.02,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0576939234686642,
      "ratio": 1.0576939234686642
    },
    {
      "s0": 1.792904527997691,
      "s1": 2.0,
      "ds0": numpy.Infinity,
      "ds1": 0.025,
      "var_ds_ratio": 1.0578783448324875,
      "ratio": 0.9452882790207295
    },
    {
      "s0": 2.0,
      "s1": 2.5,
      "ds0": 0.025,
      "ds1": 0.025,
      "var_ds_ratio": 1.06,
      "ratio": 1.0
    }
  ]
}

r_test_3_legacy = {
  "lower_bnd": 1.0,
  "upper_bnd": 2.5,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 1.0,
      "s1": 1.02,
      "ratio": 1.0,
      "num_points": 21
    },
    {
      "s0": 1.02,
      "s1": 1.3254947840660307,
      "ratio": 10.0,
      "num_points": 78
    },
    {
      "s0": 1.3254947840660307,
      "s1": 1.5,
      "ratio": 1.557967416600765,
      "num_points": 15
    },
    {
      "s0": 1.5,
      "s1": 1.8339736035413066,
      "ratio": 2.202394304953613,
      "num_points": 15
    },
    {
      "s0": 1.8339736035413066,
      "s1": 2.0,
      "ratio": 0.7285956310741509,
      "num_points": 6
    },
    {
      "s0": 2.0,
      "s1": 2.5,
      "ratio": 1.0,
      "num_points": 20
    }
  ]
}

r_test_4_adj = {
  "lower_bnd": 1.0,
  "upper_bnd": 2.5,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 1.0,
      "s1": 1.5,
      "ds0": 0.02,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 1.5,
      "s1": 1.7641909440046184,
      "ds0": 0.02,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0587419218023963,
      "ratio": 1.0587419218023963
    },
    {
      "s0": 1.7641909440046184,
      "s1": 2.2,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.0591352277749606,
      "ratio": 0.9441664990227996
    },
    {
      "s0": 2.2,
      "s1": 2.3,
      "ds0": 0.01,
      "ds1": 0.001,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 2.3,
      "s1": 2.5,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    }
  ]
}

r_test_4_legacy = {
  "lower_bnd": 1.0,
  "upper_bnd": 2.5,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 1.0,
      "s1": 1.5,
      "ratio": 1.0,
      "num_points": 25
    },
    {
      "s0": 1.5,
      "s1": 1.7099533069186643,
      "ratio": 1.5992207734956971,
      "num_points": 9
    },
    {
      "s0": 1.7099533069186643,
      "s1": 2.2,
      "ratio": 0.12543280749281463,
      "num_points": 37
    },
    {
      "s0": 2.2,
      "s1": 2.3,
      "ratio": 0.24925876497741845,
      "num_points": 47
    },
    {
      "s0": 2.3,
      "s1": 2.5,
      "ratio": 1.0,
      "num_points": 201
    }
  ]
}


r_test_5_adj = {
  "lower_bnd": 1.0,
  "upper_bnd": 10.0,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.1,
  "segment_list": [
    {
      "s0": 1.0,
      "s1": 1.05,
      "ds0": 0.0001,
      "ds1": 0.0001,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 1.05,
      "s1": 1.3,
      "ds0": 0.0001,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0297966124717568,
      "ratio": 1.0297966124717568
    },
    {
      "s0": 1.3,
      "s1": 10.0,
      "ds0": 0.0074897005603861075,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.1,
      "ratio": 1.1
    }
  ]
}

r_test_5_legacy = {
  "lower_bnd": 1.0,
  "upper_bnd": 10.0,
  "periodic": False,
  "phi_shift": 0.0,
  "BG_RATIO": 1.1,
  "segment_list": [
    {
      "s0": 1.0,
      "s1": 1.05,
      "ratio": 1.0,
      "num_points": 501
    },
    {
      "s0": 1.05,
      "s1": 1.3,
      "ratio": 74.89700560385994,
      "num_points": 147
    },
    {
      "s0": 1.3,
      "s1": 10.0,
      "ratio": 117.39085287969579,
      "num_points": 50
    }
  ]
}

phi_test_1_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.05000000000000071,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.3499999999999993,
            "ds0": numpy.Infinity,
            "ds1": 0.04,
            "var_ds_ratio": 1.0528507997038918,
            "ratio": 0.9498021944621633
        },
        {
            "s0": 0.3499999999999993,
            "s1": 2.749999999999999,
            "ds0": 0.04,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 2.749999999999999,
            "s1": 2.9499999999999993,
            "ds0": 0.02,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 2.9499999999999993,
            "s1": 3.249999999999999,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 3.249999999999999,
            "s1": 3.749999999999999,
            "ds0": 0.01,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 3.749999999999999,
            "s1": 5.933185307179586,
            "ds0": 0.02,
            "ds1": 0.04,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 5.933185307179586,
            "s1": 6.283185307179586,
            "ds0": 0.04,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0528507997038918,
            "ratio": 1.0528507997038918
        }
    ]
}

phi_test_1_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.05000000000000071,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.3499999999999993,
            "ratio": 0.6623161564131852,
            "num_points": 8
        },
        {
            "s0": 0.3499999999999993,
            "s1": 1.901790301223205,
            "ratio": 1.0,
            "num_points": 39
        },
        {
            "s0": 1.901790301223205,
            "s1": 2.6005967670744012,
            "ratio": 0.5,
            "num_points": 24
        },
        {
            "s0": 2.6005967670744012,
            "s1": 2.9499999999999993,
            "ratio": 0.5,
            "num_points": 24
        },
        {
            "s0": 2.9499999999999993,
            "s1": 3.249999999999999,
            "ratio": 1.0,
            "num_points": 30
        },
        {
            "s0": 3.249999999999999,
            "s1": 3.599403232925597,
            "ratio": 2.0,
            "num_points": 24
        },
        {
            "s0": 3.599403232925597,
            "s1": 3.749999999999999,
            "ratio": 1.0,
            "num_points": 8
        },
        {
            "s0": 3.749999999999999,
            "s1": 4.448806465851195,
            "ratio": 2.0,
            "num_points": 24
        },
        {
            "s0": 4.448806465851195,
            "s1": 5.933185307179586,
            "ratio": 1.0,
            "num_points": 38
        },
        {
            "s0": 5.933185307179586,
            "s1": 6.283185307179586,
            "ratio": 1.509852946084787,
            "num_points": 8
        }
    ]
}

phi_test_2_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 3.3,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 3.3,
            "s1": 3.8,
            "ds0": 0.01,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 3.8,
            "s1": 4.5,
            "ds0": 0.02,
            "ds1": 0.04,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 4.5,
            "s1": 6.283185307179586,
            "ds0": 0.04,
            "ds1": 0.01,
            "var_ds_ratio": 1.06,
            "ratio": 0.9433962264150942
        }
    ]
}

phi_test_2_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 3.3,
            "ratio": 1.0,
            "num_points": 330
        },
        {
            "s0": 3.3,
            "s1": 3.649403232925598,
            "ratio": 2.0,
            "num_points": 24
        },
        {
            "s0": 3.649403232925598,
            "s1": 3.8,
            "ratio": 1.0,
            "num_points": 8
        },
        {
            "s0": 3.8,
            "s1": 4.498806465851196,
            "ratio": 2.0,
            "num_points": 24
        },
        {
            "s0": 4.498806465851196,
            "s1": 4.5,
            "ratio": 1.0,
            "num_points": 1
        },
        {
            "s0": 4.5,
            "s1": 5.759932900462031,
            "ratio": 1.0,
            "num_points": 32
        },
        {
            "s0": 5.759932900462031,
            "s1": 6.283185307179586,
            "ratio": 0.25,
            "num_points": 24
        }
    ]
}

phi_test_3_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.10840734641020688,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.8915926535897931,
            "ds0": numpy.Infinity,
            "ds1": 0.02,
            "var_ds_ratio": 1.0599206374122232,
            "ratio": 0.9434668641243571
        },
        {
            "s0": 0.8915926535897931,
            "s1": 5.391592653589793,
            "ds0": 0.02,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 5.391592653589793,
            "s1": 6.283185307179586,
            "ds0": 0.02,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0599206374122232,
            "ratio": 1.0599206374122232
        }
    ]
}

phi_test_3_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.10840734641020688,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.8915926535897931,
            "ratio": 0.27796258268320523,
            "num_points": 22
        },
        {
            "s0": 0.8915926535897931,
            "s1": 5.391592653589793,
            "ratio": 1.0,
            "num_points": 225
        },
        {
            "s0": 5.391592653589793,
            "s1": 6.283185307179586,
            "ratio": 3.5976065208017647,
            "num_points": 22
        }
    ]
}

phi_test_4_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 3.01,
            "ds0": 0.01,
            "ds1": 0.05,
            "var_ds_ratio": 1.06,
            "ratio": 1.06
        },
        {
            "s0": 3.01,
            "s1": 4.0,
            "ds0": 0.05,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 4.0,
            "s1": 6.283185307179586,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        }
    ]
}

phi_test_4_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.7056399080617372,
            "ratio": 5.0,
            "num_points": 28
        },
        {
            "s0": 0.7056399080617372,
            "s1": 2.618973611211664,
            "ratio": 1.0,
            "num_points": 39
        },
        {
            "s0": 2.618973611211664,
            "s1": 4.0,
            "ratio": 0.19999999999999998,
            "num_points": 55
        },
        {
            "s0": 4.0,
            "s1": 6.283185307179586,
            "ratio": 1.0,
            "num_points": 229
        }
    ]
}

phi_test_5_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": -2.2415926535897936,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 2.7415926535897936,
            "ds0": numpy.Infinity,
            "ds1": 0.07,
            "var_ds_ratio": 1.0582271327157975,
            "ratio": 0.9449767153802177
        },
        {
            "s0": 2.7415926535897936,
            "s1": 3.5415926535897935,
            "ds0": 0.07,
            "ds1": 0.07,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 3.5415926535897935,
            "s1": 6.283185307179586,
            "ds0": 0.07,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0582271327157975,
            "ratio": 1.0582271327157975
        }
    ]
}

phi_test_5_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": -2.2415926535897936,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 2.7415926535897936,
            "ratio": 0.30467951551386085,
            "num_points": 21
        },
        {
            "s0": 2.7415926535897936,
            "s1": 3.5415926535897935,
            "ratio": 1.0,
            "num_points": 12
        },
        {
            "s0": 3.5415926535897935,
            "s1": 6.283185307179586,
            "ratio": 3.2821372920770138,
            "num_points": 21
        }
    ]
}

phi_test_6_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.1,
            "ds0": 0.01,
            "ds1": 0.03,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 1.1,
            "s1": 1.7216181119907636,
            "ds0": 0.03,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0581871097966855,
            "ratio": 1.0581871097966855
        },
        {
            "s0": 1.7216181119907636,
            "s1": 2.0,
            "ds0": numpy.Infinity,
            "ds1": 0.05,
            "var_ds_ratio": 1.0578038842945854,
            "ratio": 0.9453548194019604
        },
        {
            "s0": 2.0,
            "s1": 6.0,
            "ds0": 0.05,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 6.0,
            "s1": 6.283185307179586,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        }
    ]
}

phi_test_6_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.7019173040990004,
            "ratio": 3.0,
            "num_points": 38
        },
        {
            "s0": 0.7019173040990004,
            "s1": 1.1,
            "ratio": 1.0,
            "num_points": 14
        },
        {
            "s0": 1.1,
            "s1": 1.7216181119907636,
            "ratio": 2.207366955192968,
            "num_points": 14
        },
        {
            "s0": 1.7216181119907636,
            "s1": 2.0,
            "ratio": 0.7550473937945511,
            "num_points": 5
        },
        {
            "s0": 2.0,
            "s1": 4.618973611211664,
            "ratio": 1.0,
            "num_points": 53
        },
        {
            "s0": 4.618973611211664,
            "s1": 6.0,
            "ratio": 0.19999999999999998,
            "num_points": 55
        },
        {
            "s0": 6.0,
            "s1": 6.283185307179586,
            "ratio": 1.0,
            "num_points": 29
        }
    ]
}

phi_test_7_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": -1.7415926535897928,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 2.7415926535897928,
            "ds0": numpy.Infinity,
            "ds1": 0.03,
            "var_ds_ratio": 1.0593344932820365,
            "ratio": 0.9439888971252073
        },
        {
            "s0": 2.7415926535897928,
            "s1": 3.5415926535897926,
            "ds0": 0.03,
            "ds1": 0.03,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 3.5415926535897926,
            "s1": 6.283185307179586,
            "ds0": 0.03,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0593344932820365,
            "ratio": 1.0593344932820365
        }
    ]
}

phi_test_7_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": -1.7415926535897928,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 2.7415926535897928,
            "ratio": 0.1581030913822823,
            "num_points": 32
        },
        {
            "s0": 2.7415926535897928,
            "s1": 3.5415926535897926,
            "ratio": 1.0,
            "num_points": 27
        },
        {
            "s0": 3.5415926535897926,
            "s1": 6.283185307179586,
            "ratio": 6.3249870148463385,
            "num_points": 32
        }
    ]
}

phi_test_8_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.0,
            "ds0": 0.02,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 1.0,
            "s1": 1.4,
            "ds0": 0.01,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 1.4,
            "s1": 1.8,
            "ds0": 0.001,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 1.8,
            "s1": 3.8,
            "ds0": 0.001,
            "ds1": 0.02,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 3.8,
            "s1": 4.829708671944582,
            "ds0": 0.02,
            "ds1": 0.08000000000000002,
            "var_ds_ratio": 1.0594630943592953,
            "ratio": 1.0594630943592953
        },
        {
            "s0": 4.829708671944582,
            "s1": 5.253476635235004,
            "ds0": 0.08000000000000002,
            "ds1": 0.08000000000000002,
            "var_ds_ratio": 1.06,
            "ratio": 1.0
        },
        {
            "s0": 5.253476635235004,
            "s1": 6.283185307179586,
            "ds0": 0.08000000000000002,
            "ds1": 0.02,
            "var_ds_ratio": 1.0594630943592953,
            "ratio": 0.9438743126816934
        }
    ]
}

phi_test_8_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.6505967670744018,
            "ratio": 1.0,
            "num_points": 33
        },
        {
            "s0": 0.6505967670744018,
            "s1": 1.0,
            "ratio": 0.5,
            "num_points": 24
        },
        {
            "s0": 1.0,
            "s1": 1.0945052159339692,
            "ratio": 1.0,
            "num_points": 10
        },
        {
            "s0": 1.0945052159339692,
            "s1": 1.4,
            "ratio": 0.1,
            "num_points": 78
        },
        {
            "s0": 1.4,
            "s1": 1.8,
            "ratio": 1.0,
            "num_points": 401
        },
        {
            "s0": 1.8,
            "s1": 2.4559483198963807,
            "ratio": 20.0,
            "num_points": 102
        },
        {
            "s0": 2.4559483198963807,
            "s1": 3.8,
            "ratio": 1.0,
            "num_points": 68
        },
        {
            "s0": 3.8,
            "s1": 4.838740429440055,
            "ratio": 4.000000000000001,
            "num_points": 24
        },
        {
            "s0": 4.838740429440055,
            "s1": 5.244444877739532,
            "ratio": 1.0,
            "num_points": 6
        },
        {
            "s0": 5.244444877739532,
            "s1": 6.283185307179586,
            "ratio": 0.24999999999999994,
            "num_points": 24
        }
    ]
}

phi_test_9_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.1227718496041565,
            "ds0": 0.01,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.059428095881843,
            "ratio": 1.059428095881843
        },
        {
            "s0": 1.1227718496041565,
            "s1": 2.4,
            "ds0": numpy.Infinity,
            "ds1": 0.001,
            "var_ds_ratio": 1.0593350946009565,
            "ratio": 0.9439883612811792
        },
        {
            "s0": 2.4,
            "s1": 4.8,
            "ds0": 0.001,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 4.8,
            "s1": 6.283185307179586,
            "ds0": 0.001,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        }
    ]
}

phi_test_9_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.1227718496041565,
            "ratio": 7.542268974877096,
            "num_points": 35
        },
        {
            "s0": 1.1227718496041565,
            "s1": 2.4,
            "ratio": 0.01325860962173251,
            "num_points": 75
        },
        {
            "s0": 2.4,
            "s1": 4.8,
            "ratio": 1.0,
            "num_points": 2400
        },
        {
            "s0": 4.8,
            "s1": 5.105494784066031,
            "ratio": 10.0,
            "num_points": 78
        },
        {
            "s0": 5.105494784066031,
            "s1": 6.283185307179586,
            "ratio": 1.0,
            "num_points": 118
        }
    ]
}

phi_test_10_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.858090559953818,
            "ds0": 0.01,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0595016886637296,
            "ratio": 1.0595016886637296
        },
        {
            "s0": 0.858090559953818,
            "s1": 1.3874531392544946,
            "ds0": 0.06,
            "ds1": 0.06,
            "var_ds_ratio": 1.06,
            "ratio": 1.0
        },
        {
            "s0": 1.3874531392544946,
            "s1": 2.4,
            "ds0": numpy.Infinity,
            "ds1": 0.001,
            "var_ds_ratio": 1.0593619837865456,
            "ratio": 0.9439644005589438
        },
        {
            "s0": 2.4,
            "s1": 4.8,
            "ds0": 0.001,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 4.8,
            "s1": 6.283185307179586,
            "ds0": 0.001,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        }
    ]
}
phi_test_10_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.858090559953818,
            "ds0": 0.01,
            "ds1": 0.06,
            "var_ds_ratio": 1.0595016886637296,
            "ratio": 1.0595016886637296
        },
        {
            "s0": 0.858090559953818,
            "s1": 1.3874531392544946,
            "ds0": 0.06,
            "ds1": 0.06,
            "var_ds_ratio": 1.06,
            "ratio": 1.0
        },
        {
            "s0": 1.3874531392544946,
            "s1": 2.4,
            "ds0": 0.06,
            "ds1": 0.001,
            "var_ds_ratio": 1.0593619837865456,
            "ratio": 0.9439644005589438
        },
        {
            "s0": 2.4,
            "s1": 4.8,
            "ds0": 0.001,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 4.8,
            "s1": 6.283185307179586,
            "ds0": 0.001,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        }
    ]
}

phi_test_10_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.865071471154434,
            "ratio": 6.0,
            "num_points": 31
        },
        {
            "s0": 0.865071471154434,
            "s1": 1.3151176742877821,
            "ratio": 1.0,
            "num_points": 8
        },
        {
            "s0": 1.3151176742877821,
            "s1": 2.4,
            "ratio": 0.016666666666666666,
            "num_points": 72
        },
        {
            "s0": 2.4,
            "s1": 4.8,
            "ratio": 1.0,
            "num_points": 2400
        },
        {
            "s0": 4.8,
            "s1": 5.105494784066031,
            "ratio": 10.0,
            "num_points": 78
        },
        {
            "s0": 5.105494784066031,
            "s1": 6.283185307179586,
            "ratio": 1.0,
            "num_points": 118
        }
    ]
}

phi_test_11_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.6084073464102069,
    "BG_RATIO": 1.05,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.3915926535897931,
            "ds0": numpy.Infinity,
            "ds1": 0.01,
            "var_ds_ratio": 1.0396255358030364,
            "ratio": 0.9618847994413406
        },
        {
            "s0": 1.3915926535897931,
            "s1": 1.791592653589793,
            "ds0": 0.01,
            "ds1": 0.002,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 1.791592653589793,
            "s1": 2.791592653589793,
            "ds0": 0.002,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 2.791592653589793,
            "s1": 3.4915926535897928,
            "ds0": 0.001,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 3.4915926535897928,
            "s1": 4.191592653589793,
            "ds0": 0.001,
            "ds1": 0.002,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 4.191592653589793,
            "s1": 4.891592653589793,
            "ds0": 0.002,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 4.891592653589793,
            "s1": 6.283185307179586,
            "ds0": 0.01,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0396255358030364,
            "ratio": 1.0396255358030364
        }
    ]
}

phi_test_11_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.6084073464102069,
    "BG_RATIO": 1.05,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.3915926535897931,
            "ratio": 0.15484848501014292,
            "num_points": 48
        },
        {
            "s0": 1.3915926535897931,
            "s1": 1.515387375832126,
            "ratio": 1.0,
            "num_points": 13
        },
        {
            "s0": 1.515387375832126,
            "s1": 1.791592653589793,
            "ratio": 0.2,
            "num_points": 55
        },
        {
            "s0": 1.791592653589793,
            "s1": 2.756652330297233,
            "ratio": 1.0,
            "num_points": 483
        },
        {
            "s0": 2.756652330297233,
            "s1": 2.791592653589793,
            "ratio": 0.5,
            "num_points": 24
        },
        {
            "s0": 2.791592653589793,
            "s1": 3.4915926535897928,
            "ratio": 1.0,
            "num_points": 700
        },
        {
            "s0": 3.4915926535897928,
            "s1": 3.526532976882353,
            "ratio": 2.0,
            "num_points": 24
        },
        {
            "s0": 3.526532976882353,
            "s1": 4.191592653589793,
            "ratio": 1.0,
            "num_points": 333
        },
        {
            "s0": 4.191592653589793,
            "s1": 4.4677979313474605,
            "ratio": 5.0,
            "num_points": 55
        },
        {
            "s0": 4.4677979313474605,
            "s1": 4.891592653589793,
            "ratio": 1.0,
            "num_points": 43
        },
        {
            "s0": 4.891592653589793,
            "s1": 6.283185307179586,
            "ratio": 6.457925629265904,
            "num_points": 48
        }
    ]
}
phi_test_12_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.9801307323588668,
  "BG_RATIO": 1.05,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 1.0198692676411332,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.0390636284161634,
      "ratio": 0.9624049698710869
    },
    {
      "s0": 1.0198692676411332,
      "s1": 2.019869267641133,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 2.019869267641133,
      "s1": 2.1051339750315057,
      "ds0": 0.01,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0367196599757575,
      "ratio": 1.0367196599757575
    },
    {
      "s0": 2.1051339750315057,
      "s1": 2.419869267641133,
      "ds0": numpy.Infinity,
      "ds1": 0.001,
      "var_ds_ratio": 1.0394303253815222,
      "ratio": 0.9620654464097443
    },
    {
      "s0": 2.419869267641133,
      "s1": 3.119869267641133,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 3.119869267641133,
      "s1": 3.5346045602507603,
      "ds0": 0.001,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0397954333264119,
      "ratio": 1.0397954333264119
    },
    {
      "s0": 3.5346045602507603,
      "s1": 3.7198692676411333,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.0397828531241722,
      "ratio": 0.9617392679590367
    },
    {
      "s0": 3.7198692676411333,
      "s1": 4.519869267641133,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 4.519869267641133,
      "s1": 5.539738535282266,
      "ds0": 0.01,
      "ds1": 0.049999999999999996,
      "var_ds_ratio": 1.0390636284161634,
      "ratio": 1.0390636284161634
    },
    {
      "s0": 5.539738535282266,
      "s1": 6.283185307179586,
      "ds0": 0.049999999999999996,
      "ds1": 0.049999999999999996,
      "var_ds_ratio": 1.05,
      "ratio": 1.0
    }
  ]
}

phi_test_12_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.9801307323588668,
  "BG_RATIO": 1.05,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 1.0198692676411332,
      "ratio": 0.1999999999999998,
      "num_points": 42
    },
    {
      "s0": 1.0198692676411332,
      "s1": 2.019869267641133,
      "ratio": 1.0,
      "num_points": 100
    },
    {
      "s0": 2.019869267641133,
      "s1": 2.1051339750315057,
      "ratio": 1.3344142630656264,
      "num_points": 8
    },
    {
      "s0": 2.1051339750315057,
      "s1": 2.419869267641133,
      "ratio": 0.07493924695488781,
      "num_points": 67
    },
    {
      "s0": 2.419869267641133,
      "s1": 3.119869267641133,
      "ratio": 1.0,
      "num_points": 700
    },
    {
      "s0": 3.119869267641133,
      "s1": 3.5346045602507603,
      "ratio": 17.266213945984404,
      "num_points": 73
    },
    {
      "s0": 3.5346045602507603,
      "s1": 3.7198692676411333,
      "ratio": 0.5791657644972996,
      "num_points": 14
    },
    {
      "s0": 3.7198692676411333,
      "s1": 4.519869267641133,
      "ratio": 1.0,
      "num_points": 80
    },
    {
      "s0": 4.519869267641133,
      "s1": 5.5637119577012815,
      "ratio": 4.999999999999999,
      "num_points": 42
    },
    {
      "s0": 5.5637119577012815,
      "s1": 6.283185307179586,
      "ratio": 1.0,
      "num_points": 15
    }
  ]
}

phi_test_13_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 1.2350980492691503,
  "BG_RATIO": 1.05,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.7649019507308497,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.0392592260318434,
      "ratio": 0.9622238368941451
    },
    {
      "s0": 0.7649019507308497,
      "s1": 1.7649019507308497,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 1.7649019507308497,
      "s1": 2.1649019507308496,
      "ds0": 0.01,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0384591196385107,
      "ratio": 1.0384591196385107
    },
    {
      "s0": 2.1649019507308496,
      "s1": 2.8649019507308493,
      "ds0": 0.02568828526131253,
      "ds1": 0.03,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 2.8649019507308493,
      "s1": 2.9099346338205665,
      "ds0": 0.03,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.029015936805393,
      "ratio": 1.029015936805393
    },
    {
      "s0": 2.9099346338205665,
      "s1": 3.46490195073085,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.0392790717951337,
      "ratio": 0.9622054625546462
    },
    {
      "s0": 3.46490195073085,
      "s1": 4.26490195073085,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 4.26490195073085,
      "s1": 5.029803901461699,
      "ds0": 0.01,
      "ds1": 0.03999999999999999,
      "var_ds_ratio": 1.0392592260318434,
      "ratio": 1.0392592260318434
    },
    {
      "s0": 5.029803901461699,
      "s1": 6.283185307179586,
      "ds0": 0.03999999999999999,
      "ds1": 0.03999999999999999,
      "var_ds_ratio": 1.05,
      "ratio": 1.0
    }
  ]
}

phi_test_13_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 1.2350980492691503,
  "BG_RATIO": 1.05,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.7649019507308497,
      "ratio": 0.25000000000000006,
      "num_points": 36
    },
    {
      "s0": 0.7649019507308497,
      "s1": 1.7649019507308497,
      "ratio": 1.0,
      "num_points": 100
    },
    {
      "s0": 1.7649019507308497,
      "s1": 2.1649019507308496,
      "ratio": 2.5688285261312487,
      "num_points": 25
    },
    {
      "s0": 2.1649019507308496,
      "s1": 2.3335444656783464,
      "ratio": 1.167847510833318,
      "num_points": 6
    },
    {
      "s0": 2.3335444656783464,
      "s1": 2.8649019507308493,
      "ratio": 1.0,
      "num_points": 18
    },
    {
      "s0": 2.8649019507308493,
      "s1": 2.9099346338205665,
      "ratio": 1.0588737981994807,
      "num_points": 2
    },
    {
      "s0": 2.9099346338205665,
      "s1": 3.46490195073085,
      "ratio": 0.314799869351887,
      "num_points": 30
    },
    {
      "s0": 3.46490195073085,
      "s1": 4.26490195073085,
      "ratio": 1.0,
      "num_points": 80
    },
    {
      "s0": 4.26490195073085,
      "s1": 5.04395727281089,
      "ratio": 3.9999999999999987,
      "num_points": 36
    },
    {
      "s0": 5.04395727281089,
      "s1": 6.283185307179586,
      "ratio": 1.0,
      "num_points": 31
    }
  ]
}

phi_test_14_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": -1.376047345199388,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 2.3265158053216015,
            "ds0": numpy.Infinity,
            "ds1": 0.05,
            "var_ds_ratio": 1.058673040321875,
            "ratio": 0.9445786960778408
        },
        {
            "s0": 2.3265158053216015,
            "s1": 2.890067901146277,
            "ds0": 0.05,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 2.890067901146277,
            "s1": 3.1087597592274943,
            "ds0": 0.001,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 3.1087597592274943,
            "s1": 3.613433277876457,
            "ds0": 0.001,
            "ds1": 0.03,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 3.613433277876457,
            "s1": 6.283185307179586,
            "ds0": 0.03,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.058596261103124,
            "ratio": 1.058596261103124
        }
    ]
}

phi_test_14_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": -1.5293830397697938,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 2.4798514998920074,
            "ratio": 0.11678309982985156,
            "num_points": 39
        },
        {
            "s0": 2.4798514998920074,
            "s1": 3.0434035957166827,
            "ratio": 0.05520163979708691,
            "num_points": 98
        },
        {
            "s0": 3.0434035957166827,
            "s1": 3.2620954537979,
            "ratio": 1.0,
            "num_points": 219
        },
        {
            "s0": 3.2620954537979,
            "s1": 3.766768972446863,
            "ratio": 16.09530171896414,
            "num_points": 94
        },
        {
            "s0": 3.766768972446863,
            "s1": 6.283185307179586,
            "ratio": 9.637600060623692,
            "num_points": 42
        }
    ]
}

phi_test_15_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.09,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 2.0,
            "ds0": 0.01,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 0.970873786407767
        },
        {
            "s0": 2.0,
            "s1": 2.2,
            "ds0": 0.001,
            "ds1": 0.001,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        },
        {
            "s0": 2.2,
            "s1": 3.0,
            "ds0": 0.001,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 3.0,
            "s1": 4.1,
            "ds0": 0.01,
            "ds1": 0.03,
            "var_ds_ratio": 1.03,
            "ratio": 1.03
        },
        {
            "s0": 4.1,
            "s1": 5.019974541599029,
            "ds0": 0.03,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0585921079410743,
            "ratio": 1.0585921079410743
        },
        {
            "s0": 5.019974541599029,
            "s1": 6.283185307179586,
            "ds0": numpy.Infinity,
            "ds1": 0.01,
            "var_ds_ratio": 1.059071604498224,
            "ratio": 0.9442232194241376
        }
    ]
}

phi_test_15_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.09,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.6945052159339693,
            "ratio": 1.0,
            "num_points": 170
        },
        {
            "s0": 1.6945052159339693,
            "s1": 2.0,
            "ratio": 0.1,
            "num_points": 78
        },
        {
            "s0": 2.0,
            "s1": 2.2,
            "ratio": 1.0,
            "num_points": 201
        },
        {
            "s0": 2.2,
            "s1": 2.505494784066031,
            "ratio": 10.0,
            "num_points": 78
        },
        {
            "s0": 2.505494784066031,
            "s1": 3.0,
            "ratio": 1.0,
            "num_points": 50
        },
        {
            "s0": 3.0,
            "s1": 3.7019173040990005,
            "ratio": 3.0,
            "num_points": 38
        },
        {
            "s0": 3.7019173040990005,
            "s1": 4.1,
            "ratio": 1.0,
            "num_points": 14
        },
        {
            "s0": 4.1,
            "s1": 5.019974541599029,
            "ratio": 2.7868637346943546,
            "num_points": 18
        },
        {
            "s0": 5.019974541599029,
            "s1": 6.283185307179586,
            "ratio": 0.11960876636470795,
            "num_points": 37
        }
    ]
}

phi_test_16_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.09,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 6.283185307179586,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.03,
            "ratio": 1.0
        }
    ]
}

phi_test_16_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.0,
    "BG_RATIO": 1.09,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 6.283185307179586,
            "ratio": 1.0,
            "num_points": 629
        }
    ]
}
phi_test_17_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 1.7973716589288333,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.2549673169102826,
      "ds0": numpy.Infinity,
      "ds1": 0.02,
      "var_ds_ratio": 1.037548235793919,
      "ratio": 0.9638106118842874
    },
    {
      "s0": 0.2549673169102826,
      "s1": 1.5334735641543213,
      "ds0": 0.02,
      "ds1": 0.02,
      "var_ds_ratio": 1.04,
      "ratio": 1.0
    },
    {
      "s0": 1.5334735641543213,
      "s1": 2.184028246949664,
      "ds0": 0.02,
      "ds1": 0.03,
      "var_ds_ratio": 1.04,
      "ratio": 1.04
    },
    {
      "s0": 2.184028246949664,
      "s1": 3.08955024665529,
      "ds0": 0.03,
      "ds1": 0.01,
      "var_ds_ratio": 1.04,
      "ratio": 0.9615384615384615
    },
    {
      "s0": 3.08955024665529,
      "s1": 3.6699247931015977,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.04,
      "ratio": 1.0
    },
    {
      "s0": 3.6699247931015977,
      "s1": 4.179859426922165,
      "ds0": 0.01,
      "ds1": 0.030000000000000013,
      "var_ds_ratio": 1.0386098978426228,
      "ratio": 1.0386098978426228
    },
    {
      "s0": 4.179859426922165,
      "s1": 6.283185307179586,
      "ds0": 0.030000000000000013,
      "ds1": 0.030000000000000006,
      "var_ds_ratio": 1.06,
      "ratio": 0.9433962264150942
    }
  ]
}

phi_test_17_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 1.7973716589288333,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.2549673169102826,
      "ratio": 0.666666666666666,
      "num_points": 11
    },
    {
      "s0": 0.2549673169102826,
      "s1": 1.5334735641543213,
      "ratio": 1.0,
      "num_points": 64
    },
    {
      "s0": 1.5334735641543213,
      "s1": 1.8085598708243702,
      "ratio": 1.5,
      "num_points": 11
    },
    {
      "s0": 1.8085598708243702,
      "s1": 2.184028246949664,
      "ratio": 1.0,
      "num_points": 13
    },
    {
      "s0": 2.184028246949664,
      "s1": 2.549363370483635,
      "ratio": 1.0,
      "num_points": 13
    },
    {
      "s0": 2.549363370483635,
      "s1": 3.08955024665529,
      "ratio": 0.33333333333333337,
      "num_points": 29
    },
    {
      "s0": 3.08955024665529,
      "s1": 3.6699247931015977,
      "ratio": 1.0,
      "num_points": 59
    },
    {
      "s0": 3.6699247931015977,
      "s1": 4.22843903643576,
      "ratio": 3.0000000000000013,
      "num_points": 30
    },
    {
      "s0": 4.22843903643576,
      "s1": 6.252294047021249,
      "ratio": 1.0,
      "num_points": 68
    },
    {
      "s0": 6.252294047021249,
      "s1": 6.283185307179586,
      "ratio": 0.9999999999999998,
      "num_points": 1
    }
  ]
}

phi_test_18_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 2.2179329244696344,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.2549673169102835,
            "ds0": numpy.Infinity,
            "ds1": 0.01,
            "var_ds_ratio": 1.0392592260318434,
            "ratio": 0.9622238368941451
        },
        {
            "s0": 0.2549673169102835,
            "s1": 1.1297347492351522,
            "ds0": 0.01,
            "ds1": 0.001,
            "var_ds_ratio": 1.04,
            "ratio": 0.9615384615384615
        },
        {
            "s0": 1.1297347492351522,
            "s1": 1.4745949869786106,
            "ds0": 0.001,
            "ds1": 0.001,
            "var_ds_ratio": 1.04,
            "ratio": 1.0
        },
        {
            "s0": 1.4745949869786106,
            "s1": 1.6259970425732995,
            "ds0": 0.001,
            "ds1": 0.01,
            "var_ds_ratio": 1.04,
            "ratio": 1.04
        },
        {
            "s0": 1.6259970425732995,
            "s1": 1.880964359483583,
            "ds0": 0.01,
            "ds1": 0.020000000000000007,
            "var_ds_ratio": 1.0392592260318434,
            "ratio": 1.0392592260318434
        },
        {
            "s0": 1.880964359483583,
            "s1": 6.283185307179586,
            "ds0": 0.020000000000000007,
            "ds1": 0.020000000000000007,
            "var_ds_ratio": 1.06,
            "ratio": 1.0
        }
    ]
}

phi_test_18_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 2.2179329244696344,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.2549673169102835,
            "ratio": 0.5000000000000001,
            "num_points": 18
        },
        {
            "s0": 0.2549673169102835,
            "s1": 0.8973313679331887,
            "ratio": 1.0,
            "num_points": 65
        },
        {
            "s0": 0.8973313679331887,
            "s1": 1.1297347492351522,
            "ratio": 0.1,
            "num_points": 59
        },
        {
            "s0": 1.1297347492351522,
            "s1": 1.4745949869786106,
            "ratio": 1.0,
            "num_points": 345
        },
        {
            "s0": 1.4745949869786106,
            "s1": 1.706998368280574,
            "ratio": 10.0,
            "num_points": 59
        },
        {
            "s0": 1.706998368280574,
            "s1": 1.9870735482944881,
            "ratio": 2.000000000000001,
            "num_points": 19
        },
        {
            "s0": 1.9870735482944881,
            "s1": 6.283185307179586,
            "ratio": 1.0,
            "num_points": 215
        }
    ]
}

phi_test_19_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.34485746710016585,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 2.128042774279752,
            "ds0": numpy.Infinity,
            "ds1": 0.04,
            "var_ds_ratio": 1.0580622497757568,
            "ratio": 0.9451239756563828
        },
        {
            "s0": 2.128042774279752,
            "s1": 3.0028102066046207,
            "ds0": 0.04,
            "ds1": 0.001,
            "var_ds_ratio": 1.05,
            "ratio": 0.9523809523809523
        },
        {
            "s0": 3.0028102066046207,
            "s1": 3.499072499942768,
            "ds0": 0.001,
            "ds1": 0.001,
            "var_ds_ratio": 1.05,
            "ratio": 1.0
        },
        {
            "s0": 3.499072499942768,
            "s1": 3.655142532899834,
            "ds0": 0.001,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0595015959173797,
            "ratio": 1.0595015959173797
        },
        {
            "s0": 3.655142532899834,
            "s1": 4.155142532899834,
            "ds0": 0.010094030411281166,
            "ds1": 0.04,
            "var_ds_ratio": 1.05,
            "ratio": 1.05
        },
        {
            "s0": 4.155142532899834,
            "s1": 6.283185307179586,
            "ds0": 0.04,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0580622497757568,
            "ratio": 1.0580622497757568
        }
    ]
}

phi_test_19_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.38125888683913445,
    "BG_RATIO": 1.06,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 2.0916413545407835,
            "ratio": 0.253083666722372,
            "num_points": 25
        },
        {
            "s0": 2.0916413545407835,
            "s1": 2.151196932242241,
            "ratio": 1.0,
            "num_points": 2
        },
        {
            "s0": 2.151196932242241,
            "s1": 2.966408786865652,
            "ratio": 0.025,
            "num_points": 76
        },
        {
            "s0": 2.966408786865652,
            "s1": 3.4626710802037994,
            "ratio": 1.0,
            "num_points": 497
        },
        {
            "s0": 3.4626710802037994,
            "s1": 3.6187411131608656,
            "ratio": 10.09403041128119,
            "num_points": 40
        },
        {
            "s0": 3.6187411131608656,
            "s1": 4.1187411131608656,
            "ratio": 3.555672687944358,
            "num_points": 26
        },
        {
            "s0": 4.1187411131608656,
            "s1": 6.283185307179586,
            "ratio": 4.403616483539033,
            "num_points": 27
        }
    ]
}

phi_test_20_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": -3.1722718592555537,
    "BG_RATIO": 1.02,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 4.425544430567145,
            "ds0": numpy.Infinity,
            "ds1": 0.01,
            "var_ds_ratio": 1.0198379632602637,
            "ratio": 0.98054792626385
        },
        {
            "s0": 4.425544430567145,
            "s1": 5.0395638782567165,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.04,
            "ratio": 1.0
        },
        {
            "s0": 5.0395638782567165,
            "s1": 5.190965933851405,
            "ds0": 0.01,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0189066958677706,
            "ratio": 1.0189066958677706
        },
        {
            "s0": 5.190965933851405,
            "s1": 5.897508859959953,
            "ds0": 0.012998158478817108,
            "ds1": 0.09,
            "var_ds_ratio": 1.04,
            "ratio": 1.04
        },
        {
            "s0": 5.897508859959953,
            "s1": 6.283185307179586,
            "ds0": 0.09,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0164236122995187,
            "ratio": 1.0164236122995187
        }
    ]
}

phi_test_20_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": -2.1393787859130526,
    "BG_RATIO": 1.02,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 3.392651357224644,
            "ratio": 0.15321683100108593,
            "num_points": 116
        },
        {
            "s0": 3.392651357224644,
            "s1": 4.006670804914215,
            "ratio": 1.0,
            "num_points": 62
        },
        {
            "s0": 4.006670804914215,
            "s1": 4.158072860508904,
            "ratio": 1.2998158478817123,
            "num_points": 14
        },
        {
            "s0": 4.158072860508904,
            "s1": 4.864615786617453,
            "ratio": 3.2433975100275414,
            "num_points": 30
        },
        {
            "s0": 4.864615786617453,
            "s1": 6.283185307179586,
            "ratio": 1.5481445838447887,
            "num_points": 27
        }
    ]
}

phi_test_21_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.36261262617351875,
    "BG_RATIO": 1.02,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.8906599451380726,
            "ds0": numpy.Infinity,
            "ds1": 0.07,
            "var_ds_ratio": 1.0189024892305478,
            "ratio": 0.981448186229457
        },
        {
            "s0": 0.8906599451380726,
            "s1": 1.504679392827644,
            "ds0": 0.07,
            "ds1": 0.012998158478817108,
            "var_ds_ratio": 1.04,
            "ratio": 0.9615384615384615
        },
        {
            "s0": 1.504679392827644,
            "s1": 1.656081448422333,
            "ds0": numpy.Infinity,
            "ds1": 0.01,
            "var_ds_ratio": 1.0189066958677706,
            "ratio": 0.9814441342426665
        },
        {
            "s0": 1.656081448422333,
            "s1": 2.362624374530881,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.04,
            "ratio": 1.0
        },
        {
            "s0": 2.362624374530881,
            "s1": 6.283185307179586,
            "ds0": 0.01,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0199289161835787,
            "ratio": 1.0199289161835787
        }
    ]
}

phi_test_21_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": -0.4186414564975074,
    "BG_RATIO": 1.02,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.6719140278090987,
            "ratio": 0.544849598475221,
            "num_points": 33
        },
        {
            "s0": 1.6719140278090987,
            "s1": 2.28593347549867,
            "ratio": 0.3468165701312531,
            "num_points": 27
        },
        {
            "s0": 2.28593347549867,
            "s1": 2.437335531093359,
            "ratio": 0.7693397504190178,
            "num_points": 14
        },
        {
            "s0": 2.437335531093359,
            "s1": 3.143878457201907,
            "ratio": 1.0,
            "num_points": 71
        },
        {
            "s0": 3.143878457201907,
            "s1": 6.283185307179586,
            "ratio": 6.878683917608029,
            "num_points": 103
        }
    ]
}

phi_test_22_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": -0.5813103584334165,
    "BG_RATIO": 1.07,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.8345829297450078,
            "ds0": numpy.Infinity,
            "ds1": 0.07,
            "var_ds_ratio": 1.0658265156877869,
            "ratio": 0.9382389960102386
        },
        {
            "s0": 1.8345829297450078,
            "s1": 2.600004433029268,
            "ds0": 0.07,
            "ds1": 0.01,
            "var_ds_ratio": 1.04,
            "ratio": 0.9615384615384615
        },
        {
            "s0": 2.600004433029268,
            "s1": 3.306547359137816,
            "ds0": 0.01,
            "ds1": 0.01,
            "var_ds_ratio": 1.04,
            "ratio": 1.0
        },
        {
            "s0": 3.306547359137816,
            "s1": 4.448602377434579,
            "ds0": 0.01,
            "ds1": 0.07,
            "var_ds_ratio": 1.04,
            "ratio": 1.04
        },
        {
            "s0": 4.448602377434579,
            "s1": 6.283185307179586,
            "ds0": 0.07,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0658265156877869,
            "ratio": 1.0658265156877869
        }
    ]
}
phi_test_22_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": -0.7071130005927531,
    "BG_RATIO": 1.07,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 1.9603855719043444,
            "ratio": 0.25828379743494423,
            "num_points": 23
        },
        {
            "s0": 1.9603855719043444,
            "s1": 2.7258070751886048,
            "ratio": 0.24366872185316354,
            "num_points": 36
        },
        {
            "s0": 2.7258070751886048,
            "s1": 3.4323500012971526,
            "ratio": 1.0,
            "num_points": 71
        },
        {
            "s0": 3.4323500012971526,
            "s1": 4.574405019593915,
            "ratio": 5.616515078328274,
            "num_points": 44
        },
        {
            "s0": 4.574405019593915,
            "s1": 6.283185307179586,
            "ratio": 2.8290206829022155,
            "num_points": 18
        }
    ]
}

phi_test_23_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": -0.3558771639858911,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.7512047535942457,
      "ds0": numpy.Infinity,
      "ds1": 0.06,
      "var_ds_ratio": 1.0563135328916473,
      "ratio": 0.9466886192989599
    },
    {
      "s0": 0.7512047535942457,
      "s1": 1.718495664338091,
      "ds0": 0.06,
      "ds1": 0.027822386512968346,
      "var_ds_ratio": 1.02,
      "ratio": 0.9803921568627451
    },
    {
      "s0": 1.718495664338091,
      "s1": 2.618496772595408,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.0198728856056196,
      "ratio": 0.9805143504782767
    },
    {
      "s0": 2.618496772595408,
      "s1": 2.91288965847397,
      "ds0": 0.01,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 0.9803921568627451
    },
    {
      "s0": 2.91288965847397,
      "s1": 3.0727029393794747,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 3.0727029393794747,
      "s1": 3.2493386709066114,
      "ds0": 0.001,
      "ds1": 0.01,
      "var_ds_ratio": 1.02,
      "ratio": 1.02
    },
    {
      "s0": 3.2493386709066114,
      "s1": 3.2576104055461634,
      "ds0": 0.01,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.016380207815995,
      "ratio": 1.016380207815995
    },
    {
      "s0": 3.2576104055461634,
      "s1": 3.7203672883123104,
      "ds0": numpy.Infinity,
      "ds1": 0.001,
      "var_ds_ratio": 1.0198454780015438,
      "ratio": 0.9805407010869605
    },
    {
      "s0": 3.7203672883123104,
      "s1": 4.519433692839835,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 4.519433692839835,
      "s1": 6.283185307179586,
      "ds0": 0.001,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0597440725143705,
      "ratio": 1.0597440725143705
    }
  ]
}

phi_test_23_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": -0.43785913597620674,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.8331867255845613,
      "ratio": 0.484151033573538,
      "num_points": 14
    },
    {
      "s0": 0.8331867255845613,
      "s1": 1.8004776363284067,
      "ratio": 0.5631123067595095,
      "num_points": 29
    },
    {
      "s0": 1.8004776363284067,
      "s1": 2.7004787445857237,
      "ratio": 0.2782960392845547,
      "num_points": 65
    },
    {
      "s0": 2.7004787445857237,
      "s1": 2.9948716304642855,
      "ratio": 0.14360949907253398,
      "num_points": 98
    },
    {
      "s0": 2.9948716304642855,
      "s1": 3.1546849113697903,
      "ratio": 1.0,
      "num_points": 160
    },
    {
      "s0": 3.1546849113697903,
      "s1": 3.331320642896927,
      "ratio": 4.504152164230224,
      "num_points": 76
    },
    {
      "s0": 3.331320642896927,
      "s1": 3.4589982910674126,
      "ratio": 1.4605622639087323,
      "num_points": 24
    },
    {
      "s0": 3.4589982910674126,
      "s1": 3.802349260302626,
      "ratio": 0.15200814890444078,
      "num_points": 116
    },
    {
      "s0": 3.802349260302626,
      "s1": 4.60141566483015,
      "ratio": 1.0,
      "num_points": 800
    },
    {
      "s0": 4.60141566483015,
      "s1": 6.283185307179586,
      "ratio": 93.13582951070282,
      "num_points": 83
    }
  ]
}

phi_test_24_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.2987379892052351,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 1.9638816194042819,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.019785637354517,
      "ratio": 0.9805982388555264
    },
    {
      "s0": 1.9638816194042819,
      "s1": 2.2582745052828437,
      "ds0": 0.01,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 0.9803921568627451
    },
    {
      "s0": 2.2582745052828437,
      "s1": 2.4180877861883485,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 2.4180877861883485,
      "s1": 2.5947235177154853,
      "ds0": 0.001,
      "ds1": 0.01,
      "var_ds_ratio": 1.02,
      "ratio": 1.02
    },
    {
      "s0": 2.5947235177154853,
      "s1": 2.6029952523550373,
      "ds0": 0.01,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.016380207815995,
      "ratio": 1.016380207815995
    },
    {
      "s0": 2.6029952523550373,
      "s1": 3.0657521351211843,
      "ds0": numpy.Infinity,
      "ds1": 0.001,
      "var_ds_ratio": 1.0198454780015438,
      "ratio": 0.9805407010869605
    },
    {
      "s0": 3.0657521351211843,
      "s1": 3.8648185396487085,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 3.8648185396487085,
      "s1": 6.283185307179586,
      "ds0": 0.001,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0199402288279462,
      "ratio": 1.0199402288279462
    }
  ]
}


phi_test_24_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.22367977627504754,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 2.0389398323344694,
      "ratio": 0.14843652974729582,
      "num_points": 98
    },
    {
      "s0": 2.0389398323344694,
      "s1": 2.3333327182130312,
      "ratio": 0.14360949907253398,
      "num_points": 98
    },
    {
      "s0": 2.3333327182130312,
      "s1": 2.493145999118536,
      "ratio": 1.0,
      "num_points": 160
    },
    {
      "s0": 2.493145999118536,
      "s1": 2.669781730645673,
      "ratio": 4.504152164230224,
      "num_points": 76
    },
    {
      "s0": 2.669781730645673,
      "s1": 2.7974593788161584,
      "ratio": 1.4605622639087323,
      "num_points": 24
    },
    {
      "s0": 2.7974593788161584,
      "s1": 3.140810348051372,
      "ratio": 0.15200814890444078,
      "num_points": 116
    },
    {
      "s0": 3.140810348051372,
      "s1": 3.939876752578896,
      "ratio": 1.0,
      "num_points": 800
    },
    {
      "s0": 3.939876752578896,
      "s1": 6.283185307179586,
      "ratio": 46.911145739095474,
      "num_points": 197
    }
  ]
}

phi_test_25_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.3953275896083546,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.9672909107438454,
      "ds0": 0.0508027436203508,
      "ds1": 0.027822386512968346,
      "var_ds_ratio": 1.02,
      "ratio": 0.9803921568627451
    },
    {
      "s0": 0.9672909107438454,
      "s1": 1.8672920190011624,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.0198728856056196,
      "ratio": 0.9805143504782767
    },
    {
      "s0": 1.8672920190011624,
      "s1": 2.161684904879724,
      "ds0": 0.01,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 0.9803921568627451
    },
    {
      "s0": 2.161684904879724,
      "s1": 2.321498185785229,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 2.321498185785229,
      "s1": 2.498133917312366,
      "ds0": 0.001,
      "ds1": 0.01,
      "var_ds_ratio": 1.02,
      "ratio": 1.02
    },
    {
      "s0": 2.498133917312366,
      "s1": 2.506405651951918,
      "ds0": 0.01,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.016380207815995,
      "ratio": 1.016380207815995
    },
    {
      "s0": 2.506405651951918,
      "s1": 2.969162534718065,
      "ds0": numpy.Infinity,
      "ds1": 0.001,
      "var_ds_ratio": 1.0198454780015438,
      "ratio": 0.9805407010869605
    },
    {
      "s0": 2.969162534718065,
      "s1": 3.768228939245589,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 3.768228939245589,
      "s1": 6.283185307179586,
      "ds0": 0.001,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0199345351664744,
      "ratio": 1.0199345351664744
    }
  ]
}

phi_test_25_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.3953275896083546,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.9672909107438454,
      "ratio": 0.5631123067595095,
      "num_points": 29
    },
    {
      "s0": 0.9672909107438454,
      "s1": 1.8672920190011624,
      "ratio": 0.2782960392845547,
      "num_points": 65
    },
    {
      "s0": 1.8672920190011624,
      "s1": 2.161684904879724,
      "ratio": 0.14360949907253398,
      "num_points": 98
    },
    {
      "s0": 2.161684904879724,
      "s1": 2.321498185785229,
      "ratio": 1.0,
      "num_points": 160
    },
    {
      "s0": 2.321498185785229,
      "s1": 2.498133917312366,
      "ratio": 4.504152164230224,
      "num_points": 76
    },
    {
      "s0": 2.498133917312366,
      "s1": 2.6258115654828513,
      "ratio": 1.4605622639087323,
      "num_points": 24
    },
    {
      "s0": 2.6258115654828513,
      "s1": 2.969162534718065,
      "ratio": 0.15200814890444078,
      "num_points": 116
    },
    {
      "s0": 2.969162534718065,
      "s1": 3.768228939245589,
      "ratio": 1.0,
      "num_points": 800
    },
    {
      "s0": 3.768228939245589,
      "s1": 6.003904564548362,
      "ratio": 44.43393631862482,
      "num_points": 193
    },
    {
      "s0": 6.003904564548362,
      "s1": 6.283185307179586,
      "ratio": 1.0,
      "num_points": 7
    }
  ]
}


phi_test_26_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": -2.1196287783256427,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 2.5149563679339972,
      "ds0": numpy.Infinity,
      "ds1": 0.001,
      "var_ds_ratio": 0.9804550836557165,
      "ratio": 0.9804550836557165
    },
    {
      "s0": 2.5149563679339972,
      "s1": 3.4822472786778427,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 3.4822472786778427,
      "s1": 4.159490406869798,
      "ds0": 0.001,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0199595825764176,
      "ratio": 1.0199595825764176
    },
    {
      "s0": 4.159490406869798,
      "s1": 4.38224838693516,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.0194187765318437,
      "ratio": 0.9809511292327692
    },
    {
      "s0": 4.38224838693516,
      "s1": 4.676641272813722,
      "ds0": 0.01,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 0.9803921568627451
    },
    {
      "s0": 4.676641272813722,
      "s1": 4.836454553719227,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 4.836454553719227,
      "s1": 5.0130902852463635,
      "ds0": 0.001,
      "ds1": 0.01,
      "var_ds_ratio": 1.02,
      "ratio": 1.02
    },
    {
      "s0": 5.0130902852463635,
      "s1": 5.484118902652062,
      "ds0": 0.01,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0195698883145154,
      "ratio": 1.0195698883145154
    },
    {
      "s0": 5.484118902652062,
      "s1": 6.283185307179586,
      "ds0": 0.019327604156319893,
      "ds1": 0.0508027436203508,
      "var_ds_ratio": 1.02,
      "ratio": 1.02
    }
  ]
}

phi_test_26_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": -2.1196287783256427,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 1.0250025025029084,
      "ratio": 1.0,
      "num_points": 35
    },
    {
      "s0": 1.0250025025029084,
      "s1": 2.5149563679339972,
      "ratio": 0.03332684558375427,
      "num_points": 173
    },
    {
      "s0": 2.5149563679339972,
      "s1": 3.4822472786778427,
      "ratio": 1.0,
      "num_points": 968
    },
    {
      "s0": 3.4822472786778427,
      "s1": 4.0831188342084905,
      "ratio": 12.87502550494095,
      "num_points": 130
    },
    {
      "s0": 4.0831188342084905,
      "s1": 4.38224838693516,
      "ratio": 0.540839913467263,
      "num_points": 32
    },
    {
      "s0": 4.38224838693516,
      "s1": 4.676641272813722,
      "ratio": 0.14360949907253398,
      "num_points": 98
    },
    {
      "s0": 4.676641272813722,
      "s1": 4.836454553719227,
      "ratio": 1.0,
      "num_points": 160
    },
    {
      "s0": 4.836454553719227,
      "s1": 5.0130902852463635,
      "ratio": 4.504152164230224,
      "num_points": 76
    },
    {
      "s0": 5.0130902852463635,
      "s1": 5.484118902652062,
      "ratio": 3.077414800455695,
      "num_points": 58
    },
    {
      "s0": 5.484118902652062,
      "s1": 6.283185307179586,
      "ratio": 2.1647447682498564,
      "num_points": 39
    }
  ]
}


phi_test_27_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": -1.1196287783256427,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 1.5149563679339972,
      "ds0": numpy.Infinity,
      "ds1": 0.001,
      "var_ds_ratio": 0.9440405559550384,
      "ratio": 0.9440405559550384
    },
    {
      "s0": 1.5149563679339972,
      "s1": 2.4822472786778427,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 2.4822472786778427,
      "s1": 3.989456521037705,
      "ds0": 0.001,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0599992376029517,
      "ratio": 1.0599992376029517
    },
    {
      "s0": 3.989456521037705,
      "s1": 4.484118902652062,
      "ds0": numpy.Infinity,
      "ds1": 0.06,
      "var_ds_ratio": 1.0576439140991487,
      "ratio": 0.945497805706898
    },
    {
      "s0": 4.484118902652062,
      "s1": 5.283185307179586,
      "ds0": 0.06,
      "ds1": 0.06,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 5.283185307179586,
      "s1": 6.283185307179586,
      "ds0": 0.06,
      "ds1": 0.08927485341497825,
      "var_ds_ratio": 1.02,
      "ratio": 1.02
    }
  ]
}

phi_test_27_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": -1.1196287783256427,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.0687912841208127,
      "ratio": 1.0,
      "num_points": 1
    },
    {
      "s0": 0.0687912841208127,
      "s1": 1.5149563679339972,
      "ratio": 0.012383578833141982,
      "num_points": 77
    },
    {
      "s0": 1.5149563679339972,
      "s1": 2.4822472786778427,
      "ratio": 1.0,
      "num_points": 968
    },
    {
      "s0": 2.4822472786778427,
      "s1": 3.989456521037705,
      "ratio": 88.82343686667407,
      "num_points": 77
    },
    {
      "s0": 3.989456521037705,
      "s1": 4.484118902652062,
      "ratio": 0.6754973925413554,
      "num_points": 7
    },
    {
      "s0": 4.484118902652062,
      "s1": 5.283185307179586,
      "ratio": 1.0,
      "num_points": 14
    },
    {
      "s0": 5.283185307179586,
      "s1": 6.283185307179586,
      "ratio": 1.3458683383241299,
      "num_points": 15
    }
  ]
}

phi_test_28_adj = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.753275896083546,
    "BG_RATIO": 1.04,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.609342604268654,
            "ds0": 0.10493322752106751,
            "ds1": 0.10999140325621139,
            "var_ds_ratio": 1.02,
            "ratio": 1.02
        },
        {
            "s0": 0.609342604268654,
            "s1": 3.4112142282428732,
            "ds0": numpy.Infinity,
            "ds1": 0.0001,
            "var_ds_ratio": 1.0398982107639556,
            "ratio": 0.9616325806209007
        },
        {
            "s0": 3.4112142282428732,
            "s1": 3.610280632770398,
            "ds0": 0.0001,
            "ds1": 0.0001,
            "var_ds_ratio": 1.02,
            "ratio": 1.0
        },
        {
            "s0": 3.610280632770398,
            "s1": 6.283185307179586,
            "ds0": 0.0001,
            "ds1": numpy.Infinity,
            "var_ds_ratio": 1.0398517367830673,
            "ratio": 1.0398517367830673
        }
    ]
}

phi_test_28_legacy = {
    "lower_bnd": 0.0,
    "upper_bnd": 6.283185307179586,
    "periodic": True,
    "phi_shift": 0.753275896083546,
    "BG_RATIO": 1.04,
    "segment_list": [
        {
            "s0": 0.0,
            "s1": 0.3243384271211617,
            "ratio": 1.0482037563757232,
            "num_points": 3
        },
        {
            "s0": 0.3243384271211617,
            "s1": 0.609342604268654,
            "ratio": 1.0,
            "num_points": 3
        },
        {
            "s0": 0.609342604268654,
            "s1": 3.4112142282428732,
            "ratio": 0.0009091619621131983,
            "num_points": 179
        },
        {
            "s0": 3.4112142282428732,
            "s1": 3.610280632770398,
            "ratio": 1.0,
            "num_points": 1991
        },
        {
            "s0": 3.610280632770398,
            "s1": 6.283185307179586,
            "ratio": 1049.3322752106699,
            "num_points": 178
        }
    ]
}
phi_test_29_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 2.5473554779206786,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.5049834979184373,
      "ds0": numpy.Infinity,
      "ds1": 0.02,
      "var_ds_ratio": 1.0194954645181213,
      "ratio": 0.9808773406095179
    },
    {
      "s0": 0.5049834979184373,
      "s1": 0.783489745162476,
      "ds0": 0.02,
      "ds1": 0.011111779291662741,
      "var_ds_ratio": 1.02,
      "ratio": 0.9803921568627451
    },
    {
      "s0": 0.783489745162476,
      "s1": 1.3395664276634442,
      "ds0": numpy.Infinity,
      "ds1": 0.0001,
      "var_ds_ratio": 1.019989566651632,
      "ratio": 0.9804021851740574
    },
    {
      "s0": 1.3395664276634442,
      "s1": 1.9199409741097524,
      "ds0": 0.0001,
      "ds1": 0.0001,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 1.9199409741097524,
      "s1": 2.3395664276634447,
      "ds0": 0.0001,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0199826090126416,
      "ratio": 1.0199826090126416
    },
    {
      "s0": 2.3395664276634447,
      "s1": 2.9199409741097524,
      "ds0": 0.008409686460714147,
      "ds1": 0.01,
      "var_ds_ratio": 1.02,
      "ratio": 1.02
    },
    {
      "s0": 2.9199409741097524,
      "s1": 3.9299079699466306,
      "ds0": 0.01,
      "ds1": 0.030000000000000006,
      "var_ds_ratio": 1.019811775641927,
      "ratio": 1.019811775641927
    },
    {
      "s0": 3.9299079699466306,
      "s1": 6.283185307179586,
      "ds0": 0.030000000000000006,
      "ds1": 0.02999999999999998,
      "var_ds_ratio": 1.06,
      "ratio": 0.9433962264150942
    }
  ]
}

phi_test_29_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 2.5473554779206786,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.5049834979184373,
      "ratio": 0.6291480382903322,
      "num_points": 24
    },
    {
      "s0": 0.5049834979184373,
      "s1": 0.783489745162476,
      "ratio": 0.659775816772605,
      "num_points": 21
    },
    {
      "s0": 0.783489745162476,
      "s1": 1.3395664276634442,
      "ratio": 0.008999458806298377,
      "num_points": 238
    },
    {
      "s0": 1.3395664276634442,
      "s1": 1.9199409741097524,
      "ratio": 1.0,
      "num_points": 5804
    },
    {
      "s0": 1.9199409741097524,
      "s1": 2.3395664276634447,
      "ratio": 84.09686460713982,
      "num_points": 224
    },
    {
      "s0": 2.3395664276634447,
      "s1": 2.422417420533743,
      "ratio": 1.1891049739743806,
      "num_points": 9
    },
    {
      "s0": 2.422417420533743,
      "s1": 2.9199409741097524,
      "ratio": 1.0,
      "num_points": 50
    },
    {
      "s0": 2.9199409741097524,
      "s1": 3.9394089079318104,
      "ratio": 3.0000000000000004,
      "num_points": 56
    },
    {
      "s0": 3.9394089079318104,
      "s1": 6.22640261787245,
      "ratio": 1.0,
      "num_points": 77
    },
    {
      "s0": 6.22640261787245,
      "s1": 6.283185307179586,
      "ratio": 0.8923045594039327,
      "num_points": 2
    }
  ]
}


phi_test_30_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.7168146928204138,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 0.7168146928204138,
      "s1": 2.608407346410207,
      "ds0": 0.01,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0595362625751255,
      "ratio": 1.0595362625751255
    },
    {
      "s0": 2.608407346410207,
      "s1": 4.5,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.0595362625751255,
      "ratio": 0.9438091317135037
    },
    {
      "s0": 4.5,
      "s1": 6.283185307179586,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    }
  ]
}

phi_test_30_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.7168146928204138,
      "ratio": 1.0,
      "num_points": 72
    },
    {
      "s0": 0.7168146928204138,
      "s1": 2.608407346410207,
      "ratio": 12.022103854001086,
      "num_points": 43
    },
    {
      "s0": 2.608407346410207,
      "s1": 4.5,
      "ratio": 0.0831801165706274,
      "num_points": 43
    },
    {
      "s0": 4.5,
      "s1": 6.283185307179586,
      "ratio": 1.0,
      "num_points": 179
    }
  ]
}
phi_test_31_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.2,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 0.2,
      "s1": 1.1858090559953818,
      "ds0": 0.01,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0595442711683773,
      "ratio": 1.0595442711683773
    },
    {
      "s0": 1.1858090559953818,
      "s1": 2.0,
      "ds0": numpy.Infinity,
      "ds1": 0.02,
      "var_ds_ratio": 1.059590660708968,
      "ratio": 0.943760677666698
    },
    {
      "s0": 2.0,
      "s1": 4.2,
      "ds0": 0.02,
      "ds1": 0.02,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    },
    {
      "s0": 4.2,
      "s1": 4.505783597594411,
      "ds0": 0.02,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0596229343854777,
      "ratio": 1.0596229343854777
    },
    {
      "s0": 4.505783597594411,
      "s1": 4.983185307179586,
      "ds0": numpy.Infinity,
      "ds1": 0.01,
      "var_ds_ratio": 1.059539536580776,
      "ratio": 0.9438062153179152
    },
    {
      "s0": 4.983185307179586,
      "s1": 6.283185307179586,
      "ds0": 0.01,
      "ds1": 0.01,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    }
  ]
}

phi_test_31_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.06,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.2,
      "ratio": 1.0,
      "num_points": 20
    },
    {
      "s0": 0.2,
      "s1": 1.1858090559953818,
      "ratio": 6.744201731157817,
      "num_points": 33
    },
    {
      "s0": 1.1858090559953818,
      "s1": 2.0,
      "ratio": 0.2965510344627014,
      "num_points": 21
    },
    {
      "s0": 2.0,
      "s1": 4.2,
      "ratio": 1.0,
      "num_points": 110
    },
    {
      "s0": 4.2,
      "s1": 4.505783597594411,
      "ratio": 1.8908838177023795,
      "num_points": 11
    },
    {
      "s0": 4.505783597594411,
      "s1": 4.983185307179586,
      "ratio": 0.26442661115348276,
      "num_points": 23
    },
    {
      "s0": 4.983185307179586,
      "s1": 6.283185307179586,
      "ratio": 1.0,
      "num_points": 130
    }
  ]
}



phi_test_32_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0,
  "BG_RATIO": 1.07,
  "segment_list": [
    {
      "s0": 0,
      "s1": 6.283185307179586,
      "ds0": 0.015,
      "ds1": 0.015,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    }
  ]
}

phi_test_32_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.07,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 6.283185307179586,
      "ratio": 1.0,
      "num_points": 419
    }
  ]
}

phi_test_33_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.6415926535897931,
  "BG_RATIO": 1.07,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 2.641592653589793,
      "ds0": numpy.Infinity,
      "ds1": 0.015,
      "var_ds_ratio": 1.069644396330412,
      "ratio": 0.9348901405276946
    },
    {
      "s0": 2.641592653589793,
      "s1": 3.641592653589793,
      "ds0": 0.015,
      "ds1": 0.015,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 3.641592653589793,
      "s1": 6.283185307179586,
      "ds0": 0.015,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.069644396330412,
      "ratio": 1.069644396330412
    }
  ]
}

phi_test_33_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.6415926535897931,
  "BG_RATIO": 1.07,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 2.641592653589793,
      "ratio": 0.0774287107205714,
      "num_points": 38
    },
    {
      "s0": 2.641592653589793,
      "s1": 3.641592653589793,
      "ratio": 1.0,
      "num_points": 67
    },
    {
      "s0": 3.641592653589793,
      "s1": 6.283185307179586,
      "ratio": 12.915105917349573,
      "num_points": 38
    }
  ]
}

phi_test_34_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": -0.9247779607693793,
  "BG_RATIO": 1.07,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 2.641592653589793,
      "ds0": numpy.Infinity,
      "ds1": 0.015,
      "var_ds_ratio": 1.069644396330412,
      "ratio": 0.9348901405276946
    },
    {
      "s0": 2.641592653589793,
      "s1": 3.641592653589793,
      "ds0": 0.015,
      "ds1": 0.015,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 3.641592653589793,
      "s1": 6.283185307179586,
      "ds0": 0.015,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.069644396330412,
      "ratio": 1.069644396330412
    }
  ]
}

phi_test_34_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": -0.9247779607693793,
  "BG_RATIO": 1.07,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 2.641592653589793,
      "ratio": 0.0774287107205714,
      "num_points": 38
    },
    {
      "s0": 2.641592653589793,
      "s1": 3.641592653589793,
      "ratio": 1.0,
      "num_points": 67
    },
    {
      "s0": 3.641592653589793,
      "s1": 6.283185307179586,
      "ratio": 12.915105917349573,
      "num_points": 38
    }
  ]
}


phi_test_35_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.04,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.06755666666454285,
      "ds0": 0.0015,
      "ds1": 0.001,
      "var_ds_ratio": 1.02,
      "ratio": 0.9803921568627451
    },
    {
      "s0": 0.06755666666454285,
      "s1": 0.3175717076402922,
      "ds0": 0.001,
      "ds1": 0.001,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 0.3175717076402922,
      "s1": 0.3931576502608678,
      "ds0": 0.001,
      "ds1": 0.0015,
      "var_ds_ratio": 1.02,
      "ratio": 1.02
    },
    {
      "s0": 0.3931576502608678,
      "s1": 1.1323355634890024,
      "ds0": 0.0015,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 1.1323355634890024,
      "s1": 2.782081883823316,
      "ds0": 0.02,
      "ds1": 0.1,
      "var_ds_ratio": 1.05,
      "ratio": 1.05
    },
    {
      "s0": 2.782081883823316,
      "s1": 3.939925780614721,
      "ds0": 0.1,
      "ds1": 0.044,
      "var_ds_ratio": 1.05,
      "ratio": 0.9523809523809523
    },
    {
      "s0": 3.939925780614721,
      "s1": 4.856704690278055,
      "ds0": 0.044,
      "ds1": 0.044,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 4.856704690278055,
      "s1": 4.911074427339195,
      "ds0": 0.044,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0297032714359764,
      "ratio": 1.0297032714359764
    },
    {
      "s0": 4.911074427339195,
      "s1": 5.457346587943244,
      "ds0": numpy.Infinity,
      "ds1": 0.02,
      "var_ds_ratio": 1.048180164570447,
      "ratio": 0.9540344625866951
    },
    {
      "s0": 5.457346587943244,
      "s1": 6.233486857727595,
      "ds0": 0.02,
      "ds1": 0.0015,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 6.233486857727595,
      "s1": 6.283185307179586,
      "ds0": 0.0015,
      "ds1": 0.0015,
      "var_ds_ratio": 1.02,
      "ratio": 1.0
    }
  ]
}

phi_test_35_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.04,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.041516367254504326,
      "ratio": 1.0,
      "num_points": 28
    },
    {
      "s0": 0.041516367254504326,
      "s1": 0.06755666666454285,
      "ratio": 0.6666666666666666,
      "num_points": 21
    },
    {
      "s0": 0.06755666666454285,
      "s1": 0.3175717076402922,
      "ratio": 1.0,
      "num_points": 251
    },
    {
      "s0": 0.3175717076402922,
      "s1": 0.34361200705033074,
      "ratio": 1.5,
      "num_points": 21
    },
    {
      "s0": 0.34361200705033074,
      "s1": 0.3931576502608678,
      "ratio": 1.0,
      "num_points": 34
    },
    {
      "s0": 0.3931576502608678,
      "s1": 1.0264493019773573,
      "ratio": 13.333333333333334,
      "num_points": 88
    },
    {
      "s0": 1.0264493019773573,
      "s1": 1.1323355634890024,
      "ratio": 1.0,
      "num_points": 6
    },
    {
      "s0": 1.1323355634890024,
      "s1": 2.782081883823316,
      "ratio": 5.02456969035137,
      "num_points": 34
    },
    {
      "s0": 2.782081883823316,
      "s1": 3.939925780614721,
      "ratio": 0.43784843988225197,
      "num_points": 17
    },
    {
      "s0": 3.939925780614721,
      "s1": 4.856704690278055,
      "ratio": 1.0,
      "num_points": 21
    },
    {
      "s0": 4.856704690278055,
      "s1": 4.911074427339195,
      "ratio": 1.060288827205952,
      "num_points": 2
    },
    {
      "s0": 4.911074427339195,
      "s1": 5.457346587943244,
      "ratio": 0.4286996551149773,
      "num_points": 18
    },
    {
      "s0": 5.457346587943244,
      "s1": 5.600195206011105,
      "ratio": 1.0,
      "num_points": 8
    },
    {
      "s0": 5.600195206011105,
      "s1": 6.233486857727595,
      "ratio": 0.075,
      "num_points": 88
    },
    {
      "s0": 6.233486857727595,
      "s1": 6.283185307179586,
      "ratio": 1.0,
      "num_points": 34
    }
  ]
}

phi_test_36_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.05,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 1.380428642820414,
      "ds0": 0.04,
      "ds1": 0.04,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 1.380428642820414,
      "s1": 2.0785603464102067,
      "ds0": 0.04,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0485270326285372,
      "ratio": 1.0485270326285372
    },
    {
      "s0": 2.0785603464102067,
      "s1": 2.77669205,
      "ds0": numpy.Infinity,
      "ds1": 0.04,
      "var_ds_ratio": 1.0485270326285372,
      "ratio": 0.9537188540510153
    },
    {
      "s0": 2.77669205,
      "s1": 3.084283,
      "ds0": 0.04,
      "ds1": 0.002,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 3.084283,
      "s1": 3.356023,
      "ds0": 0.002,
      "ds1": 0.002,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 3.356023,
      "s1": 4.374399676221139,
      "ds0": 0.002,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.029969797113066,
      "ratio": 1.029969797113066
    },
    {
      "s0": 4.374399676221139,
      "s1": 4.78382069,
      "ds0": numpy.Infinity,
      "ds1": 0.02,
      "var_ds_ratio": 1.0282254625667655,
      "ratio": 0.9725493448719835
    },
    {
      "s0": 4.78382069,
      "s1": 5.084283,
      "ds0": 0.02,
      "ds1": 0.002187,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 5.084283,
      "s1": 5.356023,
      "ds0": 0.002187,
      "ds1": 0.002187,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 5.356023,
      "s1": 5.65648531,
      "ds0": 0.002187,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 5.65648531,
      "s1": 6.283185307179586,
      "ds0": 0.02,
      "ds1": 0.04,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    }
  ]
}

phi_test_36_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.05,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.3519793375620296,
      "ratio": 1.3222356116372376,
      "num_points": 10
    },
    {
      "s0": 0.3519793375620296,
      "s1": 1.380428642820414,
      "ratio": 1.0,
      "num_points": 26
    },
    {
      "s0": 1.380428642820414,
      "s1": 1.773692002798535,
      "ratio": 1.4658829121072057,
      "num_points": 9
    },
    {
      "s0": 1.773692002798535,
      "s1": 2.77669205,
      "ratio": 0.18942171091039672,
      "num_points": 36
    },
    {
      "s0": 2.77669205,
      "s1": 3.084283,
      "ratio": 0.18006983519841752,
      "num_points": 58
    },
    {
      "s0": 3.084283,
      "s1": 3.356023,
      "ratio": 1.0,
      "num_points": 136
    },
    {
      "s0": 3.356023,
      "s1": 4.224253370576758,
      "ratio": 13.819195082769786,
      "num_points": 89
    },
    {
      "s0": 4.224253370576758,
      "s1": 4.78382069,
      "ratio": 0.40214567141494784,
      "num_points": 31
    },
    {
      "s0": 4.78382069,
      "s1": 5.084283,
      "ratio": 0.19676717080686115,
      "num_points": 55
    },
    {
      "s0": 5.084283,
      "s1": 5.356023,
      "ratio": 1.0,
      "num_points": 125
    },
    {
      "s0": 5.356023,
      "s1": 5.961166276408004,
      "ratio": 9.144947416552354,
      "num_points": 75
    },
    {
      "s0": 5.961166276408004,
      "s1": 6.283185307179586,
      "ratio": 1.512589724855112,
      "num_points": 14
    }
  ]
}
phi_test_37_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.05,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 1.380428642820414,
      "ds0": 0.03,
      "ds1": 0.03,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 1.380428642820414,
      "s1": 2.0785603464102067,
      "ds0": 0.03,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.04855794586072,
      "ratio": 1.04855794586072
    },
    {
      "s0": 2.0785603464102067,
      "s1": 2.77669205,
      "ds0": numpy.Infinity,
      "ds1": 0.03,
      "var_ds_ratio": 1.04855794586072,
      "ratio": 0.9536907368329934
    },
    {
      "s0": 2.77669205,
      "s1": 3.084283,
      "ds0": 0.03,
      "ds1": 0.002,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 3.084283,
      "s1": 3.356023,
      "ds0": 0.002,
      "ds1": 0.002,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 3.356023,
      "s1": 4.374399676221139,
      "ds0": 0.002,
      "ds1": 0.03,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 4.374399676221139,
      "s1": 4.78382069,
      "ds0": 0.03,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 4.78382069,
      "s1": 5.084283,
      "ds0": 0.02,
      "ds1": 0.002187,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 5.084283,
      "s1": 5.356023,
      "ds0": 0.002187,
      "ds1": 0.002187,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 5.356023,
      "s1": 5.65648531,
      "ds0": 0.002187,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 5.65648531,
      "s1": 6.283185307179586,
      "ds0": 0.02,
      "ds1": 0.03,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    }
  ]
}

phi_test_37_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.05,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 1.380428642820414,
      "ratio": 1.0,
      "num_points": 47
    },
    {
      "s0": 1.380428642820414,
      "s1": 1.8793315665598065,
      "ratio": 1.7885299623810171,
      "num_points": 13
    },
    {
      "s0": 1.8793315665598065,
      "s1": 2.77669205,
      "ratio": 0.207000575926246,
      "num_points": 34
    },
    {
      "s0": 2.77669205,
      "s1": 3.084283,
      "ratio": 0.18006983519841752,
      "num_points": 58
    },
    {
      "s0": 3.084283,
      "s1": 3.356023,
      "ratio": 1.0,
      "num_points": 136
    },
    {
      "s0": 3.356023,
      "s1": 4.222059193017138,
      "ratio": 13.799496281706697,
      "num_points": 89
    },
    {
      "s0": 4.222059193017138,
      "s1": 4.479139723591997,
      "ratio": 0.7246641323608622,
      "num_points": 11
    },
    {
      "s0": 4.479139723591997,
      "s1": 5.084283,
      "ratio": 0.10935,
      "num_points": 75
    },
    {
      "s0": 5.084283,
      "s1": 5.356023,
      "ratio": 1.0,
      "num_points": 125
    },
    {
      "s0": 5.356023,
      "s1": 5.961166276408004,
      "ratio": 9.144947416552354,
      "num_points": 75
    },
    {
      "s0": 5.961166276408004,
      "s1": 6.283185307179586,
      "ratio": 1.512589724855112,
      "num_points": 14
    }
  ]
}

phi_test_38_adj = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.03,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.186052,
      "ds0": 0.02,
      "ds1": 0.004,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 0.186052,
      "s1": 0.217595,
      "ds0": 0.004,
      "ds1": 0.002187,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 0.217595,
      "s1": 0.387666,
      "ds0": 0.002187,
      "ds1": 0.002187,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    },
    {
      "s0": 0.387666,
      "s1": 0.415563,
      "ds0": 0.002187,
      "ds1": 0.004,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 0.415563,
      "s1": 0.73896281,
      "ds0": 0.004,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 0.73896281,
      "s1": 2.746091452820414,
      "ds0": 0.02,
      "ds1": 0.04,
      "var_ds_ratio": 1.03,
      "ratio": 1.03
    },
    {
      "s0": 2.746091452820414,
      "s1": 3.444223151410207,
      "ds0": 0.04,
      "ds1": numpy.Infinity,
      "var_ds_ratio": 1.0281220496561112,
      "ratio": 1.0281220496561112
    },
    {
      "s0": 3.444223151410207,
      "s1": 4.14235485,
      "ds0": numpy.Infinity,
      "ds1": 0.04,
      "var_ds_ratio": 1.0281220496561112,
      "ratio": 0.9726471680424347
    },
    {
      "s0": 4.14235485,
      "s1": 6.149483497179586,
      "ds0": 0.04,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 0.970873786407767
    },
    {
      "s0": 6.149483497179586,
      "s1": 6.283185307179586,
      "ds0": 0.02,
      "ds1": 0.02,
      "var_ds_ratio": 1.03,
      "ratio": 1.0
    }
  ]
}

phi_test_38_legacy = {
  "lower_bnd": 0.0,
  "upper_bnd": 6.283185307179586,
  "periodic": True,
  "phi_shift": 0.0,
  "BG_RATIO": 1.03,
  "segment_list": [
    {
      "s0": 0.0,
      "s1": 0.186052,
      "ratio": 0.366044899742639,
      "num_points": 34
    },
    {
      "s0": 0.186052,
      "s1": 0.217595,
      "ratio": 0.6809513399931778,
      "num_points": 13
    },
    {
      "s0": 0.217595,
      "s1": 0.387666,
      "ratio": 1.0,
      "num_points": 78
    },
    {
      "s0": 0.387666,
      "s1": 0.4513175719735187,
      "ratio": 1.828989483310471,
      "num_points": 21
    },
    {
      "s0": 0.4513175719735187,
      "s1": 1.003728127488853,
      "ratio": 5.0,
      "num_points": 55
    },
    {
      "s0": 1.003728127488853,
      "s1": 1.7025345933400493,
      "ratio": 2.0,
      "num_points": 24
    },
    {
      "s0": 1.7025345933400493,
      "s1": 2.746091452820414,
      "ratio": 1.0,
      "num_points": 27
    },
    {
      "s0": 2.746091452820414,
      "s1": 3.444223151410207,
      "ratio": 1.5158984204292298,
      "num_points": 15
    },
    {
      "s0": 3.444223151410207,
      "s1": 4.14235485,
      "ratio": 0.6596748083666762,
      "num_points": 15
    },
    {
      "s0": 4.14235485,
      "s1": 5.2020799945864225,
      "ratio": 1.0,
      "num_points": 27
    },
    {
      "s0": 5.2020799945864225,
      "s1": 5.9008864604376186,
      "ratio": 0.5,
      "num_points": 24
    },
    {
      "s0": 5.9008864604376186,
      "s1": 6.283185307179586,
      "ratio": 0.4387007213564054,
      "num_points": 28
    }
  ]
}

