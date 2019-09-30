from sdl2 import *

from time import time

from pivy.coin import SoSeparator
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
from pivy.coin import SoRotation

from OpenGL.GL import *


def main():
    width = 1600
    height = 1200
    timelimit = 10
    modeltranslation = 200
    
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow (b"benchmark",
      SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
      width, height, SDL_WINDOW_SHOWN|SDL_WINDOW_OPENGL)
    context = SDL_GL_CreateContext(window)
    SDL_GL_SetSwapInterval(0) #no v-sync
    
    #coin3d setup
    vpRegion = SbViewportRegion(width, height,)
    m_sceneManager = SoSceneManager()
    m_sceneManager.setViewportRegion(vpRegion)
    m_sceneManager.setBackgroundColor(SbColor(0.0, 0.0, 0.8));
    rootScene = SoSeparator()
    rootScene.ref()
    camera = SoFrustumCamera()
    basePosition = SbVec3f(0.0, 0.0, 0.0)
    camera.position.setValue(basePosition)
    camera.focalDistance.setValue(5.0);
    camera.viewportMapping.setValue(SoCamera.LEAVE_ALONE)
    camera.nearDistance.setValue(0.1);
    camera.farDistance.setValue(10000.0);
    rootScene.addChild(camera)
    light = SoDirectionalLight()
    light2 = SoDirectionalLight()
    rootScene.addChild(light)
    rootScene.addChild(light2)
    trans = SoTranslation()
    trans.translation.setValue([0,0,-modeltranslation])
    rotat = SoRotation()
    rotat.rotation.setValue(coin.SbVec3f(0,1,0),0)
    rootScene.addChild(trans)#translation have to be earlier than translated object
    rootScene.addChild(rotat)
    sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
    rootScene.addChild(sg) #get active scenegraph
    m_sceneManager.setSceneGraph(rootScene)
    
    notfinished = 1
    angle = 0
    frames =  0
    start = time()
    # Loop until time limit happens
    while notfinished:
        glUseProgram(0)
        #coin3d rendering
        angle = angle + 0.001
        frames = frames + 1
        rotat.rotation.setValue(coin.SbVec3f(0,1,0),angle)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        m_sceneManager.render()
        glDisable(GL_CULL_FACE)
        glDisable(GL_DEPTH_TEST)
        glClearDepth(1.0)
        # Swap front and back buffers
        SDL_GL_SwapWindow(window)
        stop = time()
        elapsed = stop - start
        if elapsed > timelimit:
            notfinished = 0
            
    print(frames, ' in ', elapsed, 'seconds, ', (frames/elapsed), 'fps')
    rootScene.unref()
    SDL_GL_DeleteContext(context)
    SDL_DestroyWindow(window)
    SDL_Quit()


if __name__ == "__main__":
    import threading
    t=threading.Thread(target=main)
    t.daemon = True
    t.start()
