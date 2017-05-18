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

import sys

#Import the C++ Panda3D modules
from panda3d.core import WindowProperties
from panda3d.core import KeyboardButton
from panda3d.core import AntialiasAttrib
from panda3d.core import LPoint3, LVector3
from panda3d.core import load_prc_file_data, Fog

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
		print("PoultryGeist Debug:	Setting Model Resolution to {}".format(self.quality.upper()))

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
		# Get the cursor and X, Y position of it
		md = self.win.getPointer(0)
		x = md.getX()
		y = md.getY()
		# Get the change in mouse position
		if self.win.movePointer(0, int(self.width/2), int(self.height/2)):
			self.heading = self.heading - (x - self.width//2) * 0.2
			self.pitch = self.pitch - (y - self.height//2) * 0.2
		self.pitch += math.sin(math.radians(task.time)) * 0.5
		# Limit the camera pitch
		if self.pitch < -45:
			self.pitch = -45
		if self.pitch > 45:
			self.pitch = 45
		# Rotate the camera accordingly
		self.camera.setHpr(self.heading, self.pitch, 0)
		# Get a 3D vector of the camera's direction
		dir = self.camera.getMat().getRow3(1)
		# Get the change in time since the previous frame
		elapsed = task.time - self.last
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
		if is_down(self.switch_button):
			self.sceneMgr.load_scene(MenuScene(self) if isinstance(self.sceneMgr.scene, IntroScene) else IntroScene(self))

		# Dunno what this is for
		self.focus = self.camera.getPos() + (dir * 5)
		# Store the frame time for the next loop
		self.last = task.time
		return Task.cont

	def move(self, forward, dir, elapsed):
		'''
		Move the camera forward or backwards
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
		self.load_scene(MenuScene(app))

	def load_scene(self, scene):
		'''
		Load a new scene into the game
		TODO: Fix the issue where existing objects remain in the scene!!!
		'''
		self.scene = scene
		self.app.render = self.scene.render_tree

	def runSceneTasks(self, task):
		'''
		Run the event update for the current scene
		'''
		print(task.time)
		pass

class Scene:
	'''
	Holds all of the required details about a scene of the game. Including tasks
	and render tree for Panda3D.
	'''
	def __init__(self, app, event_function):
		self.models = {}
		self.loader = app.loader
		self.render_tree = app.render
		self.event_run = event_function

	def add_model(self, model, pos=(0,0,0), scale=(1,1,1), instanceTo=None, isActor=False, key=None, anims={}, parent=None):
		'''
		Adds a model to the Scenes render tree
		'''
		if instanceTo is None:
			if isActor:
				model = Actor(model, anims)
			else:
				model = self.loader.loadModel(model)
			model.setPos(*pos)
			model.setScale(*scale)
			model.reparentTo(self.render_tree if parent is None else self.models.get(parent))
		else:
			model = self.render_tree.attachNewNode("model_placeholder")
			model.setPos(*pos)
			model.setScale(*scale)
			self.models[instanceTo].instanceTo(model)
		self.models[key if key is not None else len(self.models)] = model

class MenuScene(Scene):
	'''
	A subclass of the Scene class to handle the main menu
	and all of it's required tasks + events
	'''
	def __init__(self, app):
		self.models = {}
		self.loader = app.loader
		self.render_tree = app.render
		fog = Fog("corn_fog")
		fog.setColor(0.8,0.8, 0.8)
		fog.setLinearRange(0, 320)
		fog.setLinearFallback(45, 160, 320)
		render.attachNewNode(fog)
		render.setFog(fog)

	def event_run(self, task):
		pass


class IntroScene(Scene):
	'''
	A subclass of the Scene class to handle the main menu
	and all of it's required tasks + events
	'''
	def __init__(self, app):
		self.models = {}
		self.loader = app.loader
		self.render_tree = app.render
		self.add_model("resources/{}/ground".format(app.quality), scale=(5,5,5), key="ground")
		self.add_model("resources/{}/corn.egg".format(app.quality), isActor=True, key="corn", anims={})
		for x in range(25):
			for z in range(25):
				if (x-12)**2+(z-12)**2 > 25:
					self.add_model("resources/{}/corn.egg".format(app.quality), (x*5, z*5, 0), instanceTo="corn")
		# Create some exponential fog
		fog = Fog('exp_fog')
		fog.setColor(0.8, 0.8, 0.8)
		fog.setExpDensity(0.005)
		render.setFog(fog)




	def event_run(self, task):
		pass

Application().run()
