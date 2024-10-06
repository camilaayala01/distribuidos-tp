

juegos, campos compartidos:

len(appid) -> 1 byte 
appid -> string  MAX 3.20 M
len(name) -> 1 byte
name -> string MAX 12
release date -> string de 10 bytes
estimated owner max 7
supported langs max 1216
windows -> u8 // 0 false 1 true
mac -> u8
linux -> u8
avg playtime forever -> int32 
len(genres) -> 1 byte
genres -> string

reviews, todos los campos:
len(appid) -> 1 byte
appid -> string
len(app_name) -> 1 byte
app_name -> string 
len(review_text) -> 2 bytes
review_text
review_score -> i8, es -1 o 1
review_votes -> u8



AVG_PT_FRV_BYTES = 2 # INT - MAX: 47K
MEDIAN_PT_FRV_BYTES = 2 # INT - MAX: 19.2K
AVG_PT_TWO_WEEKS_BYTES = 3 # INT MAX: 208K
MEDIAN_PT_TWO_WEEKS_BYTES = 2 # INT MAX: 19.2K

len AppID: 1
AppID: 7
len Name: 1
Name: 207
len Release date: 1
Release date: 10
len Estimated owners: 1
Estimated owners: 21
Peak CCU: 3
Required age: 1
Price: 3
DiscountDLC count: 1
len About the game: 3
About the game: 131699
len Supported languages : 2
Supported languages: 1216
len Full audio languages: 2
Full audio languages: 1216
len Reviews: 2
Reviews: 2911
len Header image: 2
Header image: 112
len Website: 2
Website: 206
len Support url: 2
Support url: 349
len Support email: 2
Support email: 247
Windows,Mac,Linux : 3
Metacritic score: 1
len Metacritic url: 2
Metacritic url: 142
User score: 1
Positive: 3
Negative: 3
Score rank: 2
Achievements: 2
Recommendations: 3
len Notes: 2
Notes: 2028
Average playtime forever: 3
Average playtime two weeks: 3
Median playtime forever: 3
Median playtime two weeks: 3
len Developers: 2
Developers: 584
len Publishers: 2
Publishers: 164
len Categories: 2
Categories: 371
len Genres: 2
Genres: 236
len Tags: 2
Tags: 290
len Screenshots: 2
Screenshots: 22691
len Movies: 2
Movies: 3687


BIGGEST ENTRY IN GAME TABLE IS 259397
BIGGEST ENTRY IN REVIEW TABLE IS 16875
TODO:
look for biggest entry - DONE
check eof is set when file ends- DONE
create smaller  - NOT 
define responses types and how to write them in files
check game table reading (number of columns) - DONE

check performance and consider header overhead in initializer
cleanse dataset of big entries
find out send packet 