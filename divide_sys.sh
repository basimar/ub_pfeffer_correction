#!/bin/bash

# Shell-Script zur Aufteilung der zu korrigierenden Pfeffer-Aufnahmen in drei Teile:
# 1. Aufnahmen mit ISBN
# 2. Aufnahmen ohne ISBN aber mit bestimmten Fachgebieten
# 3. Rest

SEQDATA=/opt/data/dsv01/dsv01.seq

# Alle Aufnahmen mit ISBN extrahieren
grep -P '^.{10}020.*\$\$a' $SEQDATA | cut -c1-9 | sort | uniq > ./tmp/dsv01.020.sys

# Alle Aufnahmen mit DDC extrahieren
grep -P '^.{10}082.*\$\$a(4|7|8)' $SEQDATA | cut -c1-9 | sort | uniq > ./tmp/dsv01.082.sys

# Alle Aufnahmen mit RVK extrahieren
grep -P '^.{10}084.*\$\$a(E|G|H|I|K|LD|LH|LI|LJ|LK|LL|LM|LN|LO|LP|LQ|LR|LS|LT|LU|LV|LW|LX|LY|LZ).*\$\$2rvk' $SEQDATA | cut -c1-9 | sort | uniq > ./tmp/dsv01.084.sys

# Erstelle Set 1: Aufnahmen mit ISBN
cat ./tmp/dsv01.020.sys ./tmp/dsv01_pfeffer.set | sort | uniq -d > ./tmp/dsv01_pfeffer_isbn.set
cp ./tmp/dsv01_pfeffer_isbn.set .
sed -i 's/$/DSV01/g' dsv01_pfeffer_isbn.set

# Erstelle Set 2: Aufnahmen ohne ISBN aber mit bestimmten Fachgebieten
grep -Fvxf ./tmp/dsv01.020.sys ./tmp/dsv01_pfeffer.set > ./tmp/dsv01_pfeffer_no_isbn.sys

cat ./tmp/dsv01.082.sys ./tmp/dsv01.084.sys | sort | uniq > ./tmp/dsv01_pfeffer_subjects.sys 
cat ./tmp/dsv01_pfeffer_no_isbn.sys ./tmp/dsv01_pfeffer_subjects.sys | sort | uniq -d > ./tmp/dsv01_pfeffer_subjects.set

# Erstelle Set 3: Rest
grep -Fvxf ./tmp/dsv01_pfeffer_subjects.sys ./tmp/dsv01_pfeffer_no_isbn.sys > ./tmp/dsv01_pfeffer_rest.set

cp ./tmp/dsv01_pfeffer_rest.set .
cp ./tmp/dsv01_pfeffer_subjects.set .

sed -i 's/$/DSV01/g' dsv01_pfeffer_rest.set
sed -i 's/$/DSV01/g' dsv01_pfeffer_subjects.set
exit


