#!/bin/bash

# Make sure only root can run our script
if [ "$(id -u)" == "0" ]; then
   echo "This script must not be run as root" 1>&2
   exit 1
fi

. ../../config/settings.ini

mkdir /tmp/geonature

echo "Create export schema..."
echo "--------------------" &> /var/log/geonature/install_export_schema.log
echo "Create export schema" &>> /var/log/geonature/install_export_schema.log
echo "--------------------" &>> /var/log/geonature/install_export_schema.log
echo "" &>> /var/log/geonature/install_export_schema.log
cp data/export.sql /tmp/geonature/export.sql
sudo sed -i "s/MYLOCALSRID/$srid_local/g" /tmp/geonature/export.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f /tmp/geonature/export.sql  &>> /var/log/geonature/install_export_schema.log

echo "Create export export view(s)..."
echo "--------------------" &> /var/log/geonature/install_export_schema.log
echo "Create export export view(s)" &>> /var/log/geonature/install_export_schema.log
echo "--------------------" &>> /var/log/geonature/install_export_schema.log
echo "" &>> /var/log/geonature/install_export_schema.log
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/exports_export.sql  &>> /var/log/geonature/install_export_schema.log


echo "INSTALL SAMPLE  = $add_sample_data "
if $add_sample_data
	then
	echo "Insert sample data in export schema..."
	echo "" &>> /var/log/geonature/install_export_schema.log
	echo "" &>> /var/log/geonature/install_export_schema.log
	echo "" &>> /var/log/geonature/install_export_schema.log
	echo "--------------------" &>> /var/log/geonature/install_export_schema.log
	echo "Insert sample data in export schema..." &>> /var/log/geonature/install_export_schema.log
	echo "--------------------" &>> /var/log/geonature/install_export_schema.log
	echo "" &>> /var/log/geonature/install_export_schema.log
	export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/sample_data.sql  &>> /var/log/geonature/install_export_schema.log
fi

echo "Cleaning files..."
    rm /tmp/geonature/*.sql
