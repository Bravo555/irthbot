# vim: set fileencoding=utf-8 :
import os;
import yaml;
class Config:
    def __load(self):
        if not os.path.exists(self.__config_path): 
            open(self.__config_path, 'w').close();
            self.__save();
        self.__conf_file=open(self.__config_path, "r+")
        self.__conf_raw=self.__conf_file.read();
        try:
            self.__config=yaml.load(self.__conf_raw);
        except ValueError:
            raise ValueError("Bad yaml in file %s."%self.__config_path);
        self.__conf_file.close();
    def __save(self):
        self.__conf_file=open(self.__config_path, "w")
        self.__conf_file.write(yaml.dump(self.__config, default_flow_style=False));
        self.__conf_file.close();
        
    def get(self, k):
        self.__load();
        if self.__config.has_key(k):
            return self.__config[k];
        else:
            return None;
    
    def set(self, k, value):
        self.__config[k]=value;
        self.__save();
        self.__load();
        return self.__config[k];
        
    def get_or_set(self, k, value):
        ret=self.get(k);
        if ret==None:
            ret=self.set(k, value);
        return ret;
        
    def has_key(self, k):
        return self.__config.has_key(k);
    
    def get_all(self):
        return self.__config;
    
    def pop(self, k):
        self.__config.pop(k, None)
        self.__save();
    
    def __init__(self, config_name):
        self.__config_name=config_name;
        self.__config_path="./conf/"+self.__config_name+".conf";
        self.__config={};
        self.__load();
 
"""
from config import Config
conf=Config("testconf");
print conf.get_all();
conf.set("dupa", "test")
print conf.get("dupa");
print conf.get_all();
print conf.get("a");
conf.set("a","dupa");
print conf.get("a");
conf=None;
conf=Config("testconf");
print conf.get_all();
print conf.get("a");
"""