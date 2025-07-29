#!/usr/bin/env python

import unittest
import pyCollier
import numpy.testing as test

mudim1 = 100**2
mudim2 = 1000**2
Aargs = [1000]
Bargs = [1000, 100, 200]
Cargs = [200, 1000, 200, 100, 10, 50]
Dargs = [1e3, 2e3, 3e3, 1e2, 1e4, -3e3, 1e2, 1e2, 3e2, 3e2]

class numericTest(unittest.TestCase):
    def test_renscale(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(mudim1, pyCollier.get_renscale())
    def test_delta(self):
        pyCollier.set_delta(100)
        test.assert_allclose(100, pyCollier.get_delta())
        pyCollier.set_delta(0)
    # one-point functions
    def test_a0a(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.a0(*Aargs), 3302.585092994046)
    def test_a0b(self):
        pyCollier.set_renscale(mudim2)
        test.assert_allclose(pyCollier.a0(*Aargs), 7907.755278982137)
    def test_a0b(self):
        pyCollier.set_renscale(mudim1)
        pyCollier.set_delta(1)
        test.assert_allclose(pyCollier.a0(*Aargs), 4302.585092994046)
        pyCollier.set_delta(0)
    # two-point functions
    def test_b0a(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.b0(*Bargs), 5.2277622590786335 + 2.0116008064341786j)
    def test_b0b(self):
        pyCollier.set_renscale(mudim2)
        test.assert_allclose(pyCollier.b0(*Bargs), 9.83293244506672 + 2.011600806434179j)
    def test_b1a(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.b1(*Bargs), - 2.563436807828795 - 0.90522036289538j)
    def test_b1b(self):
        pyCollier.set_renscale(mudim2)
        test.assert_allclose(pyCollier.b1(*Bargs), - 4.866021900822841 - 0.90522036289538j)
    def test_b00a(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.b00(*Bargs), - 52.07823457964887 - 68.72969421983441j)
    def test_b00b(self):
        pyCollier.set_renscale(mudim2)
        test.assert_allclose(pyCollier.b00(*Bargs), - 90.4546527962163 - 68.72969421983441j)
    def test_b11a(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.b11(*Bargs), 1.696827098645421 + 0.4760788575227555j)
    def test_b11b(self):
        pyCollier.set_renscale(mudim2)
        test.assert_allclose(pyCollier.b11(*Bargs), 3.231883827308118 + 0.4760788575227555j)
    # two-point functions (derivatives)
    def test_db0a(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.db0(*Bargs), - 0.001669955625129153 + 0.001422839594794907j)
    def test_db0b(self):
        pyCollier.set_renscale(mudim2)
        test.assert_allclose(pyCollier.db0(*Bargs), - 0.001669955625129153 + 0.001422839594794907j)
    def test_db1a(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.db1(*Bargs), 0.0007010357095975972 - 0.0007408578579794169j)
    def test_db1b(self):
        pyCollier.set_renscale(mudim2)
        test.assert_allclose(pyCollier.db1(*Bargs), 0.0007010357095975972 - 0.0007408578579794169j)
    def test_db00a(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.db00(*Bargs), - 0.433304854591687 - 0.2145707526863124j)
    def test_db00b(self):
        pyCollier.set_renscale(mudim2)
        test.assert_allclose(pyCollier.db00(*Bargs), - 0.817069036757361 - 0.2145707526863124j)
    def test_db11a(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.db11(*Bargs), - 0.0002972699094582554 + 0.0005244881127019846j)
    def test_db11b(self):
        pyCollier.set_renscale(mudim2)
        test.assert_allclose(pyCollier.db11(*Bargs), - 0.0002972699094582554 + 0.0005244881127019846j)
    # three-point functions
    def test_c0(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.c0(*Cargs), 0.004769595279977717 - 0.007570567427108271j)
    def test_c1(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.c1(*Cargs), - 0.002885340179446056 + 0.001662509518253616j)
    def test_c2(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.c2(*Cargs), - 0.001328250516625898 + 0.002365487224386374j)
    def test_c00(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.c00(*Cargs), 1.336551322096479 + 0.6272847905400663j)
    def test_c11(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.c11(*Cargs), 0.001752294619925529 - 0.0007614653126638748j)
    def test_c22(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.c22(*Cargs), 0.0006240656002036454 - 0.001329550735290667j)
    # four-point functions
    def test_d0(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d0(*Dargs), -3.921393574718075e-7 - 3.209559917467113e-7j)
    def test_d1(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d1(*Dargs), 1.641967327193075e-7 + 9.34507804419116e-8j)
    def test_d2(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d2(*Dargs), - 5.107529186229758e-8 + 1.256488329644019e-7j)
    def test_d3(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d3(*Dargs), 1.321536683763819e-7 - 1.078476187183549e-8j)
    def test_d00(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d00(*Dargs), 0.0000888606734572166 - 0.0001549990347042824j)
    def test_d11(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d11(*Dargs), - 1.030282759584827e-7 - 3.327868808352181e-8j)
    def test_d12(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d12(*Dargs), 2.752260625664649e-9 - 3.388528220622128e-8j)
    def test_d13(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d13(*Dargs), -3.138306175653794e-8 + 9.26884371635395e-9j)
    def test_d22(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d22(*Dargs), 4.434796445187413e-8 - 4.903796159043477e-8j)
    def test_d23(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d23(*Dargs), -2.760832445797667e-9 - 2.759070411121907e-8j)
    def test_d33(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d33(*Dargs), -5.900167422681706e-8 + 2.723432699465579e-8j)
    def test_d001(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d001(*Dargs), -0.0000180099473133521 + 0.00005061969094122341j)
    def test_d002(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d002(*Dargs), -0.00003547196846026774 + 0.00001842295210582159j)
    def test_d003(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d003(*Dargs), -7.635375072965733e-6 + 0.00004884100653190721j)
    def test_d111(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d111(*Dargs), 7.347347039811503e-8 + 1.049294068316945e-8j)
    def test_d112(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d112(*Dargs), 3.138638658479554e-9 + 1.442562065261e-8j)
    def test_d113(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d113(*Dargs), 1.216489104206016e-8 - 6.204168227671007e-9j)
    def test_d122(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d122(*Dargs), -8.23516756412056e-9 + 1.07768376552522e-8j)
    def test_d123(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d123(*Dargs), 3.157478932096519e-9 + 4.757482322632517e-9j)
    def test_d133(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d133(*Dargs), 8.54340632532367e-9 - 7.360597169351001e-9j)
    def test_d222(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d222(*Dargs), -2.587900253336954e-8 + 2.626225798626085e-8j)
    def test_d223(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d223(*Dargs), -6.383546305430242e-9 + 9.54758896489232e-9j)
    def test_d233(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d233(*Dargs), 5.58480507414049e-9 + 9.54149287259235e-9j)
    def test_d333(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d333(*Dargs), 3.167615274115767e-8 - 2.415260929584603e-8j)
    def test_d0000(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d0000(*Dargs), 0.1373775818029426 + 0.1013480552280915j)
    def test_d0011(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d0011(*Dargs), 5.40121802870178e-6 - 0.00002479179181715668j)
    def test_d0012(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d0012(*Dargs), 7.625657365903788e-6 - 5.920542455021991e-6j)
    def test_d0013(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d0013(*Dargs), -8.5733581859672e-7 - 0.00001069540430664114j)
    def test_d0022(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d0022(*Dargs), 0.00001532601914258516 - 4.29329173403592e-6j)
    def test_d0023(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d0023(*Dargs), 6.902747658398853e-6 - 6.159211383623127e-6j)
    def test_d0033(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d0033(*Dargs), -1.344572284475638e-6 - 0.00002189467720991503j)
    def test_d1111(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d1111(*Dargs), -5.558253968213802e-8 - 9.13242004754444e-12j)
    def test_d1112(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d1112(*Dargs), -3.491415195872347e-9 - 7.559548317002753e-9j)
    def test_d1113(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d1113(*Dargs), -5.880596859080017e-9 + 4.229543526809675e-9j)
    def test_d1122(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d1122(*Dargs), 1.951088815322566e-9 - 4.038053907535405e-9j)
    def test_d1123(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d1123(*Dargs), -1.647299128617624e-9 - 1.236205575607164e-9j)
    def test_d1222(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d1222(*Dargs), 5.260441332043015e-9 - 4.150952140193131e-9j)
    def test_d1223(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d1223(*Dargs), 3.65469008694968e-10 - 1.937911373110325e-9j)
    def test_d1233(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d1233(*Dargs), -1.584904281259761e-9 - 9.40998153221134e-10j)
    def test_d1333(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d1333(*Dargs), -2.982821676427751e-9 + 4.346625876080898e-9j)
    def test_d2222(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d2222(*Dargs), 1.435874955086408e-8 - 1.788381845914258e-8j)
    def test_d2223(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d2223(*Dargs), 4.456677322939056e-9 - 3.547199422419981e-9j)
    def test_d2233(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d2233(*Dargs), 1.00814789374113e-9 - 3.364671073703352e-9j)
    def test_d2333(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d2333(*Dargs), -4.38094375109149e-9 - 3.955525036488416e-9j)
    def test_d3333(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.d3333(*Dargs), -1.854745872231621e-8 + 1.997883427103167e-8j)
    # test bget, cget, dget
    def test_bget(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.bget(0, 1, *Bargs), pyCollier.b1(*Bargs))
    def test_cget(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.cget(0, 0, 0, *Cargs), pyCollier.c0(*Cargs))
    def test_dget(self):
        pyCollier.set_renscale(mudim1)
        test.assert_allclose(pyCollier.dget(0, 0, 0, 0, *Dargs), pyCollier.d0(*Dargs))