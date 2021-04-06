#!/bin/bash

# Shell-Script zur Auswahl der zu korrigierenden Pfeffer-Aufnahmen

SEQDATA=/opt/data/dsv01/dsv01.seq

# CAT-Felder, DDC und Fachcodes extrahieren
grep -P '^.{10}CAT' $SEQDATA > ./tmp/dsv01.cat
grep -P '^.{10}072' $SEQDATA > ./tmp/dsv01.072
grep -P '^.{10}082' $SEQDATA > ./tmp/dsv01.082

# Positivliste generieren: Alle Aufnahmen die über Weihnachten 2014 angereichert worden sind
grep -P '\$\$aP18-Batch.*\$\$c2014122(4|5)' ./tmp/dsv01.cat | cut -c1-9 | sort | uniq > ./tmp/dsv01_pfeffer_positiv.sys

# Negativliste generieren: Alle Aufnahmen die korrigiert oder händisch erschlossen worden sind
# Alle Aufnahmen mit Fachcode 'mu'
grep -P '\$\$amu' ./tmp/dsv01.072 | cut -c1-9 | sort | uniq > ./tmp/dsv01_pfeffer_musik.sys

# Alle Aufnahmen mit Fachcode 'fm'
grep -P '\$\$afm' ./tmp/dsv01.072 | cut -c1-9 | sort | uniq > ./tmp/dsv01_pfeffer_film.sys

# Alle Aufnahmen mit DDC '791'
grep -P '\$\$a791' ./tmp/dsv01.082 | cut -c1-9 | sort | uniq > ./tmp/dsv01_pfeffer_film_ddc.sys

# Berner Fachreferenten-Kürzel
grep -iP '\$\$a(b-|)(hab|pal|brb|gbi|dob|bkd|bkd2|ds|fdo|fdo2|jde|nfe|gge|lgu|mih|sti|jom|iki|hk|bla|ith|ida|dma|bmt|cma|mm|evm|evm2|jmu|map|clp|arh|rma|rma2|aru|smi|res|gbs|mis|evs|evs2|ks|ks2|wa|cwe|cwy|pkz|ub|phc|phc2|sic|jdu|jdu2|afr|afr2|hom|ise|npl|ulr)\$\$' ./tmp/dsv01.cat  > ./tmp/dsv01_pfeffer_berner_sigel
grep -P '\$\$c20(08|09|10|11|12|13|14|15|16|17|18|19|20)' ./tmp/dsv01_pfeffer_berner_sigel | cut -c1-9 | sort | uniq > ./tmp/dsv01_pfeffer_berner_sigel.sys

# Spezialfall Samuel Weibel (wei/wei2)
grep -iP '\$\$a(b-|)(wei2|wei)\$\$' ./tmp/dsv01.cat  > ./tmp/dsv01_pfeffer_samuel_weibel
grep -P '\$\$c20(08|09|10|11|12|13|14|15|16|17|18|19|20)' ./tmp/dsv01_pfeffer_samuel_weibel | cut -c1-9 | sort | uniq > ./tmp/dsv01_pfeffer_samuel_weibel.sys
cat ./tmp/dsv01_pfeffer_musik.sys ./tmp/dsv01_pfeffer_samuel_weibel.sys | sort | uniq -d > ./tmp/dsv01_pfeffer_samuel_weibel_musik.sys

# Spezialfall Jeannot Schöll (js/js2)
grep -iP '\$\$a(b-|)(js2|js)\$\$' ./tmp/dsv01.cat  > ./tmp/dsv01_pfeffer_jeanott_scholl
grep -P '\$\$c20(08|09|10|11|12|13|14|15|16|17|18|19|20)' ./tmp/dsv01_pfeffer_jeanott_scholl | cut -c1-9 | sort | uniq > ./tmp/dsv01_pfeffer_jeannot_scholl.sys
cat ./tmp/dsv01_pfeffer_film.sys ./tmp/dsv01_pfeffer_jeannot_scholl.sys | sort | uniq -d > ./tmp/dsv01_pfeffer_jeannot_scholl_film.sys
cat ./tmp/dsv01_pfeffer_film_ddc.sys ./tmp/dsv01_pfeffer_jeannot_scholl.sys | sort | uniq -d > ./tmp/dsv01_pfeffer_jeannot_scholl_film_ddc.sys

# Basler Fachreferenten-Kürzel
grep -iP '\$\$a(b-|)(ale|as|bol3|bv|cb|cs|dtr|ed|ge|mb|sgu|tre|uvr|yh|mwe|chw|do|lup|joh|nor2|abi|dk|hej|asw|cog|gd|kep|hwi|dke|jsa|ssc|ehu|say|hei|cer|ets|ema|sth|prg|awi|nis|scr|vis|mon|kvr|cyr|mrs|sid|jac|emo|sach1|sach3|uja|bro|jum|lyl|gda)\$\$' ./tmp/dsv01.cat  > ./tmp/dsv01_pfeffer_basler_sigel
grep -P '\$\$c20(11|12|13|14|15|16|17|18|19|20)' ./tmp/dsv01_pfeffer_basler_sigel | cut -c1-9 | sort | uniq > ./tmp/dsv01_pfeffer_basler_sigel.sys

# Negativlisten zusammenfügen
cat ./tmp/dsv01_pfeffer_samuel_weibel_musik.sys ./tmp/dsv01_pfeffer_jeannot_scholl_film.sys ./tmp/dsv01_pfeffer_jeannot_scholl_film_ddc.sys ./tmp/dsv01_pfeffer_basler_sigel.sys ./tmp/dsv01_pfeffer_berner_sigel.sys | sort | uniq > ./tmp/dsv01_pfeffer_negativ.sys

# Zu bereinigendes Set erstellen
grep -Fvxf ./tmp/dsv01_pfeffer_negativ.sys ./tmp/dsv01_pfeffer_positiv.sys > ./tmp/dsv01_pfeffer.set
cp ./tmp/dsv01_pfeffer.set .
sed -i 's/$/DSV01/g' dsv01_pfeffer.set


