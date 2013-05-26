# vim: set fileencoding=utf-8 :
from config import Config;
import re;
import datetime;
class CommandHandler:
    def __init__(self, f, name, permission):
        self.run=f;
        self.name=name;
        self.permission=name+"."+permission;

class BotApi:
    def reload(self):
        self.__bot.reload();
    
    def plugin_list(self):
        a=[];
        for plugin in self.__bot.plugins.iterkeys():
            a.append(plugin);
        return a;
    def quit(self):
        self.__bot.run=0;
        
    def __init__(self, bot, name):
        self.__bot=bot;
        self.name=name;
        self.conf=Config(name);
        self.botconf=self.__bot.config.get_all();
    
    def is_admin(self, hostname):
        pattern=self.__bot.config.get("master");
        if len(re.findall(pattern, hostname))==1:
            return True;
        else:
            return False;
    
    def register_cmd(self, cmd, func, permission):
        cmd=cmd.lower();
        if not self.__bot.cmd_handlers.has_key(self.name):
            self.__bot.cmd_handlers[self.name]={};
        if not self.__bot.cmd_handlers[self.name].has_key(cmd):
            self.__bot.cmd_handlers[self.name][cmd]=[];
        self.__bot.cmd_handlers[self.name][cmd].append(CommandHandler(func, self.name, permission));
            
    def register_listener(self, func):
        if not self.__bot.msg_listeners.has_key(self.name):
            self.__bot.msg_listeners[self.name]=[];
        self.__bot.msg_listeners[self.name].append(func);
        
    def unregister_cmd(self, cmd, func):
        if self.__bot.cmd_handlers.has_key(self.name):
            if self.__not.cmd_handlers[self.name].has_key(cmd):
                try:
                    self.__bot.cmd_handlers[cmd].remove(func);
                except ValueError:
                    pass;
    
    def unregister_listener(self, func):
        try:
            self.__bot.msg_listeners[self.name].remove(func);
        except:
            pass;
    def op(self, chan, nick):
        self.__bot.sock.send("MODE %s +o %s\r\n"%(chan, nick));
        print "[%s][OP:%s->%s] %s"%(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), self.name, chan, nick);
    
    def deop(self, chan, nick):
        self.__bot.sock.send("MODE %s -o %s\r\n"%(chan, nick));
        print "[%s][DEOP:%s->%s] %s"%(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), self.name, chan, nick);

    def voice(self, chan, nick):
        self.__bot.sock.send("MODE %s +v %s\r\n"%(chan, nick));
        print "[%s][VOICE:%s->%s] %s"%(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), self.name, chan, nick);

    def join(self, chan):
        self.__bot.sock.send("JOIN %s\r\n"%chan);
        print "[%s][JOIN:%s] %s"%(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), self.name, chan);
        
    def part(self, chan):
        self.__bot.sock.send("PART %s\r\n"%chan);
        print "[%s][PART:%s] %s"%(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), self.name, chan);
    
    def notice(self, to, msg):
        self.__bot.sock.send("NOTICE %s :%s\r\n"%(to,msg))
        print "[%s][NOTICE:%s->%s] %s"%(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), self.name,to,msg);
    
    def nick(self, nick):
        self.__bot.sock.send("NICK %s\r\n"%nick)
        print "[%s][NICK:%s] %s"%(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), self.name, nick);
    
    def privmsg(self,to,msg):
        self.__bot.sock.send("PRIVMSG %s :%s\r\n"%(to,msg))
        print "[%s][PRIVMSG:%s->%s] %s"%(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), self.name,to,msg);
    def log(self, msg):
        print "[%s][LOG:%s] %s"%(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), self.name, msg);
    def raw(self, msg):
        self.__bot.sock.send("%s\r\n"%msg)
        print "[%s][RAW:%s] %s"%(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), self.name, msg);
        