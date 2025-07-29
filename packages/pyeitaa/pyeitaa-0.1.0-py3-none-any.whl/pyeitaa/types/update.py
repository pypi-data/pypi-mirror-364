import pyeitaa


class Update:
    def stop_propagation(self):
        raise pyeitaa.StopPropagation

    def continue_propagation(self):
        raise pyeitaa.ContinuePropagation