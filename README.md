# smileybot

A Discord port of smileybot for euphoria.io by [github.com/sillylyn](https://www.github.com/sillylyn)

Bot allows you to generate a database of images for quick recall.

Code requires the following to be entered by host:
- imgur client_id
- imgur client_secret
- discord token
- list of admin (or equivalent) user names to limit the use of the !remove command

##### Bot commands:
- &<smiley> *calls link and displays image using native embed*
- !add <smiley> <url> *add a new image*
- !search <string> *search for an image*
- !info user <username> *displays info about images added by user*
- !info image <smiley> *displays info about an image*
- !listall *lists all available image*
- !top *lists the top 10 images*
- !random *displays a random image*
- !me_irl *displays your personal smiley. create with !add me_irl <url>*
- !remove <smiley> *deletes an image from the database*
