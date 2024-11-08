from packetTracker.packetTracker import PacketTracker

"""A packet tracker that requires all packets to be received"""
class DefaultTracker(PacketTracker):
    def __init__(self, storagePath: str):
        super().__init__(nodesInCluster=1, module=0, storagePath=storagePath)