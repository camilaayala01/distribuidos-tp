from client.common.utils import loadGames, loadReviews
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.common.table import Table
from entryParsing.entryOSCount import EntryOSCount
GAME_BATCH_SIZE = 5
REVIEW_BATCH_SIZE = 100

def buildGameTableMessage(fragment: int):
    return buildMessage(fragment, loadGames, GAME_BATCH_SIZE, Table.GAMES)

def buildReviewTableMessage(fragment: int):
    return buildMessage(fragment, loadReviews, REVIEW_BATCH_SIZE, Table.REVIEWS)

def buildMessage(fragment: int, generator, batchSize: int, table: Table):
    eof = False
    payload: bytes = bytes()
    for i in range( batchSize):
        try:
            entry = next(generator)
            payload += entry.serialize()
        except StopIteration:
            eof = True
            break

    header = HeaderWithTable(table, fragment, eof)
    return header + payload, eof


def sendTable(socket, msgBuilder):
    eofTable = False
    fragment = 1
    while not eofTable:
        msg, eofTable = msgBuilder(fragment)
        fragment += 1
        socket.send(msg)

def receiveQuery1Answer(data):
    response = EntryOSCount.deserialize(data)
    