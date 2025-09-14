# -*- coding: utf-8 -*-
"""
Created on Tue Jul  8 14:03:39 2025

@author: Julian Kübach
"""

# Imports:
from arango import ArangoClient
from arango.exceptions import DatabasePropertiesError
import tkinter as tk
from tkinter import simpledialog, filedialog
import xml.etree.ElementTree as ET
import os
from lxml import etree
import types
from pathlib import Path

#%% function to logging into Arango using http://localhost:8529
'''
Input:
database = Name of the database you want to connect to
arango_username = your Arango-username
arango_password = your Arango-password

Output:
sys_db = Arango database wrapper
'''
def Arango_login():
    # Initialize the ArangoDB client unsing http://localhost:8529
    client = ArangoClient(hosts="http://localhost:8529")
    
    root = tk.Tk()
    root.withdraw()
    
    database = simpledialog.askstring(title="Input", prompt="Enter the database you want to connect to:")
    arango_username = simpledialog.askstring(title="Input", prompt="Enter the Arango-username you want to connect to:")
    arango_password = simpledialog.askstring(title="Input", prompt="Enter the Arango-password you want to connect to:", show="*")
    
    sys_db = client.db(database, username=arango_username, password=arango_password)  
    try:
        sys_db.properties()
        print(f"Login successful, access to ArabgoDB {sys_db} granted")
    except DatabasePropertiesError:
        print("Login credentials are incorrect")
    return sys_db
        
#%% function to create database
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
db_name = Name for the new database you want to create
'''
def Database_create(sys_db, db_name):
    if not sys_db.has_database(db_name):
        sys_db.create_database(db_name)
        print(f"✅ Database with the name: '{db_name}' created.")
    else:
        print(f"ℹ️ Database with the name: '{db_name}' already exists.Please choose another name!")

#%% function to delete database
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
db_name = Name of the database you want to delete
'''
def Database_delete(sys_db, db_name):
    sys_db.delete_database(db_name)
    print(f"✅ Database with the name: '{db_name}' deleted")
    
#%% function to create standard collection
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
collec_name = Name for the new collection you want to create
'''
def Standard_collection_create(sys_db, collec_name):
    if not sys_db.has_collection(collec_name):
        sys_db.create_collection(collec_name)
        print(f"✅ Collection with the name: '{collec_name}' created.")
    else:
        print(f"ℹ️ Collection with the name: '{collec_name}' already exists. Please choose another name!")
        
#%% function to delete standard collection
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
collec_name = Name of the collection you want to delete
'''
def Standard_collection_delete(sys_db, collec_name):
    sys_db.delete_collection(collec_name)
    print(f"✅ Collection with the name: '{collec_name}' deleted")

#%% function to create vertex collection
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
vert_collec_name = Name for the new vertex-collection you want to create
graph_name = Name of the graph 
'''
def Vertex_collection_create(sys_db, vert_collec_name, graph_name):
    if not sys_db.has_graph(graph_name):
        graph = sys_db.create_graph(graph_name)
    else:
        graph = sys_db.graph(graph_name)

    if not graph.has_vertex_collection(vert_collec_name):
        graph.create_vertex_collection(vert_collec_name)
        print(f"✅ Vertex-Collection with the name: '{vert_collec_name}' created.")
    else:
        print(f"ℹ️ Vertex-Collection with the name: '{vert_collec_name}' already exists. Please choose another name!")

#%% function to delete vertex collection
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
vert_collec_name = Name of the vertex-collection you want to delete
'''
def Vertex_collection_delete(sys_db, vert_collec_name):
    sys_db.delete_collection(vert_collec_name)
    print(f"✅ Vertex-Collection with the name: '{vert_collec_name}' deleted")
#%% function to create edge collection
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
edg_collec_name = Name of the new edge-collection you want to create
'''
def Edge_collection_create(sys_db, edg_collec_name):
    if edg_collec_name not in sys_db.collections():
        sys_db.create_collection(edg_collec_name, edge=True)
        print(f"✅ Edge-Collection with the name: '{edg_collec_name}' created.")
    else:
        print(f"ℹ️ Edge-Collection with the name: '{edg_collec_name}' already exists. Please choose another name!")

#%% function to delete edges collection
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
edg_collec_name = Name of the edge-collection you want to delete
'''
def Edge_collection_delete(sys_db, edg_collec_name):
    sys_db.delete_collection(edg_collec_name)
    print(f"ℹ️ Edge-Collection with the name: '{edg_collec_name}' deleted")
