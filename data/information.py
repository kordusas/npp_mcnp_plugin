
# natural abundance mapping for isotopes
natural_abundances = {
        6: [(6012, 0.9893), (6013, 0.0107)],
        92: [(92235, 0.007), (92238, 0.993)],
    }

surface_info = {}
surface_info['p'] = 'A general plane defined by its coefficients Plane equation: Ax + By + Cz - D = 0 Provide A, B, C, and D as parameters'
surface_info["px"] = 'A plane perpendicular to the x-axis. Provide X as parameter'
surface_info["py"] = 'A plane perpendicular to the y-axis. Provide Y as parameter'
surface_info["pz"] = 'A plane perpendicular to the z-axis. Provide Z as parameter'


surface_info['so'] = 'A sphere defined by its center of origin and radius Provide R as parameters'
surface_info['s'] = 'A sphere defined by its center and radius. Provide X, Y, Z, R as parameters'
surface_info['sx'] = 'A sphere defined by its centered on x axis and radius Provide X, R as parameters'
surface_info['sy'] = 'A sphere defined by its centered on y axis and radius Provide Y, R as parameters'
surface_info['sz'] = 'A sphere defined by its centered on z axis and radius Provide Z, R as parameters'

surface_info['c/x'] = 'A cylinder parallel to x axis. Provide Y,Z and R as parameters'
surface_info['c/y'] = 'A cylinder parallel to y axis. Provide X,Z and R as parameters'
surface_info['c/z'] = 'A cylinder parallel to z axis. Provide X,Y and R as parameters'
surface_info['cx'] = 'A cylinder on x axis parallel to x axis and defined by radius. Provide  R as parameter'
surface_info['cy'] = 'A cylinder on y axis parallel to y axis and defined by radius. Provide  R as parameter'
surface_info['cz'] = 'A cylinder on z axis parallel to z axis and defined by radius. Provide  R as parameter'

surface_info['k/x'] = 'Cone parallel to the x-axis. Provide parameters x,y,z,t^2, and +/-1'
surface_info['K/z'] = 'Cone parallel to the y-axis. Provide parameters x,y,z,t^2, and +/-1'
surface_info['k/z'] = 'Cone parallel to the z-axis. Provide parameters x,y,z,t^2, and +/-1'
surface_info['kx'] = 'Cone on the x-axis. Provide parameters x,t^2, and +/-1'
surface_info['ky'] = 'Cone on the y-axis. Provide parameters y,t^2, and +/-1'
surface_info['kz'] = 'Cone on the z-axis. Provide parameters z,t^2, and +/-1'
surface_info['sq'] = 'An ellipsoid,hyperboloid, or paraboloid axes parallel to x,y, or z axis. Provide parameters A,B,C,D,E,F,G, x,y,z'
surface_info['gq'] = 'A Cylinder, Cone, Ellipsoid, Hyperboloid Paraboloid. Axes not parallel to x,y or z axis. Provide parameters A,B,C,D,E,F,G, H, J, K'
surface_info['tx'] = 'Elliptical or Circular Torus, Axis is parallel to x axis. Provide parameters x,y,z, A,B,C'
surface_info['ty'] = 'Elliptical or Circular Torus, Axis is parallel to y axis. Provide parameters x,y,z, A,B,C'
surface_info['tz'] = 'Elliptical or Circular Torus, Axis is parallel to z axis. Provide parameters x,y,z, A,B,C'
surface_info['x'] = 'Surfaces defined by points see Section 3.2.2.2 and 3.2.2.3 '
surface_info['y'] = 'Surfaces defined by points see Section 3.2.2.2 and 3.2.2.3'
surface_info['z'] = 'Surfaces defined by points see Section 3.2.2.2 and 3.2.2.3'
surface_info['p'] = 'Surfaces defined by points see Section 3.2.2.2 and 3.2.2.3'
surface_info['box'] = "Form: BOX vx vy vz a1x a1y a1z a2x a2y a2z a3x a3y a3z\nvx vy vz: The x, y, z coordinates of a corner of the box.\na1x a1y a1z: Vector of 1st side from the specified corner coordinates.\na2x a2y a2z: Vector of 2nd side from the specified corner coordinates.\na3x a3y a3z: Vector of 3rd side from the specified corner coordinates."

surface_info['rpp'] = 'Surfaces defined by macrobodies (See Section 3.2.2.4)'
surface_info['sph'] = 'Surfaces defined by macrobodies (See Section 3.2.2.4)'
surface_info['rcc'] = 'Surfaces defined by macrobodies (See Section 3.2.2.4)'
surface_info['rph'] = 'Surfaces defined by macrobodies (See Section 3.2.2.4)'
surface_info['hex'] = 'Surfaces defined by macrobodies (See Section 3.2.2.4)'
surface_info['rec'] = 'Surfaces defined by macrobodies (See Section 3.2.2.4)'
surface_info['trc'] = 'Surfaces defined by macrobodies (See Section 3.2.2.4)'
surface_info['ell'] = 'Surfaces defined by macrobodies (See Section 3.2.2.4)'
surface_info['wed'] = 'Surfaces defined by macrobodies (See Section 3.2.2.4)'
surface_info['arb'] = 'Surfaces defined by macrobodies (See Section 3.2.2.4)'


