from office365.runtime.client_value import ClientValue


class Report(ClientValue):

    def __init__(self, content=None):
        super(Report, self).__init__()
        self.content = content
