from common.grouperPositiveReviews import GrouperPositiveReviews
from internalCommunication.internalComunication import InternalCommunication

def main():
    grouper = GrouperPositiveReviews()
    internalComm = InternalCommunication(grouper._type)
    internalComm.defineMessageHandler(grouper.handleMessage)

if __name__ == "__main__":
    main()