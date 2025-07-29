from rich import print
class LogTypecl():
    log = 1
    error = 2
    warning = 3
    state = 4
LogType = LogTypecl()

class Loger():
    def __init__(self,startmsg = 1, filename="log.log", error_prefix="[!]", warning_prefix="[-]", log_prefix="[L]", state_prefix="[+]"):
        self.save_filename = filename
        self.save_error_prefix = error_prefix
        self.save_warning_prefix = warning_prefix
        self.save_log_prefix = log_prefix
        self.save_state_prefix = state_prefix
        if startmsg:
            self.log(message= "------------------------------start-----------------------------")
    def log(self,message,logtype=5):
        if logtype == LogType.log:
            self.print_log(self.save_log_prefix + " " + message,"[/blue]","[blue]")
        elif logtype == LogType.error:
            self.print_log(self.save_error_prefix + " " + message,"[/red]","[red]")
        elif logtype == LogType.warning:
            self.print_log(self.save_warning_prefix + " " + message,"[/yellow]","[yellow]")
        elif logtype == LogType.state:
            self.print_log(self.save_state_prefix + " " + message,"[/green]","[green]")
        elif logtype == 5:
            self.print_log(message,"","")
    def print_log(self,text,suf,pref):
        with open(self.save_filename, 'a',encoding="utf-8") as outfile:
            outfile.write(text+"\n")
            print(pref+text+suf)
        


