# Patch APK
Simple scripts to patch the Tapped Out APK with new server urls.

## Linux

### Requirements
- A Tapped Out APK
- cURL
- Python3
- Python3-venv
- Python3-pip
- openjdk-11-jre

### Usage
```
./patch-apk.sh APK_TO_PATCH NEW_GAMESERVER_URL NEW_DLCSERVER_URL
```

## Windows
The windows version is very slow. I reccomend you use the linux version, and you can use it on windows with git bash (https://git-scm.com/). 

### Requirements
- A Tapped Out APK
- Python3 And Pip (https://python.org/)
- Java JRE or JDK

### Usage
```
.\patch-apk.bat APK_TO_PATCH NEW_GAMESERVER_URL NEW_DLCSERVER_URL
```