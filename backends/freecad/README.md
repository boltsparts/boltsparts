# BOLTSFC
[![Total alerts](https://img.shields.io/lgtm/alerts/g/boltsparts/BOLTSFC.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/boltsparts/BOLTSFC/alerts/) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/boltsparts/BOLTSFC.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/boltsparts/BOLTSFC/context:python)  
### Information
* Installable FreeCAD package of BOLTS.
* This package is generated from of the following repository branch:
    * https://github.com/boltsparts/BOLTS/commits/master


### Pull Requests
* The pull requests made here can not be taken directly into the origin BOLTS repository.
* It is recomended to make pull requests to the main repository (commit author etc will be kept than).
    * https://github.com/boltsparts/BOLTS/pulls


### Installation by the FreeCAD AddOn manager:
* Start FreeCAD Addon manager on menu Tools.
* The directory BOLTSFC (inside this there will be the BOLTS directory) will be copied to your FreeCAD Mod directory (just wait a bit, ATM there will be no information about successful installation).
* Restart FreeCAD.


### Installation manually copied:
* Download FreeCAD macro file "start_bolts.FCMacro" and the BOLTS directory .
* Place both in your FreeCAD Macro directory.
* For more information refere to the webpage
    * https://www.bolts-library.org/en/docs/0.3/document/freecad/installation.html


### Start BOLTS
* by FreeCAD Gui:
    * Run the Macro "start_bolts.FCMacro".
* by Python in FreeCAD Python console
```
import BOLTS
BOLTS.show_widget()
```


### For developer
* LGTM: https://lgtm.com/projects/g/boltsparts/BOLTSFC



bernd@bimstatik.org
