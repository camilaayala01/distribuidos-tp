from common.utils import loadGames, loadReviews, storeResultsQuery1
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.common.table import Table
from entryParsing.entryOSCount import EntryOSCount
GAME_BATCH_SIZE = 5
REVIEW_BATCH_SIZE = 100

def buildGameTableMessage(fragment: int):
    generator = loadGames()
    return buildMessage(fragment, generator, GAME_BATCH_SIZE, Table.GAMES)

def buildReviewTableMessage(fragment: int):
    generator = loadReviews()
    return buildMessage(fragment, generator, REVIEW_BATCH_SIZE, Table.REVIEWS)

def buildMessage(fragment: int, generator,  batchSize: int, table: Table):
    eof = False
    payload: bytes = bytes()
    for i in range(batchSize):
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
    storeResultsQuery1("Total de juegos: " + str(response._total) + 
    "Total de juegos soportados en Windows: " + str(response._windows) + 
    "Total de juegos soportados en Linux: " + str(response._linux) +
    "Total de juegos soportados en Mac: " + str(response._mac))
    

def processResponse(data: bytes) -> bool:
    header, data = HeaderWithQueryNumber.deserialize(data)
    match header._queryNumber:
        case 1: receiveQuery1Answer(data)
        case default:
            raise(Exception("invalid query num"))
        
    return header._eof