#%% function to generate the graph
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
'''
def Create_graph(sys_db):
    graph = "graph"
    # create the hole graph
    if graph not in sys_db.graphs():
        sys_db.create_graph(
            name=graph,
            # define the edges
            edge_definitions=[
                {
                    "edge_collection": "uses",
                    "from_vertex_collections": ["models"],
                    "to_vertex_collections": ["meshes"]
                },
                {
                    "edge_collection": "used_by",
                    "from_vertex_collections": ["meshes"],
                    "to_vertex_collections": ["models"]
                },
                {
                    "edge_collection": "generates",
                    "from_vertex_collections": ["models"],
                    "to_vertex_collections": ["output"]
                },
                {
                    "edge_collection": "generated_by",
                    "from_vertex_collections": ["output"],
                    "to_vertex_collections": ["models"]
                }
            ]
        )
        print(f"✅ Graph '{graph}' created.")
    else:
        print(f"ℹ️ Graph '{graph}' already exists.")

#%% function to add the python model data into the database
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
'''
def Python_model_data_in_database(sys_db):
    # Create an empty dictionary
    master_dict = {}
    # Select the folder 
    folder_selected = filedialog.askdirectory(title="Select the folder for the python-files")
    # Crawl through every file that ends with ".py"
    for dirpath, _, filenames in os.walk(folder_selected):
        for filename in filenames:
            if filename.endswith(".py"):
                fullpath = os.path.join(dirpath, filename)
                # Extract the information using "Python_model_extractor"
                model_info = Python_model_extractor(fullpath)
                if model_info:  
                    master_dict[fullpath] = model_info
    # Add the data into the database
    Python_model_vertex_create(sys_db, master_dict)

