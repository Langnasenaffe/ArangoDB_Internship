# ArangoDB_Internship
## 1. Step: Login to ArangoDB
Call: Arango_login() <br>
Input: Database name, Password, Username <br>
Output: sys_db = login wrapper (save it for later) <br>
Important:
Use „_system“ if no database is created yet

## 2. Step: Create a new Database (if not created yet)
Call : Database_create() <br>
Input: sys_db is the variable from the Login, db_name <br>
Conditions: must be logged into „_system“ to create or delete , name must be unique <br>

## 3. Step: Create a graph (if not creatd yet)
Call: Create_graph(sys_db) <br>
Input: sys_db <br>
Purpose: organizes relationships between data <br>

## 4. Step: Create Collections (if not creatd yet)
Vertex Collections: models, meshes, output <br>
Edge Collections: uses, used_by, generates, generated_by <br>
Call for Vertex Collections: Vertex_collection_create() <br>
Call for Edge Collections: Edge_collection_create() <br>
Inputs: sys_db, vert_collec_name / edg_collec_name <br>

## 5. Step: Import Python Models 
Call: Python_model_in_database() <br>
What happens: open file dialog for Python model folder, extracts information from „.py“ files, stores it in „models“ collection, returns object saved as a variable (model) <br>

## 6. Step: Import Mesh Data (XML)
Call: Xml_data_in_database() <br>
What happens: open folder dialog for „.xml“ files, extract mesh structure, save to meshes collection <br>
Create edges: mesh => model, model => mesh <br>

## 7. Step: Import Output Data (XDMF)
Call: Xdmf_data_in_database() <br>
What happens: open folder dialog for „.xdmf“ files, store result in „output“ <br>
Create edges:  output => model, model => output <br>



