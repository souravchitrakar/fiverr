#!/bin/sh

#########################################################################################
#   Name:           Backup automation script
#   Date:           19th October, 2020
#   Description:    Automates the backup of database directory
#########################################################################################

#   move to home directory
cd ~

#   creating the tar file with the name of bakup
tar -cvf backup database