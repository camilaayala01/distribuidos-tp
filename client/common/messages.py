from common.utils import loadGames, loadReviews, storeResultsQuery1
from entryParsing.common.headerWithQueryNumber import HeaderWithQueryNumber
from entryParsing.common.headerWithTable import HeaderWithTable
from entryParsing.common.table import Table
from entryParsing.entryOSCount import EntryOSCount



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
