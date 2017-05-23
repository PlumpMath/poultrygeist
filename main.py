#!/usr/bin/env python3
"""

PoultryGeist
You'll Be Running Chicken

"""
# Import the Python Panda3D modules
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.filter.CommonFilters import *
from direct.task.Task import Task

# Import the main render pipeline class
from rpcore import RenderPipeline
from rpcore import PointLight, SpotLight
from rpcore.util.movement_controller import MovementController

import sys
from time import sleep
import math

#Import the C++ Panda3D modules
from panda3d.core import WindowProperties, AntialiasAttrib
from panda3d.core import KeyboardButton, load_prc_file_data
from panda3d.core import LPoint3, LVector3, Vec3, Fog

class Application(ShowBase):
	'''
	The default Application class which holds the code for
	Panda3D to run the game
	'''
	def __init__(self):
		#Modify the Panda3D config on-the-fly
		#In this case, edit the window title
		load_prc_file_data("", """window-title PoultryGeist
								  threading-model /Draw
								  multisamples 2
								  framebuffer-multisample 1
							   """)

		# Construct and create the pipeline
		self.render_pipeline = RenderPipeline()
		self.render_pipeline.create(self)

		self.width, self.height = (800, 600)
		render.setAntialias(AntialiasAttrib.MAuto)

		# Set the model quality, (low or high)
		self.quality = "low"
		print("[>] PoultryGeist:		Setting Model Resolution to {}".format(
														self.quality.upper()))

		# Set the time
		self.render_pipeline.daytime_mgr.time = "20:15"

		# Set the current viewing target
		self.focus = LVector3(55, -55, 20)
		self.heading = 180
		self.pitch = 0
		self.mousex = 0
		self.mousey = 0
		self.last = 0
		self.mousebtn = [0, 0, 0]

		# Turn off normal mouse controls
		self.disableMouse()



		# Hide the cursor
		props = WindowProperties()
		props.setCursorHidden(True)
		props.setMouseMode(WindowProperties.M_relative)
		# Lower the FOV to make the game more difficult
		self.win.requestProperties(props)
		self.camLens.setFov(90)

		# Set the camera control task
		taskMgr.add(self.controlCamera, "camera-task")

		# Register the buttons for movement
		self.w_button = KeyboardButton.ascii_key('w'.encode())
		self.s_button = KeyboardButton.ascii_key('s'.encode())

		self.switch_button = KeyboardButton.ascii_key('p'.encode())

		# Initialise the SceneManager
		self.sceneMgr = SceneManager(self)

		# Add the sceneMgr to run as a task
		taskMgr.add(self.sceneMgr.runSceneTasks, "scene-tasks")

	def controlCamera(self, task):
		'''
		Control the camera to move more nicely
		'''
		# Get the change in time since the previous frame
		elapsed = task.time - self.last
		# Get the cursor and X, Y position of it
		md = self.win.getPointer(0)
		x = md.getX()
		y = md.getY()
		# Get the change in mouse position
		if self.win.movePointer(0, int(self.width/2), int(self.height/2)):
			# And set the heading and pitch accordingly
			self.heading = self.heading - (x - self.width//2) * 0.2
			self.pitch = self.pitch - (y - self.height//2) * 0.2
		# Make the camera bob slightly
		# TODO Make this only occur whilst moving and return to default when stopped.
		self.pitch += math.sin(math.radians(task.time)*180) * 0.25 * (elapsed/0.167)

		# Limit the camera pitch
		if self.pitch < -75:
			self.pitch = -75
		if self.pitch > 75:
			self.pitch = 75
		# Rotate the camera accordingly
		self.camera.setHpr(self.heading, self.pitch, 0)
		# Get a 3D vector of the camera's direction
		dir = self.camera.getMat().getRow3(1)
		# If this is the first frame then set elapsed to 0
		if self.last == 0:
			elapsed = 0
		# Alias the really long function to a short name
		is_down = base.mouseWatcherNode.is_button_down
		# Check for a w press and move forward
		if is_down(self.w_button):
			self.move(True, dir, elapsed)
		# Check for an s press and move backwards
		if is_down(self.s_button):
			self.move(False, dir, elapsed)
		# Check for a scene switch and switch the scene
		if is_down(self.switch_button):
			self.sceneMgr.load_scene(MenuScene(self) if isinstance(self.sceneMgr.scene, IntroScene) else IntroScene(self))

		# TODO Dunno what this is for
		self.focus = self.camera.getPos() + (dir * 5)
		# Store the frame time for the next loop
		self.last = task.time
		return Task.cont

	def move(self, forward, dir, elapsed):
		'''
		Move the camera forward or backwards
		For testing ONLY at the moment
		'''
		if forward:
			self.focus += dir * elapsed * 30
		else:
			self.focus -= dir * elapsed * 30
		# Set the position of the camera based on the direction
		self.camera.setPos(self.focus - (dir * 5))

class SceneManager:
	'''
	The SceneManager to handle the events and tasks of each scene as well as
	handle scene swapping.
	'''
	def __init__(self, app):
		self.app = app
		self.scene = None
		self.load_scene(MenuScene(app))

	def load_scene(self, scene):
		'''
		Load a new scene into the game
		'''
		# TODO Fix this to actually work
		# if self.scene:
		# 	for child in self.app.render.getChildren():
		# 		child.detachNode()
		# 		print(child)
		self.scene = scene
		self.app.render = self.scene.render_tree
		# for child in scene.render_tree.getChildren():
		# 	child.reparentTo(self.app.render)
		self.scene.init_scene()

	def runSceneTasks(self, task):
		'''
		Run the event update for the current scene
		'''
		# print(task.time)
		pass

class Scene:
	'''
	Holds all of the required details about a scene of the game. Including tasks
	and render tree for Panda3D.
	'''
	def add_model(self, model, pos=(0,0,0), scale=(1,1,1), instanceTo=None, isActor=False, key=None, anims={}, parent=None):
		'''
		Adds a model to the Scenes render tree
		'''
		# Check if the model is being instanced to an existing model
		if instanceTo is None:
			# Check if the model is an Actor or static model
			if isActor:
				# Add the model as an Actor with the required animations
				model = Actor(model, anims)
			else:
				# Add the model as a static model
				model = self.loader.loadModel(model)
			# Set the position of the model
			model.setPos(*pos)
			# Set the scale
			model.setScale(*scale)
			# Parent the model to either the render tree or the parent (if applicable)
			model.reparentTo(self.render_tree if parent is None else self.models.get(parent))
		else:
			# If the model is being instanced to an existing model
			# Create a new empty node and attach it to the render tree
			model = self.render_tree.attachNewNode("model_placeholder")
			# Set the position and scale of the model
			model.setPos(*pos)
			model.setScale(*scale)
			# Instance the model to the chosen object
			self.models[instanceTo].instanceTo(model)
		# Add the model to the scenes model dictionary
		self.models[key if key is not None else len(self.models)] = model
		# Return the model nodepath incase something else will use it later
		return model

	def init_scene(self):
		'''
		A placeholder function for running events when the scene is first loaded
		'''
		pass

class MenuScene(Scene):
	'''
	A subclass of the Scene class to handle the main menu
	and all of it's required tasks + events
	'''
	def __init__(self, app):
		self.app = app
		self.models = {}
		self.loader = app.loader
		self.render_tree = app.render
		# fog = Fog("corn_fog")
		# fog.setColor(0.8,0.8, 0.8)
		# fog.setLinearRange(0, 320)
		# fog.setLinearFallback(45, 160, 320)
		# render.attachNewNode(fog)
		# render.setFog(fog)

	def event_run(self, task):
		pass


class IntroScene(Scene):
	'''
	A subclass of the Scene class to handle the main menu
	and all of it's required tasks + events
	'''
	def __init__(self, app):
		self.app = app
		self.models = {}
		self.loader = app.loader
		self.render_tree = app.render
		# Add the ground model
		self.add_model("resources/{}/ground".format(app.quality), scale=(8,8,8), key="ground")
		# Create a corn model and add it in the bottom corner
		self.add_model("resources/{}/corn.egg".format(app.quality), pos=(-62, -62, 0), isActor=True, key="corn", anims={})
		# add the laser pointer to the scene
		# TODO is this needed in this scene
		m = self.add_model("resources/{}/laser.bam".format(app.quality), pos=(0, 0, 1), scale=(5,5,5))
		# Iterate a 25x25 square for the corn
		for x in range(25):
			for z in range(25):
				# Use amazing maths skills to create a 'lollypop' shape cutout
				if (x-12)**2+(z-12)**2 > 25 and (abs(x-12) > 1 or z > 12):
					# Add a corn instance to the scene
					self.add_model("resources/{}/corn.egg".format(app.quality), (x*5, z*5, 0), instanceTo="corn")
		# Prepare the scene with the RenderPipeline
		# (due to being exported from Blender with the BAM exporter)
		app.render_pipeline.prepare_scene(m)
		# TODO Add a test light
		spot = SpotLight()
		spot.pos = (20, 20, 15)
		spot.set_color_from_temperature(1800)#(0.5, 0.3, 0)
		spot.casts_shadows = True
		spot.shadow_map_resolution = 1024
		spot.energy = 20000
		spot.radius = 2000000
		spot.fov = 180
		# spot.look_at(0, 0, 0)
		app.render_pipeline.add_light(spot)

	def event_run(self, task):
		pass

	def init_scene(self):
		'''
		Set up the movement controller and begin the motion path.
		'''
		# Make the motion path
		mopath = ()
		# Create the controller for movement
		self.app.controller = MovementController(self.app)
		# Set the initial position
		self.app.controller.set_initial_position(Vec3(0, -60, 2), Vec3(-180, 0, 0))
		# Run the setup on the movement controller
		self.app.controller.setup()
		sleep(1)
		# Play the pre-defined motion path
		self.app.controller.play_motion_path(mopath, 3)
		pass

# Run the application
Application().run()
