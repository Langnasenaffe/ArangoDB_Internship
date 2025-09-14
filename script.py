# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 11:47:14 2025

@author: Student
"""

import arango_handler as AH

# Login
db = AH.Arango_login()
# Model
model = AH.Python_model_data_in_database(db)
# Meshes
AH.Xml_data_in_database(db, model)
# Output
AH.Xdmf_data_in_database(db, model)

# !Only works if every collection and the graph is there!





