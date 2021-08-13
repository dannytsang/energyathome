energy@home
============

energy@home is a project created to use the CurrentCost CC128 device. CC128 is
the one with the black boarder around the display. I decided to make my own
program to learn programming about in Linux. The goal of the project is to
capture information from CC128 (and possibly other devices) and display it in
a friendly manner accessible over the Internet. I found other Linux based
programs to be complicated or did not do what I wanted to do. The software is
for self hosting and therefore no monthly or annual fee is required (except
for running the software in-house).

# LICENSE

See COPYING for more details about the licensing of this program.

# FEATURES

  * All free (cost) and free (freedom) software (see license) 
  * Tested with CurrentCost CC128 "Envi" device 
  * Intelligent and configurable data capture and storage using triggers and filters 
  * Requires Python.

Example data displayed in [Home Assistant](https://www.home-assistant.io/)
[<img src="https://twitter.com/i/status/1425402088708837388">](https://i0.wp.com/https://twitter.com/i/status/1425402088708837388 "Energy usage in home assistant")

# INSTALL

See INSTALL file to install / run energy@home.

# LIMITATIONS

Currently it only supports CurrentCost CC128 "Envi" device but I have reports
that it also works with "EnviR" devices too. This is because I only have this
device to work with and therefore to test with.

If the time is taken from the device it will automatically use the date from
the server. This is due to the limitation with the device because it only
sends out the time with no date information. Also CC128 does not sync it's
time to anything so if power was lost, the time would be wrong and could cause
data anomalies. It is advised to use NTP or similar protocol on the server to
ensure the date and time is correct regardless if the time is taken from the
device or not. This is a device limitation.
