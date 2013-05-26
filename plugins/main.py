# vim: set fileencoding=utf-8 :
class Plugin:
    def reload(self, sender, to, argc, argv):
        if self.api.is_admin(sender['host']):
            self.api.log("Przeładowywanie wtyczek...")
            self.api.conf.set("reload", True);
            self.api.conf.set("reload_to", to)
            self.api.privmsg(to, "Przeładowywanie...")
            self.api.reload();
        else:
            self.api.privmsg(to, "%s, nie masz uprawnień. Co kombinujesz? ;>"%sender['nick']);
    
    def plugin_list(self, sender, to, argc, argv):
        self.api.privmsg(to, "%s, załadowane wtyczki: %s."%(sender['nick'],", ".join(self.api.plugin_list())))
    
    def quit(self, sender, to, argc, argv):
        if self.api.is_admin(sender['host']):
            self.api.privmsg(to, "Okej, jeżeli mnie nie chcecie...");
            self.api.quit();
        else:
            self.api.privmsg(to, "%s, nie kombinuj!"%sender['nick']);
            
    def op(self, sender, to, argc, argv):
        if self.api.is_admin(sender['host']):
            if argc>1:
                NICKS=argv[1:];
                for i in NICKS:
                    self.api.op(argv[0], i)
        else:
            self.api.privmsg(to, "%s, czo ty robisz, nie możesz :v"%sender['nick']);
    
    def deop(self, sender, to, argc, argv):
        if self.api.is_admin(sender['host']):
            if argc>1:
                NICKS=argv[1:];
                for i in NICKS:
                    self.api.deop(argv[0], i)
        else:
            self.api.privmsg(to, "%s, czo ty robisz, nie możesz :v"%sender['nick']);
    
    def join(self, sender, to, argc, argv):
        if self.api.is_admin(sender['host']):
            if argc==1:
                self.api.join(argv[0]);

    def part(self, sender, to, argc, argv):
        if self.api.is_admin(sender['host']):
            if argc==1:
                self.api.part(argv[0]);
    def say(self, sender, to, argc, argv):
        self.api.privmsg(to, " ".join(argv))
    
    def nick(self, sender, to, argc, argv):
        if argc>0:
            if self.api.is_admin(sender['host']):
                self.api.nick(argv[0])
    
    def voice(self, sender, to, argc, argv):
        if self.api.is_admin(sender['host']):
            if argc>1:
                NICKS=argv[1:];
                for i in NICKS:
                    self.api.voice(argv[0], i)
    
    def __init__(self, api):
        self.api=api;
    def onLoad(self):
        if self.api.conf.get_or_set("reload", False):
            self.api.privmsg(self.api.conf.get("reload_to"),"Przeładowano!")
            self.api.conf.pop("reload")
        self.api.register_cmd("reload",self.reload, "reload")
        self.api.register_cmd("plugins",self.plugin_list, "plugins")
        self.api.register_cmd("quit",self.quit, "quit")
        self.api.register_cmd("join",self.join, "join")
        self.api.register_cmd("part",self.part, "part")
        self.api.register_cmd("op",self.op, "op")
        self.api.register_cmd("deop",self.deop, "deop")
        self.api.register_cmd("say",self.say,"say");
        self.api.register_cmd("nick",self.nick,"voice");
        self.api.register_cmd("voice",self.voice,"voice")