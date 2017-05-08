"""

PoultryGeist
You'll Be Running Chicken

"""
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
# Import the main render pipeline class
from rpcore import RenderPipeline

class Application(ShowBase):

	def __init__(self):
		# Construct and create the pipeline
		self.render_pipeline = RenderPipeline()
		self.render_pipeline.create(self)

		# Do normal stuff here
		corn = Actor("resources/corn.egg", {})#{"sway":"resources/sway.egg"})
		# corn.loop("sway")
		corn.setPos(0,0,0)
		for x in range(50):
			for z in range(50):
				placeholder = render.attachNewNode("Corn-Placeholder")
				placeholder.setPos(x*5, z*5, 0)
				# Directions are x, z, y
				corn.instanceTo(placeholder)

Application().run()
