#!/bin/sh

filename=$1

if [ ! -d $filename ]; then
	mkdir $filename
	chmod 777 $filename 
else
	rm $filename/*
fi	