particle_designators = {
    "neutron": {
        "designator": "N",
        "mass": 939.56563,
        "lower_erg_limit": 0.0,
        "upper_erg_limit": 0.0,
        "MCNP decay treatment": "no decay"
    },
    "photon": {
        "designator": "P",
        "mass": 0.0,
        "lower_erg_limit": 1.e-6,
        "upper_erg_limit": 1.e-3,
        "MCNP decay treatment": "1x10^29"
    },
    "electron": {
        "designator": "E",
        "mass": 0.511008,
        "lower_erg_limit": 1.e-5,
        "upper_erg_limit": 1.e-3,
        "MCNP decay treatment": "1x10^29"
    },
    "negative muon": {
        "designator": "|",
        "mass": 105.658389,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 0.11261,
        "MCNP decay treatment": "2.19703x10-6"
    },
    "anti neutron": {
        "designator": "Q",
        "mass": 939.56563,
        "lower_erg_limit": 0.0,
        "upper_erg_limit": 0.0,
        "MCNP decay treatment": "no decay"
    },
    "electron neutrino": {
        "designator": "U",
        "mass": 0.0,
        "lower_erg_limit": 0.0,
        "upper_erg_limit": 0.0,
        "MCNP decay treatment": "1x10^29"
        
    },
    "muon neutrino": {
        "designator": "V",
        "mass": 0.0,
        "lower_erg_limit": 0.0,
        "upper_erg_limit": 0.0
    },
    "positron": {
        "designator": "F",
        "mass": 0.511008,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.e-3
    },
    "proton": {
        "designator": "H",
        "mass": 938.27231,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.0
    },
    "lambda baryon": {
        "designator": "L",
        "mass": 1115.684,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.0
    },
    "positive sigma baryon": {
        "designator": "+",
        "mass": 1189.37,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.26760
    },
    "negative sigma baryon": {
        "designator": "-",
        "mass": 1197.436,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.26760
    },
    "cascade; xi baryon": {
        "designator": "X",
        "mass": 1314.9,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.0
    },
    "negative cascade; negative xi baryon": {
        "designator": "Y",
        "mass": 1321.32,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.40820
    },
    "omega baryon": {
        "designator": "O",
        "mass": 1672.45,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.78250
    },
    "positive muon": {
        "designator": "!",
        "mass": 105.658389,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 0.11261
    },
    "anti electron neutrino": {
        "designator": "<",
        "mass": 0.0,
        "lower_erg_limit": 0.0,
        "upper_erg_limit": 0.0
    },
    "anti muon neutrino": {
        "designator": ">",
        "mass": 0.0,
        "lower_erg_limit": 0.0,
        "upper_erg_limit": 0.0
    },
    "anti proton": {
        "designator": "G",
        "mass": 938.27231,  # Mass not provided in the input
        "lower_erg_limit": 1.e-3 ,  
        "upper_erg_limit": 1.0  
    },

    "positive pion": {
        "designator": "/",
        "mass": 139.56995,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 0.14875
    },
    "neutral pion": {
        "designator": "Z",
        "mass": 134.9764,
        "lower_erg_limit": 0.0,
        "upper_erg_limit": 0.0
    },
    "positive kaon": {
        "designator": "K",
        "mass": 493.677,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 0.52614
    },
    "kaon, short": {
        "designator": "%",
        "mass": 497.672,
        "lower_erg_limit": 0.0,
        "upper_erg_limit": 0.0
    },
    "kaon, long": {
        "designator": "^",
        "mass": 497.672,
        "lower_erg_limit": 0.0,
        "upper_erg_limit": 0.0
    },
    "anti lambda baryon": {
        "designator": "B",
        "mass": 1115.684,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.0
    },
    "anti positive sigma baryon": {
        "designator": "_",
        "mass": 1189.37,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.26760
    },
    "anti negative sigma baryon": {
        "designator": "~",
        "mass": 1197.436,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.26760
    },
    "anti cascade; anti neutral xi baryon": {
        "designator": "C",
        "mass": 1314.9,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.0
    },
    "positive cascade; positive xi baryon": {
        "designator": "W",
        "mass": 1321.32,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.40820
    },
    "anti omega": {
        "designator": "@",
        "mass": 1672.45,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 1.78250
    },
    "deuteron": {
        "designator": "D",
        "mass": 1875.627,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 2.0
    },
    "triton": {
        "designator": "T",
        "mass": 2808.951,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 3.0
    },
    "helion (3He)": {
        "designator": "S",
        "mass": 2808.421,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 3.0
    },
    "alpha particle": {
        "designator": "A",
        "mass": 3727.418,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 4.0
    },
    "negative pion": {
        "designator": "*",
        "mass": 139.56995,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 0.14875
    },
    "negative kaon": {
        "designator": "?",
        "mass": 493.677,
        "lower_erg_limit": 1.e-3,
        "upper_erg_limit": 0.52614
    }

}
