#! /usr/bin/perl

use warnings;
use strict;

# Skript verlangt zwei Aleph-Sequential files als Input und exportiert aufgrund der 
# Systemnummern im ersten Inputfile sämtliche Felder im zweiten Inputfile mit der 
# gleichen Systemnummern.
# Autor: Basil Marti (basil.marti@unbas.ch)

# 2017.09.17: Uploaded to ub-catmandu /bmt 

die "Argumente: $0 Input (Systemnummer), Input (Daten), Output\n" unless @ARGV == 3;

my($input1file,$input2file,$outputfile) = @ARGV;

open my $handle1, '<', $input1file;;
chomp(my @lines1 = <$handle1>);
close $handle1;

open my $handle2, '<', $input2file;;
chomp(my @lines2 = <$handle2>);
close $handle2;

open my $out, ">", $outputfile or die "$0: open $outputfile: $!";

for (@lines1) {
    my $sys = $_;
    #print $sys . "\n";
    for (@lines2) {
        if ($sys eq substr($_,0,9)) {
            print $out $_ . "\n";
            print $_ . "\n";
        }
    }
}

close $out or warn "$0: close $outputfile:: $!";

