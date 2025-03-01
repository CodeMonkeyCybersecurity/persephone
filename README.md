# Persephone: Enhanced Restic Backup Wrapper

In Greek mythology, **Persephone** is the goddess of both the underworld and springtime. This represents cycles of loss and renewal—paralleling the backup and recovery process. 

**Persephone** is a solution designed to simplify and enhance the use of Restic for backups and recovery, providing additional features like centralized management, automated scheduling, and modular configuration.

This will currently work only on debian-based systems (eg. Ubuntu, Debian, Kali). **Work is ongoing to expand this to MacOS and Windows.**

Below is a completed quickstart guide that fills in the missing “Use Persephone” section and adds instructions for Windows 10+. (Note that you should adjust paths or commands as needed for your particular environment.)

# Quick start

Below are the instructions for installing and using Persephone on UNIX-like systems (except MacOS X), MacOS X, and Windows 10+.

# UNIX-like systems (except MacOS X)

### Become root
```
su
```
Clone Persephone
```
cd /opt
git clone https://github.com/CodeMonkeyCybersecurity/persephone.git
cd persephone
```
Move into unix directory
```
cd unix
```
Install Go and dependencies
```
apt install gcc
go install golang.org/x/term@latest
```

Run the scripts 
```
go run createPersephoneFiles.go
go run createPersephoneConfig.go
go run createPersephoneRepoS3.go
go run createPersephoneBackupS3Script.go
go run createPersephoneSchedule.go
```

You can now configure your backup settings (for example, by editing the included configuration file or passing command-line options) and schedule your backups using cron.

# MacOS X

Become root
```
su
```
Clone Persephone
```
cd /opt
git clone https://github.com/CodeMonkeyCybersecurity/persephone.git
cd persephone
```
Move into macosx directory
```
cd macosx
```
Install Go and dependencies
Ensure that you have Homebrew installed, then:
```
brew install gcc
go get golang.org/x/term
```

Run the scripts 
```
go run createTimeMachineIncludes.go
go run createPersephoneFiles.go
go run createPersephoneConfig.go
go run createPersephoneRepoS3.go
go run createPersephoneBackupS3Script.go
go run createPersephoneSchedule.go
```

# Windows 10+

Open an elevated Command Prompt or PowerShell

Right-click your Command Prompt/PowerShell and choose Run as administrator.

Clone Persephone

Ensure you have Git for Windows installed, then:
```
mkdir C:\opt
cd C:\opt
git clone https://github.com/CodeMonkeyCybersecurity/persephone.git
cd persephone
```

Move into windows directory
```
cd windows
```

Install Go and dependencies

Make sure Go for Windows is installed and added to your PATH. Then install the required package by running:
```
winget install --id GoLang.Go

## Open a new pwsh admin tab and check Go installed correctly
$env:Path -split ';' | Select-String "Go"
go get golang.org/x/term
```
If you need a C compiler, you may install MinGW or use TDM-GCC.

Run the scripts 
```
go run createPersephoneFiles.go
go run createPersephoneConfig.go
go run createPersephoneRepoS3.go
go run createPersephoneBackupS3Script.go
go run createPersephoneSchedule.go
```

Verify the new scheduled task
```
Get-ScheduledTask -TaskName "PersephoneBackupHourly" | Format-List *
```


You can then edit configuration files or use command-line parameters to customize your backup tasks. Consider using the Windows Task Scheduler to automate running Persephone at scheduled intervals.

This guide should help you get started with Persephone across different operating systems. Be sure to review the project’s documentation for more details on configuration and advanced usage.
# See out knowledge base, [Athena](https://wiki.cybermonkey.net.au), for more on how to use this.

# Other links
See our website: [cybermonkey.net.au](https://cybermonkey.net.au/)

Our [Facebook](https://www.facebook.com/codemonkeycyber)

Or [X/Twitter](https://x.com/codemonkeycyber)


# Complaints, compliments, confusion:

Secure email: [main@cybermonkey.net.au](mailto:main@cybermonkey.net.au)  
Website: [cybermonkey.net.au](https://cybermonkey.net.au)

```
#     ___         _       __  __          _
#    / __|___  __| |___  |  \/  |___ _ _ | |_____ _  _
#   | (__/ _ \/ _` / -_) | |\/| / _ \ ' \| / / -_) || |
#    \___\___/\__,_\___| |_|  |_\___/_||_|_\_\___|\_, |
#                  / __|  _| |__  ___ _ _         |__/
#                 | (_| || | '_ \/ -_) '_|
#                  \___\_, |_.__/\___|_|
#                      |__/
```


---
© 2025 [Code Monkey Cybersecurity](https://cybermonkey.net.au/). ABN: 77 177 673 061. All rights reserved.
