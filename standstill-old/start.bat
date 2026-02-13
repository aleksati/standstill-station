@echo off
setlocal enableextensions EnableDelayedExpansion

echo weit for IP and start 

set "folderarray[]="

:startGetIP
set "count=0"
echo.
echo Start Get IP
ipconfig > c:\RITMO\ipconfig.tmp

for /F "delims=" %%a in (c:\RITMO\ipconfig.tmp) do (
	SET var=%%a
	SET MyVar=!var!
	SET MyVar=!MyVar: =!
	SET /A count+=1
	SET "folderarray[!count!]=!MyVar!"
)
echo !folderarray[5]!
set i=0
for /L %%i in (1,1,%count%) do call :checkifip !folderarray[%%i]! %%i
Timeout 10
goto startGetIP

:checkifip
@setlocal enableextensions enabledelayedexpansion
set element1=%1
if not x%element1:IPv4=%==x%element1% (
	echo IPv4 in element
	set ipv4=!element1:ipv4Address...........:=!
	call :checkiprange !ipv4!
)
goto :eof

:checkiprange
set element2=%1
::echo %element2%
if not %element2:192.168.1=%==%element2% (
	echo my IP is %element2% and within the defined range
	goto :startSetup
)
goto :eof

:startSetup

echo ==========
echo == START ==
echo ==========
cd C:\RITMO\stillstanding-master\
python standstill02.py

exit