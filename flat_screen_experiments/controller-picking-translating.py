# The example shows picking and moving shapes with a ray shot from a controller
# It requires getObjectInfoRay function https://github.com/kwahoo2/FreeCAD/commit/e595da35c1f8258b2cf66e729966d79b1a9335ae
# In this example a coin shape (loaded from *.iv file) representing controller is moved by openvr input
# Save the "right_con.iv" file in the FreeCAD bin directory, otherwise a simple cube will be used as fallback

import FreeCAD as App, FreeCADGui as Gui, Part, time, sys, math
from PySide2 import QtGui, QtCore
from pivy import coin
import openvr
import numpy as np

class Tracker(object):
    def __init__(self):
        self.vr = openvr.init(openvr.VRApplication_Other)
        self.vrsystem = openvr.VRSystem()
        self.view = Gui.ActiveDocument.ActiveView
        self.doc = App.ActiveDocument
        self.poses = []  # will be populated with proper type after first call
        self.trigger_state = 'released'
        self.sel_obj = 'None'
        self.sel_comp_str = ''
        self.dragging_in_progress = False
        self.obj_plac_at_sel = App.Placement()
        self.con_plac_at_sel = App.Placement()
        self.sg = self.view.getSceneGraph()
        self.tracker_sep = coin.SoSeparator() # this separator contains everything that moves with controller/tracker
        unpickable = coin.SoPickStyle()
        unpickable.style = coin.SoPickStyle.UNPICKABLE # everything after this will be not pickable
        self.tracker_sep.addChild(unpickable)
        self.sg.addChild(self.tracker_sep)
        self.add_controller_shape()
        self.add_ray_node()
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.frame_update)
        App.ActiveDocument.recompute()
        Gui.runCommand('Std_PerspectiveCamera',1)
        self.timer.start(16) #60 fps
        App.Console.PrintMessage('timer started')

    def add_controller_shape(self):
        con_sep = coin.SoSeparator()
        # Read the file
        con_node = self.read_file("right_con.iv")
        if (con_node == None):
            con_node = coin.SoSeparator()
            con_cube = coin.SoCube()
            con_cube.width.setValue(10)
            con_cube.height.setValue(5)
            con_cube.depth.setValue(30)
            controller_node.addChild(con_cube) #  replace controller with simple cube if the iv file not found
        self.controller_coords = coin.SoTransform()
        con_sep.addChild(self.controller_coords)
        con_sep.addChild(con_node)
        self.tracker_sep.addChild(con_sep)

    def add_ray_node(self):
        r_sep = coin.SoSeparator()
        self.ray_vtxs = coin.SoVertexProperty()
        self.ray_vtxs.vertex.set1Value(0, 0, 0, 0)  # Set first vertex, later update to center of the controller
        self.ray_vtxs.vertex.set1Value(1, 0, 0, 1)  # Set second vertex, later update to point of intersection ray with hit object
        ray_line = coin.SoLineSet()
        ray_line.vertexProperty = self.ray_vtxs
        self.ray_col = coin.SoBaseColor() # red sphere to show intersection point
        self.ray_col.rgb = coin.SbColor(1, 0, 0)
        r_sep.addChild(self.ray_col)
        r_sep.addChild(ray_line)
        self.sph_trans = coin.SoTranslation()
        self.sph_trans.translation.setValue(0, 0, 0)
        r_sep.addChild(self.sph_trans)
        ray_sph = coin.SoSphere()
        ray_sph.radius.setValue(20)
        r_sep.addChild(ray_sph)
        self.tracker_sep.addChild(r_sep)

    def pick_ray(self, pos, rot, dir_vec):
        start_vec = pos
        self.ray_vtxs.vertex.set1Value(0, start_vec)
        fcstart = self.coinvec_to_fcvec(start_vec)
        fcdir = self.coinvec_to_fcvec(dir_vec)
        # App.Console.PrintMessage("Start" + str(fcstart) + "dir" + str(fcdir) +"\n")
        info = self.view.getObjectInfoRay(fcstart, fcdir)
        if (info): #FIXME script will fail if picked point lost during draggin
            # App.Console.PrintMessage("Selected info" + str(info) +"\n")
            end_ray = coin.SbVec3f(info['x'], info['y'], info['z'])
            self.sph_trans.translation.setValue(end_ray)
            self.ray_vtxs.vertex.set1Value(1, end_ray)
            if not self.dragging_in_progress:
                obj = self.doc.getObject(info['Object'])
                comp_str = info['Component']
                if ((obj != self.sel_obj) or (comp_str != self.sel_comp_str)):
                    Gui.Selection.clearSelection()
                    Gui.Selection.addSelection(info['Document'], info['Object'], info['Component'], info['x'], info['y'], info['z'])
                    self.sel_obj = obj
                    self.sel_comp_str = comp_str
            fcbase = self.coinvec_to_fcvec(pos)
            fcrot = self.coinrot_to_fcrot(rot)
            con_plac = App.Placement(fcbase, fcrot)
            App.Console.PrintMessage("Trigger " + str(self.trigger_state) +"\n")
            if self.trigger_state == 'just_pressed':
                self.dragging_in_progress = True
                self.obj_plac_at_sel = obj.Placement
                self.con_plac_at_sel = con_plac
                self.ray_col.rgb = coin.SbColor(0, 1, 0)
            elif self.trigger_state == 'pressed':
                self.move_obj(con_plac) # expensive
            elif self.trigger_state == 'just_released':
                self.move_obj(con_plac)
                self.ray_col.rgb = coin.SbColor(1, 0, 0)
                self.dragging_in_progress = False
        else:
            end_ray = start_vec + 2000 * dir_vec # ray length 2000 when nothing is selected
            self.ray_vtxs.vertex.set1Value(1, end_ray)
            self.sel_obj = None
            Gui.Selection.clearSelection()

    def get_ray_axis(self, rot):
        x = rot.getValue()[0]
        y = rot.getValue()[1]
        z = rot.getValue()[2]
        w = rot.getValue()[3]
        mat02 = 2*x*z+2*y*w
        mat12 = 2*y*z-2*x*w
        mat22 = 1-2*x*x-2*y*y
        ray_axis = coin.SbVec3f(mat02, mat12, mat22)
        return ray_axis

    def update_controller(self, pos, rot, state):
        self.controller_coords.rotation.setValue(rot)
        self.controller_coords.translation.setValue(pos)
        self.process_controller_state(state)
        self.pick_ray(pos, rot, - self.get_ray_axis(rot)) # //direction is reversed controller Z get_ray_axis

    def read_file(self, filename):
        # Open the input file
        scene_input = coin.SoInput()
        if not scene_input.openFile(filename):
            App.Console.PrintMessage("Cannot open file:" + str(filename) +"\n")
            return None

        # Read the whole file into the database
        graph = coin.SoDB.readAll(scene_input)
        if graph == None:
            App.Console.PrintMessage("Problem reading file" + str(filename) +"\n")
            return None

        scene_input.closeFile()
        return graph

    def extract_coin_rotation(self, transfmat): #extract rotation quaternion
        qw = math.sqrt(np.fmax(0, 1 + transfmat[0][0] + transfmat[1][1] + transfmat[2][2])) / 2
        qx = math.sqrt(np.fmax(0, 1 + transfmat[0][0] - transfmat[1][1] - transfmat[2][2])) / 2
        qy = math.sqrt(np.fmax(0, 1 - transfmat[0][0] + transfmat[1][1] - transfmat[2][2])) / 2
        qz = math.sqrt(np.fmax(0, 1 - transfmat[0][0] - transfmat[1][1] + transfmat[2][2])) / 2
        qx = math.copysign(qx, transfmat[2][1] - transfmat[1][2]);
        qy = math.copysign(qy, transfmat[0][2] - transfmat[2][0])
        qz = math.copysign(qz, transfmat[1][0] - transfmat[0][1])
        rot = coin.SbRotation(qx, qy, qz, qw)
        return rot

    def extract_coin_translation(self, transfmat):
        pos = coin.SbVec3f(transfmat[0][3], transfmat[1][3], transfmat[2][3])
        return pos

    def coinvec_to_fcvec(self, vec):
        fcvec = App.Vector(vec.getValue()[0], vec.getValue()[1], vec.getValue()[2])
        return fcvec

    def coinrot_to_fcrot(self, rot):
        fcrot = App.Rotation(rot.getValue()[0], rot.getValue()[1], rot.getValue()[2], rot.getValue()[3])
        return fcrot

    def process_controller_state(self, state):
        if (state.ulButtonPressed >> 33 & 1): # trigger pressed
            #App.Console.PrintMessage("Trigger is pressed\n")
            if self.trigger_state == 'released' or self.trigger_state == 'just_released':
                self.trigger_state = 'just_pressed'
            elif self.trigger_state == 'pressed' or self.trigger_state == 'just_pressed':
                self.trigger_state = 'pressed'
        else:
            if self.trigger_state == 'pressed' or self.trigger_state == 'just_pressed':
                self.trigger_state = 'just_released'
            elif self.trigger_state == 'released' or self.trigger_state == 'just_released':
                self.trigger_state = 'released'

    def move_obj(self, con_plac):
        old_obj_plac = self.obj_plac_at_sel
        old_con_plac = self.con_plac_at_sel
        # App.Console.PrintMessage("Start" + str(fcstart) + "dir" + str(fcdir) +"\n"
        plt_con = con_plac * old_con_plac.inverse() # calculating transformation between two controller poses
        obj_plac = plt_con * old_obj_plac
        self.sel_obj.Placement = obj_plac

    def frame_update(self):
        try:
            self.poses = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0, openvr.k_unMaxTrackedDeviceCount)
            for i in range(1, len(self.poses)):
                pose = self.poses[i]
                if not pose.bDeviceIsConnected:
                    continue
                if not pose.bPoseIsValid:
                    continue
                device_class = openvr.VRSystem().getTrackedDeviceClass(i)
                if not device_class == openvr.TrackedDeviceClass_Controller:
                    continue
                controllerPose = pose.mDeviceToAbsoluteTracking
                result, pControllerState = self.vrsystem.getControllerState(i)
                conrot = self.extract_coin_rotation(controllerPose)
                conpos = self.extract_coin_translation(controllerPose)
                conpos_mm = conpos * 1000
                self.update_controller(conpos_mm, conrot, pControllerState)
        except:
            pass

    def stop(self):
        self.timer.stop()
        openvr.shutdown()
        self.sg.removeChild(self.tracker_sep)

tracker = Tracker()

#To stop the tracking, type:
#tracker.stop()
