from ouimeaux.pysignals import Signal, receiver

# Work around a bug in pysignals when in the interactive interpreter
import sys
_main = sys.modules.get('__main__')
if _main:
    _main.__file__ = "__main__.py"

class StateChange( Signal ):

    def __init__(self, providing_args=None):
        super(StateChange, self).__init__(providing_args)
        self.sender_status = {}

    def send(self, sender, **named):
        """
        Send signal from sender to all connected receivers *only if* the signal's
        contents has changed.
        If any receiver raises an error, the error propagates back through send,
        terminating the dispatch loop, so it is quite possible to not have all
        receivers called if a raises an error.
        Arguments:
            sender
                The sender of the signal Either a specific object or None.
            named
                Named arguments which will be passed to receivers.
        Returns a list of tuple pairs [(receiver, response), ... ].
        """
        responses = []
        if not self.receivers:
            return responses

        sender_id = _make_id(sender)
        if sender_id not in self.sender_status:
            self.sender_status[sender_id] = {}

        if self.sender_status[sender_id] == named:
            return responses

        self.sender_status[sender_id] = named

        for receiver in self._live_receivers(sender_id):
            response = receiver(signal=self, sender=sender, **named)
            responses.append((receiver, response))
        return responses

# Fires when a device responds to a broadcast 
discovered = Signal(providing_args=["address", "headers"])

# Fires when a device is found and added to the environment
devicefound = Signal()

# Fires when a subscriber receives an event
subscription = Signal(providing_args=["type", "value"])

# Fires when a device changes state
statechange = StateChange(providing_args=["state"])


@receiver(subscription)
def _got_subscription(sender, **kwargs):
    if kwargs['type'] == 'BinaryState':
        statechange.send(sender, state=int(kwargs['value']))
