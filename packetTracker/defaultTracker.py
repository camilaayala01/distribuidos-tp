from packetTracker.packetTracker import PacketTracker

"""A packet tracker that requires all packets to be received"""
class DefaultTracker(PacketTracker):
    def __init__(self):
        super().__init__(nodesInCluster=1, module=0)

    @classmethod
    def fromStorage(cls, attributes):
        super().fromStorage(nodesInCluster=1, module=0, attributes=attributes)

