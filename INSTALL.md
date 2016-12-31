# Install

This file documents how to install and run energy@home.

This program was tested on Ubuntu 10.04 and therefore written for the same
distribution. Please adapt the install for your own environment.

# Description

The program should contain the following directories which reflect their
components: - datalogger The Python backend which "talks" to the CurrentCost
CC128 display. It recieves the data from the device over the optional USB
cable and stores it in the database.

## install

Directory storing all setup and install related files. This should only be
needed once and can be removed after.

## web

The web component allows users to view data stored in the database from a web
site/page.

Each component is independant of eachother and can be installed without any
requisite of one being installed before the other. Although this is the case,
if datalogger is not installed, the data will not be captured from the CC128
device and therefore will not display any data unless it is being logged by
another application.

# Pre-Requisites

The following programs / libraries are currently supported and should be
considered as minimum requirement:

## datalogger

Python 2.6.5 PySerial 2.3 PyMySQLDB 1.2.2

## Database

MySQL 5.7

## web

Apache (tested with 2.4) PHP 7.0

To install these pre-requisites: Update your repository:

    
    `$ sudo apt-get update`

Type in the following commands to install the relevant component requisites:

## datalogger

    
    `$ sudo apt-get install python python-serial python-mysqldb`

## Database

Try:

    
    `$ sudo apt-get install mysql-server`

This usually installs the latest version of MySQL according to the
distribution. If that fails try installing a specific version:

    
    `$ sudo apt-get install mysql-server-5.7`

where 5.7 is the version of MySQL server.

It will ask for the root password and confirmation of the root password.
Ensure this is strong password because it will have access to everything on
the database. Also this account and password may be required to setup
Energy@Home.

## web

    `$ sudo apt-get install apache2 php7.0 php7.0-mysql libapache2-mod-php7.0`

# Recommended Tools

## GNU Screen

The datalogger sits and runs 24/7 but it has not been implemented as a Linux
demon yet. To keep it running in the background even when the user has logged
off this program allows you to do that. Alternatively run it in the terminal
but do not close the terminal itself (that includes logging off or shutting
down the computer).

    
    `$ sudo apt-get install screen`

## MySQL Admin

A set of tools to maintain the MySQL database. It can make creating, editing
and backing up easier.

    
    `$ sudo apt-get install mysql-admin`

# Download Energy@Home

