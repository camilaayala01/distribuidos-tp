from common.utils import loadGames, loadReviews

biggestEntrySize = 0
generator = loadReviews()
while True:
    try:
        entry = next(generator)
        serialized = entry.serialize()
        size = len(serialized)
        if size > biggestEntrySize:
            biggestEntrySize = size
            print(f'biggest is now {biggestEntrySize}')
    except StopIteration:
        break
print(f'biggest entry is {biggestEntrySize}')