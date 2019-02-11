from stark.services.v1 import site
from stark.handler import Handler
from app02 import models


class HostHandler(Handler):
    display_list = ['host', 'IP', Handler.edit_display, Handler.del_display]
    multi_list = [Handler.multi_delete]


site.register(models.Host, HostHandler)
