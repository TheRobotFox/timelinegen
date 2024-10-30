from os import system,mkdir
from Visuals import *
from actors import *
from shutil import rmtree
from sys import argv, exit


audio_out=wave.open("data/audio.wav","wb")
audio_out.setnchannels(2)
audio_out.setsampwidth(2)
audio_out.setframerate(48000)

# abtract layer for drawing basic shapes
class Frame:
	def __init__(self, num, Resolution):
		self.num = num
		self.img = Image.new("RGB", Resolution)

	def save(self, path):
		self.img.save(path+str(self.num)+".png")
	def setAlpha(self, p):
		self.img.putalpha(int(p*255))
	def copy(self):
		res = self.__class__
		res.img = self.img.copy()
		res.num=self.num
		return res

	def open(self, path):
		self.img.open(path)

	def show(self):
		self.img.show()

class Video:
	def __init__(self, Scriptfile = 0):
		global fonts
		global Resolution
		self.Scriptfile = Scriptfile
		
		self.FPS = 30
		self.Resolution = [1920, 1080]
		self.actors = [Actor_bez,Actor_goto,Actor_setVar,AddSpecialDate,RemoveSpecialDate,Wait, SetTape, addMark, rmMark]
		self.videoobjects = [TimeLine,Text,Font, TuringMaschine]
		self.frames=0
		self.currentTime=0
		self.FrameList = []
		self.actorlist = []
		self.activeactors=[]
		self.objectsList = {}

	def RaiseException(self, error, linenum = -1, line = -1):
		if line == -1:
			print(f"\n\nInternal exception:\n{error}\n\n")
		else:
			print(f"\n\nException at line {linenum+1}:\n{line}\n{error}\n")
		print("Exiting!")
		exit(0)

	def checkCommandLine(self, line):
		pass

	def setResolution(self, Resolution):
		self.Resolution = Resolution

	def toList(self, string):
		argv = []
		string=string[1:-1]
		if len(string):
			instring=0
			intuple=0
			start=0
			# print("str",string)
			for i in range(len(string)):
				if string[i] == "\"":
					instring= not instring
				if string[i] == "(":
					intuple=1
				if string[i] == ")":
					intuple=0
				if string[i]=="," and instring==0 and intuple==0:
					argv.append(string[start:i].strip())
					# print(string[start:i], string[i], instring)
					start=i+1
			argv.append(string[start:])


			print(argv)
			for arg in range(len(argv)):
				if argv[arg][0]=="\"" and argv[arg][-1]=="\"":
					argv[arg]=bytes(argv[arg][1:-1], "utf-8").decode("unicode_escape")
				elif argv[arg][0]=="(":
					argv[arg]=tuple(self.toList(argv[arg]))
				elif argv[arg][0]=="&":
					if argv[arg][1:] in self.objectsList:
						argv[arg]=self.objectsList[argv[arg][1:]]
					else:
						return "Object not found! " + argv[arg][1:]
				else:
					try:
						argv[arg]=float(argv[arg])
					except ValueError as e:
						print(e)
						exit(0)
			#print(argv)
		return argv

	def createActor(self, actor):
		return actor[0](*actor[1])

	def interpretScript(self,Scriptfile = 0):
		if Scriptfile and self.Scriptfile:
			self.RaiseException("Two Scriptfiles where specified!")
		if Scriptfile:
			self.Scriptfile = Scriptfile
		if not self.Scriptfile:
			self.RaiseException("No Scriptfile was specified!")
		self.out = self.Scriptfile

		Script = open(self.Scriptfile, "r").readlines()
		command = ""
		for i,line in enumerate(Script):
			line=line.strip()
			if line.startswith("//"):
				continue
			if line.startswith("[") and line.endswith("]"):
				self.frames=max(self.currentTime*self.FPS,self.frames)
				self.currentTime=float(line[1:-1])
				print(self.currentTime)
				continue

			if ";" in line:

				command+=line[:line.index(";")]
				result = "Unknown command"

				for VideoObject in self.videoobjects:
					identifier = VideoObject.getidentifier()
					if command.strip().split(" ")[0]==identifier:
						command=command[len(identifier):]
						if not "(" in command and not ")" in command:
							try:
								self.videoobjects[command]=VideoObject()
							except TypeError as e:
								self.RaiseException("Could not create VideoObject!\n "+str(e),i,command)

						elif "(" in command and ")" in command:
							args = self.toList(command[command.index("("):])
							if type(args)!=list:
								self.RaiseException(args, i, line)
							if len(args):
								self.objectsList[command.split("(")[0].strip()]=VideoObject(*args)
							else:
								self.objectsList[command.split("(")[0].strip()]=VideoObject()

						result = 0
						break
				if "." in command and result:
					Object = self.objectsList[command.split(".")[0].strip()]
					identifier = command[command.index(".")+1:]
					if Object:
						for actor in self.actors:
							if identifier[:identifier.index("(")].strip()==actor.getidentifier():
								if "(" in identifier and ")" in identifier:
									self.actorlist.append((actor,[Object,self.currentTime,* self.toList(identifier[identifier.index("("):])]))
									self.currentTime+=self.createActor(self.actorlist[-1]).gettime()
									result=0

					
				if result:
					self.RaiseException(result,i,command)

				command=""
				continue

			command+=line
		if command.strip():
			self.RaiseException(f"Expected \";\" got \"\"", i, line)
		self.frames=max(self.currentTime*self.FPS,self.frames)

	def Render(self):
		try:
			rmtree("data/frames/")
		except:
			pass

		mkdir("data/frames")
		print("Baking",self.frames)
		audio=False
		for i in range(int(self.frames+1)):
			self.Bakeframe(i)
		for VideoObject in self.objectsList.values():
			if type(VideoObject)==TimeLine:
				audio_out.writeframes(bytes(VideoObject.audio_buff))
				audio = True
		print("Rendering",self.frames)
		for frame in self.FrameList:
			frame.save("data/frames/")
		try:
			mkdir("output")
		except:
			pass
		system("ffmpeg -r "+str(self.FPS)+" -i data/frames/%d.png " + ("-i data/audio.wav" if audio else "") + "-vcodec libx264 -b 10MB \"output/" + self.out + ".mp4\" -y")
		print("Done!")

	def Bakeframe(self,i):
		self.FrameList.append(Frame(i,self.Resolution))
		for e,actor in enumerate(self.actorlist):
			if actor:
				cactor=self.createActor(actor)
				if i/self.FPS>=cactor.time_start:
					self.activeactors.append(cactor)
					self.actorlist[e]=0
					print(i,cactor)
		for actor in self.activeactors:
			res = actor.work(i/self.FPS)
			if res:
				self.RaiseException(res[1])
		for VideoObject in self.objectsList.values():
			if VideoObject.vars["alpha"]==1:
				VideoObject.Draw(self.FrameList[-1])
			elif VideoObject.vars["alpha"]==0:
				pass
			else:
				overlay = self.FrameList[-1].copy()
				# overlay.setAlpha(VideoObject.getVar("alpha")[1])
				VideoObject.Draw(overlay)
				now = self.FrameList[-1].img
				overlay.img.putalpha(int(255*VideoObject.getVar("alpha")[1]))
				overlay.img
				self.FrameList[-1].img.paste(overlay.img, (0,0), overlay.img)


	def Renderframe(self, time):
		self.FrameList.append(Frame(0,Resolution))
		for actor in self.actorlist:
			actor.work(time)
			if actor.gettime()+actor.time_start < time:
				#print(actor, (actor.gettime()+actor.time_start))
				res = actor.work((actor.gettime()+actor.time_start))
				if res:
					self.RaiseException(res[1])

		for VideoObject in self.objectsList.values():
			# if "SpecialDates" in VideoObject.vars:
			# 	VideoObject.Draw(self.FrameList[-1])
			VideoObject.Draw(self.FrameList[-1])
		self.FrameList[-1].show()




if len(argv) !=2:
	print("No VideoScript specified!")
	exit(0)
Vid = Video(argv[1])
Vid.interpretScript()
Vid.setResolution([1920,1920//6])
# Vid.Bakeframe(0)
# Vid.Renderframe(0)
Vid.Render()
