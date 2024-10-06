from common.utils import loadGames, loadReviews

generator = loadReviews()
for i in range(100):
    try:
        entry = next(generator)
        serialized = entry.serialize()
    except StopIteration:
        break