> To download a stable release version:

  1. Go to [https://github.com/dannytsang/energyathome/releases](https://github.com/dannytsang/energyathome/releases)
  2. Find and download the latest version. E.g energyathome_x.x.tar.gz 
  3. Extract the files: 
    
    `$ tar -xvwzf energyathome_x.x.tar.gz`

  4. Rename the directory from energyathome_x.x to energyathome 
    
    `$ mv energyathome_x.x energyathome`

  5. To download the latest version in the repository install mercurial source control software: 
    
    `$ sudo apt-get install git`

  6. Then checkout the latest code: 
    
    `$ git clone https://geek94@energyathome.googlecode.com/hg/energyathome`

# Install MySQL

  1. Install MySQL shown in Pre-Requisites section. 
  2. Log into MySQL with grant and create priviledges e.g root user. 
  3. Create a 'energyathome' user. By default the username is 'energyathome' and chose a password. 
  4. Run the database install script ~/install/install.sql to create the schema and tables in the install directory. The script is called install.sql. 
  5. Grant the energyathome user access to the database. The bare minimum access it needs are SELECT, INSERT. 
  6. Run the install.sql file located in energyathome/install/install.sql. This can be achieve by running the command below where root is the username. A password will be prompted before the script is run: 
    
    `$ mysql -u root -p < energyathome/install/install.sql`

# Install datalogger

  1. Copy the datalogger directory to a suitable location. For purpose of the following instructions it will use ~/datalogger 
  2. Change directory to the datalogger: 
    
    `$ cd ~/energyathome/datalogger`

  3. Edit energyathome.ini to match your database setup. There are comments in the file to enter specfic values between the quotes (") e.g username, password, etc. There are also other options but the defaults should work "out of the box". 

## Hints

I'm sure there is a command line way to find out which port the CurrentCost
device is connected to but I used installed and used gtkterm.

    
    `$ sudo apt-get install gtkterm`

Start gtkterm either from Applications menu > Accessories > Serial port
terminal or via the terminal. Set the port settings in Configuration > Port
and set the settings stated in the default Config.pu file. Once the port
settings screen is set it should connect to the device. Wait for at least 6
seconds for an XML string to appear on the screen. If nothing appears then try
a different port. Make sure the gtkterm is closed before starting datalogger.

## Start datalogger

If you are using GNU screen do the following:

  1. Start screen: 
    
    `$ screen`

  2. The screen should be at command prompt. If not already, go to the datalogger directory: 
    
    `$ cd ~/energyathome/datalogger`

  3. Start the logger: 
    
    `$ python Main`

  4. "Detach" the screen is like minimizing the terminal. Pressing the following keyboard combination: 
    
    [ctrl] + a
    (let go of above keys)
    d

  5. This should return to the prompt before you typed "screen" in step 1. 
  6. To "re-attach" the terminal i.e you want to view or stop the data logger use the following command: 
    
    `$ screen -r`

For more information on screen see the man pages ($ man screen) or help
(screen -h) or the website
<[http://www.gnu.org/software/screen/>](http://www.gnu.org/software/screen/>)

Without GNU screen:

  1. The screen should be at command prompt. If not already, go to the datalogger directory: 
    
    `$ cd ~/energyathome/datalogger`

  2. Start the logger: 
    
    `$ python Main`

Please be aware whilst the data logger is started you will not be able to free
up the terminal till you stop the data logger by pressing ctrl + c. It is best
to use GNU screen above whilst the Linux demon for data logger is being
developed.

If you encounter the following message:

> Unable to connect to device port. could not open port /dev/ttyUSB0: 13
Permission denied: '/dev/ttyUSB0'

it means the user needs to be added to the dialout group to gain access: `sudo
usermod -a -G dialout $USER` where `$USER is ther current user. If the
datalogger is not going to be running as the current user, replace `$USER with
the appropriate username. This may require the user to log out and back in or
restart to take affect.

# Install web

  1. Install Apache and PHP as shown in Pre-Requisites section. 
  2. By default the web directory is in /var/www. If you type in [http://localhost](http://localhost) in a web browser on the same computer where Apache is installed it would bring up a web page saying "It works!". This means it should be all set up and ready to go. You will require super user privileges to copy to this directory. There are two places you can put the web component: 
  3. To place it as the main page on the is the site e.g [http://www.mysite.com](http://www.mysite.com) copy the ~/web directory to /var/www directory: 
    
    `$ sudo cp -R ~/energyathome/web/* /var/www`

  4. To copy it to a sub directory e.g [http://www.mysite.com/energyathome](http://www.mysite.com/energyathome) do the following: 
    
    `$ sudo mkdir /var/www/energyathome`
    `$ sudo cp -R ~/energyathome/web/* /var/www/energyathome`

  5. Edit the web configuration file at ~/var/www/energyathome/config/energyathome.ini to match your settings. 
  6. It is best to password protect this information. A simple method is to create a .htpassword and .htaccess files. The ~/web directory already contains a .htaccess file. All that is required is to change the "AuthUserFile" line. By default it assumes you used 3b as the web install. If path is different then amend the path according to your install. The authentication accepts any user specified in the .htpasswd stated in the "AuthUserFile" line. 
  7. Generate a .htpasswd file. This contains a username and their password. The password is encrypted in the file. Execute the following line, changing the path /var/www/energyathome to match your install and user to the username you want: 
    
    `$ sudo htpasswd -c /var/www/energyathome/.htpasswd user`

  8. To add additional users to type in the same command as in step 5 but without the '-c' argument e.g: 
    
    `$ sudo htpasswd /var/www/energyathome/.htpasswd user2`

By no means is this a secure way of password protecting the web front end but
it's a simple method. If after going through the steps above no prompt for
username and password when visiting the web page appears check your Apache
config. Make sure "AllowOverride AuthConfig" and "Options FollowSymLinks" is
in the

    
    <directory>

directive. Another way to enhance security is to enable and connect using SSL.
This is beyond the score of this document.

There is a config file inside the web/server directory called config.php. This
also needs the database log in details. There are other options such as
database name should these be different from the default but generally it
should work without any changes.
