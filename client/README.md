juegos, campos compartidos:

len(appid) -> 1 byte
appid -> string
len(name) -> 1 byte
name -> string 
release date -> string de 10 bytes
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