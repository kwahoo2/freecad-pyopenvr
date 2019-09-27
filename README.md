# FreeCAD PyOpenVR
Moving towards a working implementation of VR in FreeCAD with range support for various VR hardware

## Screenshots

![Famous-Schenkel-in-VR][Screenshot1]

![Performance-Teaser][Screenshot2]

[Screenshot1]: https://user-images.githubusercontent.com/4140247/65766355-bd108b00-e0f8-11e9-9624-3e32feb45a2d.png "FreeCAD's Famous Schnekel visualized in VR"  

[Screenshot2]: https://user-images.githubusercontent.com/4140247/65766408-e204fe00-e0f8-11e9-8c22-7709dbf2b738.png "Displaying some perfomance stats"

## Background

> This thread continues (the) discussion from a (previous FreeCAD discussion) thread about [Oculus Rift](https://forum.freecadweb.org/viewtopic.php?style=10&f=9&t=7715&start=30).
I would like discuss here about wider VR hardware support. A few weeks ago an open VR/AR standard was presented: [OpenXR](ttps://www.khronos.org/openxr).
>
> Waiting for OpenXR hardware adoption (manufacturers like Oculus or Valve announced future support) I've starded experimenting with another API: **OpenVR**. 
OpenVR is not quite open as name suggest - it still needs a proprietary runtime (SteamVR), but unlike Oculus SDK it is supported on different operating systems and supports hardware from other manufacturers.
>
> Initially, I started tinkering with jriegel Rift's implementation, but later i found Python bindings for OpenVR [pyopenvr](https://github.com/cmbruns/pyopenvr). Basic idea is: write (and experiment with) an implementation in pyopenvr, and then port the code to C++.

[source](https://forum.freecadweb.org/viewtopic.php?p=336241#p336241)

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

## Installation and Usage

1. Install Python libraries
2. Start SteamVR
3. Start FreeCAD
4. Paste [`freecad-pyopenvr.py`](https://raw.githubusercontent.com/kwahoo2/freecad-pyopenvr/master/freecad-pyopenvr.py) contents in to the FreeCAD Python console

## Contribute

PR's are welcome!

## Discussion

Feedback, thoughts, questions, please direct them to the [dedicated FreeCAD forum discussion thread](https://forum.freecadweb.org/viewtopic.php?p=336241#p336241). 

## License

Check [LICENSE](LICENSE) for details.
