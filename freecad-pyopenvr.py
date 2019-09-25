import time
import sdl2
import openvr
import numpy
import threading

from OpenGL.GL import *
from openvr.glframework import shader_string
from sdl2 import *

from pivy.coin import SoSeparator
from pivy.coin import SoGroup
from pivy.coin import SoBaseColor
from pivy.coin import SbColor
from pivy.coin import SoSceneManager
from pivy.coin import SbViewportRegion
from pivy.coin import SoFrustumCamera
from pivy.coin import SbVec3f
from pivy.coin import SoCamera
from pivy.coin import SoDirectionalLight
from pivy.coin import SoCone
from pivy.coin import SoTranslation
from pivy.coin import SbRotation
from pivy.coin import SoScale

from math import sqrt, copysign

# see https://github.com/cmbruns/pyopenvr

class OpenVRTest(object):
  "Tiny OpenVR example with python (based on openvr example)"

  def __init__(s):
    s.vr_system = openvr.init(openvr.VRApplication_Scene)
    s.vr_compositor = openvr.VRCompositor()
    poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
    s.poses = poses_t()
    s.w, s.h = s.vr_system.getRecommendedRenderTargetSize()
    SDL_Init(SDL_INIT_VIDEO)
    s.window = SDL_CreateWindow (b"test",
      SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
      100, 100, SDL_WINDOW_SHOWN|SDL_WINDOW_OPENGL)
    s.context = SDL_GL_CreateContext(s.window)
    SDL_GL_MakeCurrent(s.window, s.context)
    s.depth_buffer = glGenRenderbuffers(1)
    s.frame_buffers = glGenFramebuffers(2)
    s.texture_ids = glGenTextures(2)
    s.textures = [None] * 2
    s.eyes = [openvr.Eye_Left, openvr.Eye_Right] 
    s.camToHead = [None] * 2
    s.proj_raw = [None] * 2
    s.nearZ = 0.01
    s.farZ = 500

    for eye in range(2):
      glBindFramebuffer(GL_FRAMEBUFFER, s.frame_buffers[eye])
      glBindRenderbuffer(GL_RENDERBUFFER, s.depth_buffer)
      glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, s.w, s.h)
      glFramebufferRenderbuffer(
        GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER,
        s.depth_buffer)
      glBindTexture(GL_TEXTURE_2D, s.texture_ids[eye])
      glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA8, s.w, s.h, 0, GL_RGBA, GL_UNSIGNED_BYTE,
        None)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
      glFramebufferTexture2D(
        GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
        s.texture_ids[eye], 0)
      texture = openvr.Texture_t()
      texture.handle = int(s.texture_ids[eye])
      texture.eType = openvr.TextureType_OpenGL
      texture.eColorSpace = openvr.ColorSpace_Gamma
      s.textures[eye] = texture
      s.proj_raw[eye]= s.vr_system.getProjectionRaw(s.eyes[eye]) #void GetProjectionRaw( Hmd_Eye eEye, float *pfLeft, float *pfRight, float *pfTop, float *pfBottom )
      eyehead = s.vr_system.getEyeToHeadTransform(s.eyes[eye]) #[0][3] is eye-center distance
      s.camToHead[eye] = numpy.array([ [eyehead.m[j][i] for i in range(4)] for j in range(3) ]) 

    s.setupcameras()
    s.setupscene()

    while s.draw():
      pass

  def setupscene(s):
    #coin3d setup
    vpRegion = SbViewportRegion(s.w, s.h)
    s.m_sceneManager = SoSceneManager()
    s.m_sceneManager.setViewportRegion(vpRegion)
    s.m_sceneManager.setBackgroundColor(SbColor(0.0, 0.0, 0.8));
    light = SoDirectionalLight()
    light2 = SoDirectionalLight()
    light2.direction.setValue(-1,-1,-1)
    light2.intensity.setValue(0.6)
    light2.color.setValue(0.8,0.8,1)
    s.scale = SoScale()
    s.scale.scaleFactor.setValue(0.001, 0.001, 0.001) #OpenVR uses meters not milimeters
    s.camtrans0 = SoTranslation()
    s.camtrans1 = SoTranslation()
    s.cgrp0 = SoGroup()
    s.cgrp1 = SoGroup()
    s.sgrp0 = SoGroup()
    s.sgrp1 = SoGroup()
    s.camtrans0.translation.setValue([s.camToHead[0][0][3],0,0])
    s.camtrans1.translation.setValue([s.camToHead[1][0][3],0,0])
    sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()#get active scenegraph
    #LEFT EYE
    s.rootScene0 = SoSeparator()
    s.rootScene0.ref()
    s.rootScene0.addChild(s.cgrp0)
    s.cgrp0.addChild(s.camtrans0)
    s.cgrp0.addChild(s.camera0)
    s.rootScene0.addChild(s.sgrp0)
    s.sgrp0.addChild(light)
    s.sgrp0.addChild(light2)
    s.sgrp0.addChild(s.scale)
    s.sgrp0.addChild(sg)#add scenegraph
    #RIGHT EYE
    s.rootScene1 = SoSeparator()
    s.rootScene1.ref()
    s.rootScene1.addChild(s.cgrp1)
    s.cgrp1.addChild(s.camtrans1)
    s.cgrp1.addChild(s.camera1)
    s.rootScene1.addChild(s.sgrp1)
    s.sgrp1.addChild(light)
    s.sgrp1.addChild(light2)
    s.sgrp1.addChild(s.scale)
    s.sgrp1.addChild(sg)#add scenegraph

  def setupcameras(s):
    nearZ = s.nearZ
    farZ = s.farZ
    #LEFT EYE
    s.camera0 = SoFrustumCamera()
    s.basePosition0 = SbVec3f(0.0, 0.0, 0.0)
    s.camera0.position.setValue(s.basePosition0)
    s.camera0.viewportMapping.setValue(SoCamera.LEAVE_ALONE)
    left = nearZ * s.proj_raw[0][0]
    right = nearZ * s.proj_raw[0][1]
    top = nearZ * (-s.proj_raw[0][2]) #why top is negative?
    bottom = nearZ * (-s.proj_raw[0][3])
    aspect = (2 * nearZ / (top - bottom)) / (2 * nearZ * (right - left))
    s.camera0.nearDistance.setValue(nearZ)
    s.camera0.farDistance.setValue(farZ)
    s.camera0.left.setValue(left)
    s.camera0.right.setValue(right)
    s.camera0.top.setValue(top)
    s.camera0.bottom.setValue(bottom)
    s.camera0.aspectRatio.setValue(aspect)
    #RIGHT EYE
    s.camera1 = SoFrustumCamera()
    s.basePosition1 = SbVec3f(0.0, 0.0, 0.0)
    s.camera1.position.setValue(s.basePosition1)
    s.camera1.viewportMapping.setValue(SoCamera.LEAVE_ALONE)
    left = nearZ * s.proj_raw[1][0]
    right = nearZ * s.proj_raw[1][1]
    top = nearZ * (-s.proj_raw[1][2])
    bottom = nearZ * (-s.proj_raw[1][3])
    aspect = (2 * nearZ / (top - bottom)) / (2 * nearZ * (right - left))
    s.camera1.nearDistance.setValue(nearZ)
    s.camera1.farDistance.setValue(farZ)
    s.camera1.left.setValue(left)
    s.camera1.right.setValue(right)
    s.camera1.top.setValue(top)
    s.camera1.bottom.setValue(bottom)
    s.camera1.aspectRatio.setValue(aspect)
  
  def extractrotation(s): #extract rotation quaternion
    s.qw = sqrt(numpy.fmax(0, 1 + s.transfmat[0][0] + s.transfmat[1][1] + s.transfmat[2][2])) / 2
    s.qx = sqrt(numpy.fmax(0, 1 + s.transfmat[0][0] - s.transfmat[1][1] - s.transfmat[2][2])) / 2
    s.qy = sqrt(numpy.fmax(0, 1 - s.transfmat[0][0] + s.transfmat[1][1] - s.transfmat[2][2])) / 2
    s.qz = sqrt(numpy.fmax(0, 1 - s.transfmat[0][0] - s.transfmat[1][1] + s.transfmat[2][2])) / 2
    s.qx = copysign(s.qx, s.transfmat[2][1] - s.transfmat[1][2]);
    s.qy = copysign(s.qy, s.transfmat[0][2] - s.transfmat[2][0])
    s.qz = copysign(s.qz, s.transfmat[1][0] - s.transfmat[0][1])
    
  def extracttranslation(s):
    s.hmdpos = SbVec3f(s.transfmat[0][3], s.transfmat[1][3], s.transfmat[2][3])
      

  def draw(s):
    #s.vr_compositor.waitGetPoses(s.poses, openvr.k_unMaxTrackedDeviceCount, None, 0)
    s.vr_compositor.waitGetPoses(s.poses, None)
    headPose = s.poses[openvr.k_unTrackedDeviceIndex_Hmd]
    if not headPose.bPoseIsValid:
      return True

    headToWorld = headPose.mDeviceToAbsoluteTracking
    s.transfmat = numpy.array([ [headToWorld.m[j][i] for i in range(4)] for j in range(3) ])
    s.extractrotation()
    hmdrot = SbRotation(s.qx, s.qy, s.qz, s.qw)
    s.extracttranslation()

    for eye in range(2):
      glBindFramebuffer(GL_FRAMEBUFFER, s.frame_buffers[eye])
      #coin3d rendering
      glUseProgram(0)
      if eye == 0:
        s.camera0.orientation.setValue(hmdrot)
        s.camera0.position.setValue(s.basePosition0 + s.hmdpos)
        s.m_sceneManager.setSceneGraph(s.rootScene0)
      if eye == 1:
        s.camera1.orientation.setValue(hmdrot)
        s.camera1.position.setValue(s.basePosition1 + s.hmdpos)
        s.m_sceneManager.setSceneGraph(s.rootScene1)
      glEnable(GL_CULL_FACE)
      glEnable(GL_DEPTH_TEST)
      s.m_sceneManager.render()
      glDisable(GL_CULL_FACE)
      glDisable(GL_DEPTH_TEST)
      glClearDepth(1.0)
      #end coin3d rendering
      s.vr_compositor.submit(s.eyes[eye], s.textures[eye])
    return True

if __name__ == "__main__":
  t=threading.Thread(target=OpenVRTest)
  t.daemon = True
  t.start()
