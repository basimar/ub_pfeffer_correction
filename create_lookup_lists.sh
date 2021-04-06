#!/bin/bash

# Creates lists used as input for modify_fields.py

# In
REST=dsv01_pfeffer_rest.set
MESH=imported_fields/imported_mesh.sys
GND=imported_fields/imported_gnd.sys

# Out
# Mesh mit ISBN sowie aus heiklen Fächern
MESH_ISBN=imported_fields/imported_mesh_isbn_subjects.sys
# GND mit ISBN sowie aus heiklen Fächern
GND_ISBN=imported_fields/imported_gnd_isbn_subjects.sys
# GND Rest
GND_REST=imported_fields/imported_gnd_rest.sys


comm -23 <(cat $MESH | sort | uniq) <(cat $REST | sort | uniq) > $MESH_ISBN
comm -23 <(cat $GND | sort | uniq) <(cat $REST | sort | uniq) > $GND_ISBN
comm -13 <(cat $GND | sort | uniq) <(cat $REST | sort | uniq) > $GND_REST
