@echo off

set module=UmbraTk

if "%1"=="-text" (
   set module=UmbraText
   shift
)
if "%1"=="--text" (
   set module=UmbraText
   shift
)

py -O -m umbra.%module% %1 %2 %3 %4 %5 %6 %7 %8 %9
