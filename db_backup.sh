##################################
# Backup of FluTypeDB
#
# TODO: compress backup
# TODO: run via cron job
# TODO: differential backup
# TODO: check that backup can be restored
##################################

cd /var/git/flutype_webapp

# create directory for backup
DIR=/var/backups/flutypedb/$(date '+%F')
sudo mkdir -p $DIR
sudo chown -R mkoenig:mkoenig $DIR
echo "Backup to" $DIR

# backup media
sudo cp -Rv /var/git/flutype_webapp/media $DIR

# backup database
echo "---------------"
echo "Dump database"
echo "---------------"
sudo -u postgres pg_dump flutype > $DIR/dump.psql


