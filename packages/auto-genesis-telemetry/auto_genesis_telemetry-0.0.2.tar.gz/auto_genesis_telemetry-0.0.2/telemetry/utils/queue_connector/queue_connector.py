class QueueConnector:
    def send_message(self, message, destination):
        """Send a message to the specified destination."""
        raise NotImplementedError

    def receive_messages(self, callback, source):
        """Receive messages from the specified source."""
        raise NotImplementedError
