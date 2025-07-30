import re

def assess_risk(command):
    cmd = command.lower()
    # Critical: destructive or system-wide
    if re.search(r"\brm\b.*-rf|\bmkfs\b|\bdd\b|\bshutdown\b|\breboot\b|\binit\b|\b:(){:|:&};:\b|\b:(){:|;:};:\b|\bhalt\b|\bpoweroff\b|\bsudo\b.*passwd|\bchown\b.*-R /|\bchmod\b.*777 /", cmd):
        return "critical"
    # Dangerous: sudo, user/system changes
    if re.search(r"\bsudo\b|\bchown\b|\bchmod\b|\bkill\b|\buseradd\b|\buserdel\b|\bgroupadd\b|\bgroupdel\b|\bmount\b|\bumount\b|\bservice\b|\bsystemctl\b", cmd):
        return "dangerous"
    # Medium: file move, copy, network
    if re.search(r"\bmv\b|\bcp\b|\bwget\b|\bcurl\b|\bscp\b|\bftp\b|\bchmod\b|\bchown\b", cmd):
        return "medium"
    # Safe: read-only, list, echo, cat, ls, pwd, whoami, etc.
    return "safe" 