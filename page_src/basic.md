# BASIC KNOWLEDGE ABOUT TWIG

## ![](/image/tag.png) Basic rules

* just send messages that you want to tweet and it will be posted to your timeline.
* the prefix of commands is "`{{prefix}}`", and any message starts with a leading "`{{prefix}}`" will be regarded as commands
* to send tweets that start with the prefix, you need to duplicate the first prefix:
#### e.g.: "{{prefix}}{{prefix}}tweet anything" will post "{{prefix}}tweet anything"

## ![](/image/tag.png) Frequently used commands

* "`.ho`" prints home timeline
* "`.@`" prints mention timeline
* "`.msg`" views conversation
* "`.@ <tweet id> <text>`" replys to the author of the tweet
* "`.@a <tweet id> <text>`" replys to all users mentioned in the tweet
* "`.tl [user]`" prints the tweets of a given user, "`.tl`" will show your tweets
* "`.st [user]`" queries detailed information of a given user, and "`.st`" queries yours
* "`.r <tweet id>`" official retweet
* "`.r <tweet id> [text]`" retweet with your comment (RT)
* "`.fav`" show your favorites, "`.+fav <tweet id>`" favorites tweets
* "`.del`" removes the most recent tweet of yours, and "`.del <tweet id>`" removes the given tweet
* "`.d`" checks the receive direct messages, and "`.d <user> <message>`" send direct message to a given user

## ![](/image/tag.png) Help documents
* each command has its format, use "`.help`" with any commands (without prefix, including "`.help`" itself) to see the format
#### e.g.: "{{prefix}}help help" (remember to remove the prefix) 
* when you are looking at the help document: 
* parameters enclosed with pointy brackets (e.g "`<tweet id>`") means it is a compulsory parameter for the command.
#### e.g.: command `reply`'s format is shown as "`.reply <id> <text>`" 
####       which means you have to provide both `id` and `text` before `.reply` can work properly
* parameters enclosed with squared brackets (e.g "`[where]`") means is is an optional parameter for the command.
#### e.g.: command `mention`'s format is shown as "`.mention [where]`"
####       which means both "`.mention`" and "`.mention <123456`" are valid
* **alias** is a handy feature, which makes twig more flexible to use:
* using command "`.help <command>`" or command "`.alias <command>`" to grab a list of the aliases of a given command.
* all names in the list are identical.
#### e.g.: "`.alias mention`" returns "`[@,at,mention]`", which means all commands below are identical:
####       "`.@ <12345`"
####       "`.at <12345`"
####       "`.mention <12345`"
####       given that "`.alias help`" returns "`[?,h,help,hlp,man]`", even commands below are identical as well:
####       "`.h help`"
####       "`.man ?`"
####       "`.? ?`"
* almost each command has many aliases, pick one you prefered to use!

## ![](/image/tag.png) Twig outputs
* the meaning of a twig reply depends on the first character of each line. 
* '`#`' indicates the following message is a piece of twig information or a string data
* '`!`' indicates errors and warnings
* '`A`' indicates the following data is an array
* '`=`' indicates a key-value pair, e.g: "= id: 123456" reads "id is 123456"
* '`R`' indicates a raw string, with a leading number indicating its length
* '`T`' for tweets
* '`L`' for detail of lists
* '`D`' for direct messages 
* '`>`' will never be the first line, and it indicates additional data of the previous line 
