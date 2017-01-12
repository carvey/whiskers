"""
module to hold all logic related to turning rethink change feed messages into DDP compliant messages and vice-versa
"""

from PythonDDPClient.src.message import *

def rethink_to_ddp(table, message):
    """
    Parse rethink changfeed and generate the appropriate ddp message with the following rules:
        - new_val but no old_val -> (ddp) added
        - new_val and old_val -> (ddp) changed
        - old_val but no new_val -> (ddp) removed

    :param message: dict of a rethink changefeed message that should be converted to a ddp message
    :return:
    """
    old_val = message['old_val']
    new_val = message['new_val']

    # added
    if new_val and not old_val:
        id = message['new_val']['id']
        del message['new_val']['id']

        added = AddedMessage(collection=table, id=id, fields=message['new_val'])
        return added

    # changed
    elif new_val and old_val:
        changed_fields = {}
        for key, val in new_val.items():

            # field has been added
            if key not in old_val:
                changed_fields[key] = val

            # field has been changed
            if old_val[key] != val:
                changed_fields[key] = val

        cleared = []
        for key, val in old_val.items():
            if key not in new_val:
                cleared.append(key)

        changed = ChangedMessage(collection=table, id=message['old_val']['id'], fields=changed_fields, cleared=cleared)

        # meteor doesn't send the id back in the fields, but need to confirm this is how it should work in cases
        # where an id might change??
        if 'id' in message['old_val']:
            del message['old_val']['id']

        if 'id' in message['new_val']:
            del message['new_val']['id']

        return changed

    # removed
    elif not new_val and old_val:
        removed = RemovedMessage(collection=table, id=message['old_val']['id'])
        return removed