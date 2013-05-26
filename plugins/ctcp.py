class Plugin:
    def __init__(self, api):
        self.api=api;
    
    def onMessage(self, sender, to, msg):
        if msg==u'VERSION':
            self.api.notice(sender['nick'], "VERSION %s"%self.api.conf.get_or_set("VERSION", "Tak."))
    
    def onLoad(self):
        self.api.register_listener(self.onMessage)
    
    def onUnload(self):
        pass;