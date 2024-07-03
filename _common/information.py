
# natural abundance mapping for isotopes
natural_abundances = {
        6: [(6012, 0.9893), (6013, 0.0107)],
        92: [(92235, 0.007), (92238, 0.993)],
    }

surface_info = {}
surface_info['so'] = 'A sphere defined by its center of origin and radius Provide R as parameters'
surface_info['sx'] = 'A sphere defined by its centered on x axis and radius Provide X, R as parameters'
surface_info['sy'] = 'A sphere defined by its centered on y axis and radius Provide Y, R as parameters'
surface_info['sz'] = 'A sphere defined by its centered on z axis and radius Provide Z, R as parameters'
surface_info['s'] = 'A sphere defined by its center and radius. Provide X, Y, Z, R as parameters'
surface_info['cx'] = 'A cylinder on x axis parallel to x axis and defined by radius. Provide  R as parameter'
surface_info['cy'] = 'A cylinder on y axis parallel to y axis and defined by radius. Provide  R as parameter'
surface_info['cz'] = 'A cylinder on z axis parallel to z axis and defined by radius. Provide  R as parameter'
surface_info['c/x'] = 'A cylinder parallel to x axis. Provide Y,Z and R as parameters'
surface_info['c/y'] = 'A cylinder parallel to y axis. Provide X,Z and R as parameters'
surface_info['c/z'] = 'A cylinder parallel to z axis. Provide X,Y and R as parameters'
surface_info["px"] = 'A plane perpendicular to the x-axis. Provide X as parameter'
surface_info["py"] = 'A plane perpendicular to the y-axis. Provide Y as parameter'
surface_info["pz"] = 'A plane perpendicular to the z-axis. Provide Z as parameter'
surface_info['p'] = 'A general plane defined by its coefficients Plane equation: Ax + By + Cz - D = 0 Provide A, B, C, and D as parameters'