#%% function to extract data from the python model
'''
Input:
py_path = Path of the python file
Output:
extracted_data = the dictionary of the extracted data
'''
def Python_model_extractor(py_path):
    py_path = Path(py_path)
    # Define starting and ending point
    start_marker = "# Definition of the simulation conditions, model, approximation, coordinates and path for input files"
    end_marker = "file_type = 'pvd'"

    in_block = False
    block_lines = []
    # Extracting only the code needed
    try:
        with open(py_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not in_block and stripped == start_marker:
                    in_block = True
                if in_block:
                    block_lines.append(line)
                    if stripped == end_marker:
                        break
    except Exception as e:
        print(f"Fehler beim Lesen von {py_path}: {e}")
        return {}

    block_code = ''.join(block_lines)

    class Dummy:
        file_input = Path("dummy_path")

    ns = types.SimpleNamespace()
    vars(ns)["files"] = Dummy()

    try:
        exec(block_code, vars(ns))
    except Exception as e:
        print(f"Fehler beim Ausführen des Codes in {py_path}: {e}")
        return {}

    extracted_data = {
        key: value for key, value in vars(ns).items()
        if not key.startswith("__") and key != "files"
    }

    return extracted_data


#%% function to create the python model vertex
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
dictionary = Data from the extractor
Output:
m = The id from the inseted models
'''
def Python_model_vertex_create(sys_db, dictionary):
    # Define the collection
    models = sys_db["models"]
    for key, val in dictionary.items():
        # Define the variables
        path_to_python_model = key
        model = None
        gas = None
        freq = None
        file_type = None
        coordinates = None
        circuit_state = None
        Tgas = None
        semi_implicit = None
        U_w = None
        Ud = None
        Resistance = None
        PulseType = None
        p0 = None
        N0 = None
        approximation = None
        Capacitance = None
        # Fill the variables
        try:
            model = val["model"]
            gas = val["gas"]
            freq = val["freq"]
            file_type = val["file_type"]
            coordinates = val["coordinates"]
            circuit_state = val["circuit_state"]
            Tgas = val["Tgas"]
            semi_implicit = val["semi_implicit"]
            U_w = val["U_w"]
            Ud = val["Ud"]
            Resistance = val["Resistance"]
            PulseType = val["PulseType"]
            p0 = val["p0"]
            N0 = val["N0"]
            approximation = val["approximation"]
            Capacitance = val["Capacitance"]
        except KeyError:
            print("Information is missing")
        # Generate keys
        query = "RETURN LENGTH(models)"
        models_key = sys_db.aql.execute(query)
        highest_key = next(models_key, 0)
        masterKey = "models" + str(highest_key)
        # Create the document
        if model is not None and gas is not None and freq is not None and file_type is not None and coordinates is not None and circuit_state is not None and semi_implicit is not None and U_w is not None and Ud is not None and Resistance is not None and PulseType is not None and p0 is not None and N0 is not None and approximation is not None and Capacitance is not None and Tgas is not None:
            doc = {
                '_key': masterKey,
                'path': path_to_python_model,
                'model': str(model),
                'gas': str(gas),
                'frequenz': str(freq),
                'coordinates': str(coordinates),
                'circuit_state': str(circuit_state),
                'semi_implicit': str(semi_implicit),
                'U_w': str(U_w),
                'Ud': str(Ud),
                'resistence': str(Resistance),
                'pulse_type': str(PulseType),
                'p0': str(p0),
                'N0': str(N0),
                'approximation': str(approximation),
                'capacitance': str(Capacitance),
            }
            # Insert the document
            m = models.insert(doc)
        else:
            print(f"Missing data for: {path_to_python_model}")
        return m

#%% function to add the xml data into the database
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
model = Connection to python model
'''
def Xml_data_in_database(sys_db, model):
    # Create an empty dictionary
    master_dict = {}
    # Select the folder
    folder_selected = filedialog.askdirectory(title="Select the folder for xml-files")
    # Crawl through every file that ends with ".xml"
    for dirpath, _, filenames in os.walk(folder_selected):
        for filename in filenames:
            if filename.endswith(".xml"):
                fullpath = os.path.join(dirpath, filename)
                # Extract the information using "Xml_information_extractor"
                dim, celltype, vertices_size = Xml_information_extraction(fullpath)
                master_dict[fullpath] = {
                        "dim": dim,
                        "celltype": celltype,
                        "vertices_size": vertices_size
                        }
    Xml_vertex_create(sys_db, master_dict, model)
#%% function to extract xml data 
'''
Input:
xml_path = Path from the file.xml
Output:
dim, celltype, vertices_size = The extracted information 
'''
def Xml_information_extraction(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        ns = {"dolfin": "http://www.fenicsproject.org"}

        mesh = root.find("mesh") or root.find("dolfin:mesh", ns)
        if mesh is None:
            raise ValueError("No <mesh>-Element found")

        dim = mesh.attrib.get("dim")
        celltype = mesh.attrib.get("celltype")

        vertices = mesh.find("vertices") or mesh.find("dolfin:vertices", ns)
        vertices_size = vertices.attrib.get("size") if vertices is not None else None
        return dim, celltype, vertices_size
    except Exception as e:
        return {"error": str(e)}
    

#%% function to create xml vertexes
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
dictionary = Data from the extractor
model = Connection to python model
'''
def Xml_vertex_create(sys_db, dictionary, model):
    # Define the collection
    meshes = sys_db["meshes"]
    # Define the variables and default values
    for path_to_xml, val in dictionary.items():
        dim = val.get("dim")
        celltype = val.get("celltype")
        vertices_size = val.get("vertices_size")

        if dim is None or celltype is None or vertices_size is None:
            print(f"Missing data for: {path_to_xml}")
            continue

        # Generate the key
        query = "RETURN LENGTH(meshes)"
        count_cursor = sys_db.aql.execute(query)
        count = next(count_cursor, 0)  # default to 0 if no result

        masterKey = f"meshes{count}"
        # Create the document
        doc = {
            '_key': masterKey,
            'path': path_to_xml,
            'dim': str(dim),
            'celltype': str(celltype),
            'vertices_size': str(vertices_size)
        }

        try:
            # Insert the document 
            m = meshes.insert(doc)
            Create_edges(sys_db, model["_id"], m["_id"], "uses", "used_by")
        except Exception as e:
            print(f"Failed to insert {masterKey}: {e}")

#%% function xdmf data in database
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
model = Connection to python model
'''
def Xdmf_data_in_database(sys_db, model):
    # Create an empty dictionary
    master_dict = {}
    # Select the folder
    folder_selected = filedialog.askdirectory(title="Select the folder for the xdmf-files")
    # Crawl through every file that ends with ".xdmf"
    for dirpath, _, filenames in os.walk(folder_selected):
        for filename in filenames:
            if filename.endswith(".xdmf"):
                fullpath = os.path.join(dirpath, filename)
                # Extract the information using "Xdmf_information_extractor"
                grids_info = Xdmf_information_extraction(fullpath)
                master_dict[fullpath] = grids_info

    Xdmf_vertex_create(sys_db, master_dict, model)
#%% function xdmf information extraction
'''
Input:
xdmf_path = Path from the file.xdmf
Output:
grids_dict = The extracted information 
'''
def Xdmf_information_extraction(xdmf_path):
    tree = etree.parse(xdmf_path)
    root = tree.getroot()

    nsmap = root.nsmap
    default_ns = nsmap.get(None)
    ns = {'x': default_ns} if default_ns else {}

    if ns:
        grids = root.xpath("//x:Grid[@GridType='Uniform']", namespaces=ns)
    else:
        grids = root.xpath("//Grid[@GridType='Uniform']")

    grids_dict = {}

    for i, grid in enumerate(grids):
        name = grid.attrib.get("Name")
        grid_type = grid.attrib.get("GridType")
        time_elem = grid.find("x:Time", namespaces=ns) if ns else grid.find("Time")
        time_val = time_elem.attrib.get("Value") if time_elem is not None else None

        grids_dict[f"Grid_{i}"] = {
            "Name": name,
            "GridType": grid_type,
            "Time": float(time_val) if time_val else None
        }

    return grids_dict
#%% function to create xdmf vertexes
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
dictionary = Data from the extractor
model = Connection to python model
'''
def Xdmf_vertex_create(sys_db, dictionary, model):
    # Define the collection
    output = sys_db["output"]
    for key, val in dictionary.items():
        # Define the variables and default values
        path_to_xdmf = key
        name = None
        grid_type = None
        time_val = None

        for attr_name, attr_value in val.items():
            try:
                name = attr_value["Name"]
                grid_type = attr_value["GridType"]
                time_val = attr_value["Time"]
            except KeyError:
                print("Information is missing")
            # Generate the key
            query = "RETURN LENGTH(output)"
            
            output_key = sys_db.aql.execute(query)
            highest_key = next(output_key, None)
            masterKey = "output" + str(highest_key)
            if name is not None and grid_type is not None and time_val is not None:
                # Create the document
                doc = {'_key': masterKey, 
                       'path': path_to_xdmf, 
                       'name': str(name), 
                       'grid_type': str(grid_type), 
                       'time_value': str(time_val)}
                # Insert the document 
                o = output.insert(doc)
                Create_edges(sys_db, model["_id"], o["_id"], "generates", "generated_by")
            else:
                print(f"Missing data for: {path_to_xdmf}")

#%% function to create the edges
'''
Input:
sys_db = Arango database wrapper created by Arango_login()
from_doc = ID from the document
to_doc = ID from the document
edge_out = Name of the edge
edge_back = Name of the edge
'''
def Create_edges(sys_db, from_doc, to_doc, edge_out, edge_back):
    try:
        sys_db.collection(edge_out).insert({'_from': from_doc, '_to': to_doc})
        print(f"{edge_out}: {from_doc} → {to_doc}")
    except Exception as e:
        print(f"⚠️ Fail during data integration in '{edge_out}': {e}")

    try:
        sys_db.collection(edge_back).insert({'_from': to_doc, '_to': from_doc})
        print(f"{edge_back}: {to_doc} → {from_doc}")
    except Exception as e:
        print(f"⚠️ Fail during data integration in '{edge_back}': {e}")
