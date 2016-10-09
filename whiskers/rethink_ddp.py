"""
module to hold all logic related to turning rethink change feed messages into DDP compliant messages and vice-versa
"""

def rethink_to_ddp(message):
    """
    Attempt to parse rethink changfeed and generate the appropriate ddp message with the following rules:
        - new_val but no old_val -> (ddp) added
        - new_val and old_val -> (ddp) changed
        - old_val but no new_val -> (ddp) removed

    :param message: dict of a rethink changefeed message that should be converted to a ddp message
    :return:
    """
    pass