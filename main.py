"""

PoultryGeist
You'll Be Running Chicken

"""
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
# Import the main render pipeline class
from rpcore import RenderPipeline
from panda3d.core import load_prc_file_data

class Application(ShowBase):
	'''
	The default Application class which holds the code for
	Panda3D to run the game
	'''
	def __init__(self):
		#Modify the Panda3D config on-the-fly
		#In this case, edit the window title
		load_prc_file_data("", "window-title PoultryGeist")

		# Construct and create the pipeline
		self.render_pipeline = RenderPipeline()
		self.render_pipeline.create(self)

		# Set the time
		self.render_pipeline.daytime_mgr.time = "20:15"

		# Initialise the SceneManager
		self.sceneMgr = SceneManager(self)

		# Add the sceneMgr to run as a task


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
		'''
		self.scene = scene
		self.app.render = self.scene.render_tree

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
		self.add_model("resources/ground", scale=(5,5,5), key="ground")
		self.add_model("resources/corn.egg", isActor=True, key="corn", anims={})
		for x in range(25):
			for z in range(25):
				if (x-12)**2+(z-12)**2 > 25:
					self.add_model("resources/corn.egg", (x*5, z*5, 0), instanceTo="corn")

	def event_run(self, task):
		pass

Application().run()
