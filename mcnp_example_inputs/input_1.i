Test Input graphite target with concrete shielding
C ==============================================================================
C ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
C ||||||||||||||||||||||||||||||||||||||||||||||||||||| CELL SPECIFICATION |||||
C ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
C ==============================================================================
c ---------- void before target ----------------
1  0   1 -2 -10 imp:n=1
c ----------     Target     --------------------
2 60 -2.2 2 -3 -10 imp:n=0 
c ----------------------------------------------
c shielding
c ----------------------------------------------
10  81 -2.35  1 -3  
             -11 10 imp:n=1
11  81 -2.35 1 -3& 
 -12 11 imp:n=1
12  81 -2.35 1 -3  -13 12 imp:n=1
13  81 -2.35 1 -3  -14 13 imp:n=1
14  81 -2.35 1 -3  -15 14 imp:n=1
15  81 -2.35 1 -3  -16 15 imp:n=1
16  81 -2.35 1 -3  -17 16 imp:n=1
17  81 -2.35 1 -3  -18 17 imp:n=1
18  81 -2.35 1 -3  -19 18 imp:n=1
19  81 -2.35 1 -3  -20 19 imp:n=1
20  81 -2.35 1 -3  -21 20 imp:n=1
21  81 -2.35 1 -3  -22 21 imp:n=1
22  81 -2.35 1 -3  -23 22 imp:n=1
23  81 -2.35 1 -3  -24 23 imp:n=1
24  81 -2.35 1 -3  -25 24 imp:n=1
25  81 -2.35 1 -3  -26 25 imp:n=1
26  81 -2.35 1 -3  -27 26 imp:n=1
27  81 -2.35 1 -3  -28 27 imp:n=1
28  81 -2.35 1 -3  -29 28 imp:n=1
c -----------------------------------------------
998 0  -999 (29 1 -3) imp:n=1
c ------------ outside void ---------------------
999 0  999 imp:n=0

C ==============================================================================
C ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
C ||||||||||||||||||||||||||||||||||||||||||||||||||||| SURFACE SPECIFICATION ||
C ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
C ==============================================================================
1 pz 0
2 pz 20
3 pz 40
c ------------------------------------------------------------------------------
10  CZ  10
11  CZ  20
12  CZ  30
13  CZ  40
14  CZ  50
15  CZ  60
16  CZ  70
17  CZ  80
18  CZ  90
19  CZ 100
20  CZ 110
21  CZ 120
22  CZ 130
23  CZ 140
24  CZ 150
25  CZ 160
26  CZ 170
27  CZ 180
28  CZ 190
29  CZ 200
c ----------------
999 so  400

C ------------------------------------------------------------------------------
C                            GRAPHITE density -2.2 
C ------------------------------------------------------------------------------
M60         6000  1
C ------------------------------------------------------------------------------
C                            Aluminum 
C ------------------------------------------------------------------------------
M13           13027 1.000000000  $ AL
C ------------------------------------------------------------------------------
C                            Concrete density -2.35
C ------------------------------------------------------------------------------
M81 1001    -0.01       $ Hydrogen
    6000    -0.001      $ Carbon 
    8016    -0.52       $ Oxygen
    11023   -0.02       $ Sodium 
    12024   -0.002      $ Magnesiu
    13027   -0.034      $ Aluminum
    14028   -0.34       $ Silicon
    19039   -0.013      $ Potassiu
    20040   -0.044      $ Calcium
    26056   -0.014      $ Iron
C ==============================================================================
C ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
C |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| TYPE ||
C ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
C ==============================================================================
MODE        N
C ==============================================================================
C ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
C |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| SOURCE ||
C ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
C ==============================================================================
SDEF pos 0 0 0 erg  14 par n vec 0 0 1
f4:n 1
