#!/bin/bash

#########################################################################################
#   Name:           User creation automation script
#   Date:           16th October, 2020
#   Description:    Automates the user creation and supporting activities
#########################################################################################

##   function: creating directory and give access
folder_creation() {

    user_name=$1
    user_group=$2

    if [ $user_group == 'hr' ]
    then

        cd /home/$user_name
        rm -f -R Daily_Benefits Share Documents HR

        #   directory creation hr
        mkdir Daily_Benefits Share Documents

        #   soft link creation for the hr
        ln -s /home/Personnel HR

        #   changing the ownership for hr
        chown -h $user_name:$user_group *
        stat_chown=$?

        #   changing the directories permissions for hr
        chmod 700 Daily_Benefits
        stat_ch_a=$?
        chmod 740 Share
        stat_ch_b=$?

        statu=`expr $stat_chown + $stat_ch_a + $stat_ch_b`

        if [ $statu == '0' ]
        then
            echo 'user permission changed successfully' > temp
        else
            echo 'Failed to change the user permission'
            exit 1
        fi

        rm -f temp

        #   readme file creation for hr
        line1='Monthly drops will be placed in the folder of the most up to date financial'
        line2='records for the institution.'
        line=`echo $line1 $line2`
        echo $line > Daily_Benefits/readme.txt
        line1='It is their responsibility to rename them'
        line2='monthly so they are not to be overwritten.'
        line=`echo $line1 $line2`
        echo $line >> Daily_Benefits/readme.txt


    else

        cd /home/$user_name
        rm -f -R Daily_Records Share Documents Projects

        #   directory creation analyst
        mkdir Daily_Records Share Documents

        #   soft link creation for the analyst
        ln -s /home/Projects Projects

        #   changing the ownership for analyst
        chown -h $user_name:$user_group *
        stat_chown=$?

        #   changing the directories permissions for analyst
        chmod 700 Daily_Records
        stat_ch_a=$?
        chmod 740 Share
        stat_ch_b=$?

        statu=`expr $stat_chown + $stat_ch_a + $stat_ch_b`

        if [ $statu == '0' ]
        then
            echo 'user permission changed successfully' > temp
        else
            echo 'Failed to change the user permission'
            exit 1
        fi

        rm -f temp

        #   readme file creation for analyst
        line1='Daily drops will be placed in the folder of the most up to date financial'
        line2='records for the institution.'
        line=`echo $line1 $line2`
        echo $line > Daily_Records/readme.txt
        line1='It is their responsibility to rename them monthly so they are not to be'
        line2='overwritten.'
        line=`echo $line1 $line2`
        echo $line >> Daily_Records/readme.txt

    fi

}

# #  function: user creation and group addition
user_create() {

    user_name=$1
    user_group=$2

    #   check the existance of the user
    user_count=`cat /etc/passwd|grep $user_name|wc -l`

    if [ $user_count == '0' ]
    then

        # creating user and setting the password
        useradd -m -s /bin/bash $user_name
        user_create_stat=$?
        echo $user_name:Welcome1|chpasswd
        password_change_stat=$?
        chage -d 0 $user_name
        password_reset_stat=$?

        statu=`expr $user_create_stat + $password_change_stat + $password_reset_stat`
        if [ $statu == '0' ]
        then
            echo 'user created successfully' > temp
        else
            echo 'Failed to create the user'
            exit 1
        fi

        # adding the user to the group
        #adduser $user_name $user_group >> temp
        usermod -g $user_group $user_name >> temp
        statu=$?
        if [ $statu == '0' ]
        then
            echo 'user added to the group successfully' >> temp
        else
            echo 'Failed to add the user in the group'
            exit 1
        fi

        groupdel $user_name
        rm -f temp

    else
        
        echo 'The user name already exists'
        exit 0

    fi

}


##  main section

#   checking if input is provided from CLA   
user_length=`echo $1|wc -c`

if [ $user_length == '1' ]
then

    #   input from user
    read -p "Enter the user name : " user_name
    read -p "Enter the user group [analyst/hr] : " user_group

else

    #   assigning user name and group provided from CLA
    user_name=$1
    user_group=$2

fi

#   checking the validity of the group
if [ $user_group == 'hr' ]
then

    #   calling the function to create the user
    user_create $user_name $user_group

    #   calling the function to create the folders and set permissions
    folder_creation $user_name $user_group

    #   log file for hr
    creation_time=`date`
    msg=`echo 'User:' $user_name '(group:'$user_group') is created on' $creation_time`
    echo $msg >> /root/userAccounts.txt

    echo 'User:' $user_name 'is created on' `date`

    exit 0

elif [ $user_group == 'analyst' ]
then
    
    #   calling the function to create the user
    user_create $user_name $user_group

    #   calling the function to create the folders and set permissions
    folder_creation $user_name $user_group

    #   log file for analyst
    creation_time=`date`
    msg=`echo 'User:' $user_name '(group:'$user_group') is created on' $creation_time`
    echo $msg >> /root/userAccounts.txt

    echo 'User:' $user_name 'is created on' `date`

    exit 0

else

    echo 'Input group is not valid'
    exit 0

fi