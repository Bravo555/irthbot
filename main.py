# vim: set fileencoding=utf-8 :
import socket
import re
import os
import imp
import glob
from config import Config
#from botapi import BotApi

class Bot:
    BotApi=__import__("botapi").BotApi;
    config=None;
    sock=None;
    api=None;
    cmd_handlers={};
    plugins={};
    msg_listeners={};
    run=0;
    def __init__(self):
        self.run();
    def load_plugin(self, filepath):
        class_inst = None
        expected_class = 'Plugin'
        mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])
        self.api.log("Ładowanie wtyczki \"%s\"..."%mod_name)
        err=0;
        ex=None;
        if file_ext.lower() == '.py':
            py_mod = imp.load_source(mod_name, filepath)   
        elif file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, filepath)
        if hasattr(py_mod, expected_class):
            try:
                class_inst = py_mod.Plugin(self.BotApi(self, mod_name))
            except TypeError as e:
                err=1;
                ex=e;
                self.api.log("Błąd: Konstruktor wtyczki \"%s\" powinien pobierać jedynie jeden argument, z API bota."%mod_name);
                self.api.log("Wtyczka \"%s\" nie została załadowana."%mod_name)
            self.plugins[mod_name]=class_inst;
            if hasattr(self.plugins[mod_name],"onLoad"):
                try:
                    self.plugins[mod_name].onLoad();
                except Exception as e:
                    ex=e;
                    err=1;
                    self.api.log("Błąd: Coś poszło źle przy wywoływaniu funkcji .onLoad() wtyczki \"%s\". Sprawdź jej kod i włącz tryb \"debug\" w \"./conf/bot.conf\"."%mod_name)
            
        else:
            err=1;
            self.api.log("Błąd: Wtyczka \"%s\" nie ma klasy Plugin."%mod_name)
            
        if err:
            if not ex==None:
                self.api.log("Błąd: Bot dostał w mordę wyjątkiem: \""+ex.__class__.__name__+": "+ex.__str__()+"\".")
            self.api.log("Wtyczka \"%s\" nie została załadowana."%mod_name)
            if (not ex==None) and self.config.get("debug"):
                raise;
            self.plugins[mod_name]=None;
            self.plugins.pop(mod_name);
        else:
            self.api.log("Załadowano plugin \"%s\"."%mod_name)
            
        
    def unload_plugin(self, name):
        if self.plugins.has_key(name):
            ex=None;
            err=0;
            self.api.log("Wyłączanie wtyczki \"%s\"."%name);
            if hasattr(self.plugins[name],"onUnload"):
                try:
                    self.plugins[name].onUnload();
                except Exception as e:
                    ex=e;
                    err=1;
            if err:
                if not ex==None:
                    self.api.log("Błąd: Coś poszło źle przy wywoływaniu funkcji .onUnload() wtyczki \"%s\". Sprawdź jej kod i włącz tryb \"debug\" w \"./conf/bot.conf\"."%name)
                    self.api.log("Błąd: Bot dostał w mordę wyjątkiem: \""+ex.__class__.__name__+": "+ex.__str__()+"\".")
                    if self.config.get("debug"):
                        raise;
            try:
                self.cmd_handlers.pop(name);
                print self.msg_listeners[name]
            except:
                pass;
            try:
                self.msg_listeners.pop(name);
                print self.msg_listeners[name]
            except:
                pass;
            self.plugins[name]=None;
            self.plugins.pop(name);
            self.api.log("Wtyczka \"%s\" została wyłączona."%name)
            
    def load_plugins(self):
        pwd=os.getcwd();
        os.chdir("./plugins")
        for module in glob.glob("*.py"):
            os.chdir(pwd)
            self.load_plugin("./plugins/"+module);
            
    def unload_plugins(self):
        i=[];
        for key in self.plugins.iterkeys():
            i.append(key);
            
        for name in i:
            self.unload_plugin(name);

    def load_config(self):
        self.config=Config("bot");
        self.config.get_or_set("server", "irc.freenode.net");
        self.config.get_or_set("port",6667)
        self.config.get_or_set("channels", ["#irth"]);
        self.config.get_or_set("nickname", "irthbot");
        self.config.get_or_set("username", "irthbot");
        self.config.get_or_set("realname", "bot irtha :3");
        self.config.get_or_set("plugins", ["main", "test"])
        self.config.get_or_set("command", "%")
        self.config.get_or_set("master", ":(.*?)!irth@shell.uw-team.org")
        self.config.get_or_set("debug", False)
        
    def reload(self):
        self.BotApi=imp.load_source("botapi", "./botapi.py").BotApi;
        self.api=self.BotApi(self,"bot");
        self.unload_plugins();
        self.load_plugins();
        #self.api.log("Reloaded!")
        
    def connect(self):
        log=self.api.log;
        self.sock=socket.socket();
        self.sock.connect((self.config.get("server"),self.config.get("port")));
        print "connected"
        log("Trwa łączenie z serwerem %s na porcie %s."%(self.config.get("server"),self.config.get("port")));
        NICK="NICK %s\r\n"%self.config.get("nickname");
        USER="USER %s 8 * :%s\r\n"%(self.config.get("username"),self.config.get("realname"))
        self.sock.send(NICK);
        log("Ustawiam nick \"%s\"..."%self.config.get("nickname"));
        self.sock.send(USER);
        log("Ustawiam username i realname...")
        a=[""];
        log("Czekam na serwer...")
        while not "/MOTD" in a:
            msg=self.sock.recv(1024)
            for i in msg.split("\n"):
                if "PING" in i.split(" "):
                    self.api.raw("PONG %s"%i.split(" ")[1])
                log(i)
            a=msg.split(" ");
            
            
        log("Połączono!")
        for chan in self.config.get("channels"):
            log("Dołączam do %s."%chan)
            self.api.join(chan)
    
    def exec_cmd(self, cmd, sender, to, argc, argv):
        handled=0;
        for f in self.cmd_handlers.itervalues():
            if f.has_key(cmd):
                handled=1;
                for handler in f[cmd]:
                    try:
                        handler.run(sender, to, argc, argv);
                        self.api.log("Komenda \"%s\" została wykonana przez wtyczkę \"%s\"."%(cmd, handler.name));
                    except:
                        self.api.log("Błąd: Coś poszło źle przy wywoływaniu funkcji \"%%s\" wtyczki \"%s\""%(cmd, handler.name))
        if not handled:
            self.api.log("Żadna wtyczka nie chciała wykonać biednej komendy \"%s\". :("%cmd);
    
    def exec_msg(self, sender, to, msg):
        for f in self.msg_listeners.itervalues():
            for listener in f:
                listener(sender, to, msg);
    
    def parse(self, msg):
        msg=msg.split(" ");
        if msg[0]=="PING":
            self.api.raw("PONG %s"%msg[1])
        if msg[1]=="PRIVMSG":
            cmd=msg[3][1:]
            if cmd[0:1]==self.config.get("command"):
                cmd=cmd[1:].lower();
                sender={}
                sender['host']=msg[0];
                sender['nick']=re.search("^:(.*?)!", sender['host']).group(0)[1:-1];
                to=(sender['nick'] if msg[2]==self.config.get("nickname") else msg[2]);
                argc=len(msg)-4;
                i=4;
                argv=[];
                while i<=3+argc:
                    argv.append(msg[i]);
                    i+=1;
                self.exec_cmd(cmd, sender, to, argc, argv);
            else:
                sender={}
                sender['host']=msg[0];
                sender['nick']=re.search("^:(.*?)!", sender['host']).group(0)[1:-1];
                to=(sender['nick'] if msg[2]==self.config.get("nickname") else msg[2]);
                argc=len(msg)-3;
                i=3;
                argv=[];
                while i<=2+argc:
                    argv.append(msg[i]);
                    i+=1;
                msg=" ".join(argv)[1:]
                self.exec_msg(sender, to, msg);
                
    def listen(self):
        log=self.api.log;
        conn_buffer="";
        while self.run:
            conn_buffer=self.sock.recv(1024);
            msgs=conn_buffer.split("\n");
            conn_buffer=msgs.pop();
            for msg in msgs:
                msg_=msg.rstrip();
                log(msg_);
                self.parse(msg_);

    def run(self):
        self.load_config()
        self.api=self.BotApi(self,"bot");
        self.connect();
        self.load_plugins();
        self.run=1;
        self.listen();
    
Bot()
