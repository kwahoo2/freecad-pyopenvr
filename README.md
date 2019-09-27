# FreeCAD PyOpenVR
Moving towards a working implementation of VR in FreeCAD with range support for various VR hardware

## Background

> This thread continues (the) discussion from a (previous FreeCAD discussion) thread about [Oculus Rift](https://forum.freecadweb.org/viewtopic.php?style=10&f=9&t=7715&start=30).
I would like discuss here about wider VR hardware support. A few weeks ago an open VR/AR standard was presented: [OpenXR](ttps://www.khronos.org/openxr).
>
> Waiting for OpenXR hardware adoption (manufacturers like Oculus or Valve announced future support) I've starded experimenting with another API: **OpenVR**. 
OpenVR is not quite open as name suggest - it still needs a proprietary runtime (SteamVR), but unlike Oculus SDK it is supported on different operating systems and supports hardware from other manufacturers.
>
> Initially, I started tinkering with jriegel Rift's implementation, but later i found Python bindings for OpenVR [pyopenvr](https://github.com/cmbruns/pyopenvr). Basic idea is: write (and experiment with) an implementation in pyopenvr, and then port the code to C++.

source: https://forum.freecadweb.org/viewtopic.php?p=336241#p336241

## Prerequisites


### Software Dependencies

* FreeCAD v0.19.xxxxx
* Python 3.5+
* SteamVR Runtime (distributed with Valve Steam)

#### Python libraries
* numpy
* pivy.coin
* openvr
* sdl2

### Hardware

* Any HMD supported by OpenVR (HTC Vive, Valve Index, Oculus Rift)

## Installation

* Install Python libraries
* Start SteamVR
* Start FreeCAD
* Paste `freecad-pyopenvr.py` content in the FreeCAD Python console

## Contribute

PR's are welcome!FreeCAD 

## Discussion

Feedback, thoughts, questions, please direct them to the [dedicated FreeCAD forum discussion thread](https://forum.freecadweb.org/viewtopic.php?p=336241#p336241). 

## License

Check `LICENSE` for details
