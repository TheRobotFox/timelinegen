from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import numpy as np
import os
from shutil import rmtree
from threading import Thread


offset=100
fontsize=100

class Font:
	def __init__(self, name, size, color=(255,255,255)):
		self.font=ImageFont.truetype(name, size)
		self.color=color

class BkImage:
	def __init__(self, path, opacity=1):
		self.path=path
		self.opacity=opacity

	def Draw(self, img):
		if self.path:
			image=Image.open(self.path)
			scale=image.size[1]/img.size[1]
			newsize=(int(image.size[0]/scale),int(image.size[1]/scale))
			image=image.resize(newsize)
			image=ImageEnhance.Brightness(image).enhance(self.opacity)
			offset=(int((img.size[0]/2)-(image.size[0]/2)),0)#int((img.size[1]/2)-(image.size[1]/2)))
			Image.Image.paste(img,image,offset)




class Text:
	def __init__(self, text, Font):
		self.Font=Font
		self.text=text
		self.pos=pos
	def Draw(img,pos):


class Date:
	def __init__(self, year, Font):
		self.year=int(year)
		self.Font=Font

	def Draw(img,pos):
		d = ImageDraw.Draw(img)
		d.text(pos,str(self.year),self.font.color,self.font.font)

class TimeLine:
	def __init__(self, year, Font, width=25, y_offset=45, color=(255,255,255), sections=2, width1=22, heigth1=45, subsections=11, width2=12, heigth2=30):
		self.year = year
		self.Font = Font
		self.width = width
		self.sections = sections
		self.Y = y_offset
		self.color = color
		self.subsections = int(subsections)
		self.width1 = width1
		self.height1 = heigth1
		self.width2 = width2
		self.height2 = heigth2
		self.SpecialDates = []

	def getfrac(self, num):
		return num-int(num)

	def Print(self, img, X, year):
		year=int(year)
		d = ImageDraw.Draw(img)
		color=self.Font.color
		font=self.Font.font
		for e in self.SpecialDates:
			if e.year==year:
				color=e.Font.color
				font=e.Font.font
				break
		w,h = d.textsize(str(year),font)
		d.text((X-w/2,self.Y-self.height1-h),str(year),color,font)
	

	def Draw(self, img):
		d = ImageDraw.Draw(img)
		self.Y+=img.size[1]/2
		pos=(0,self.Y,img.size[0],self.Y)
		d.line(pos,self.color,self.width)

		center=img.size[0]/2
		div=img.size[0]/(self.sections+1)
		sectionhalf=int(np.round(self.sections/2))
		for i in range(-sectionhalf-2,sectionhalf+2):
			X=int(center+div*i-self.getfrac(self.year)*div)
			d.line((X,int(self.Y-self.height1),X,int(self.Y+self.height1)),self.color,int(self.width1))
			self.Print(img, X, self.year+i)
			for sub in range(self.subsections):
				subpos=X+div/(self.subsections+1)*(sub+1)
				d.line((subpos,self.Y+self.height2,subpos,self.Y-self.height2),self.color,int(self.width2))
	
	def AddSpecialDate(self, year, font, size, color):
		self.SpecialDates.append(Date(year,Font(font, size, color)))

	def DelSpecialDate(self, year):
		for i in self.SpecialDates:
			if i.year==year:
				self.SpecialDates.remove(i)

class Frame:
	def __init__(self, img, TimeLine, Title, Text, BkImage):
		self.img=img
		self.TimeLine=TimeLine
		self.Title=Title
		self.Text=Text
		self.BkImage=BkImage

	def Draw(self):
		#self.clear()
		self.BkImage.Draw(self.img)
		self.TimeLine.Draw(self.img)

	def clear(self):
		self.img.paste((0,0,0),(0,0)+self.img.size)

	def save(self, path):
		self.img.save(path)

	def show(self):
		self.img.show()

class Actor:
	def __init__(self, func, start, args):
		self.start=start
		self.func=func
		self.end=end
		self.args=args

	def act(self,video,frame):
		if frame>self.start:
			self.func(video,frame-self.start, *self.args)

def beziere(start, end, t, slope):
	return start+(end-start)*((np.arctan((t-0.5)*slope*360)/np.arctan(slope*180))/2+0.5)

class Functions:
	def goto(self, frame, destination, end, slope=0.04):
		start=self.timelineargs[0]
		self.timelineargs[0] = beziere(start,destination,frame/end,slope)
		return end

	def wait(self, frame, end):
		return end

	def setframesize(self, string):
		self.size=tuple([int(i) for i in Script[0][1:-2].strip().split("x")])
		return 1

class Command:
	def __init__(self, function, name):
		self.function = function
		self.name = name
		self.args = []


class Video:
	def __init__(self, script, *kargs):
		self.Frames = []
		self.fps = 30
		self.size=(1920,1080)
		self.currentTime = 0.0
		self.Queue = []

		self.Variables = [
		Font("twcen.ttf"),
		[2013,0,25,45,(255,255,255),2,22,45,11,12,30],
		["1.png",1],
		["",0],
		["",0],
		[]
		]

		self.chunks = ["defaultFont","timeline","image","title","text","var"]
		self.varnames = [
		["year", "font", "width", "y_offset", "color", "sections", "width1", "heigth1", "subsections", "width2", "heigth2"],
		["path", "opacity"],
		["text", "font"],
		["text", "font"]
		]

		self.defaultFont = self.Variables[1]
		self.timelinesettings = self.Variables[0]
		self.bkimagesettings = self.Variables[1]
		self.textsettings = self.Variables[2]
		self.titlesettings = self.Variables[3]

		self.timelinesettings[1]=defaultFont
		self.textsettings[1]=defaultFont
		self.titlesettings[1]=defaultFont

		self.name=script.replace("/","\\").split("\\")[-1].split(".")[0]
		try:
			os.mkdir("Data\\"+self.name)
		except:
			self.Cleanup()
		print("Iterpreting script!")
		self.Storyborder(script)
		print("Rendering {} Frames!".format(len(self.Frames)))
		self.Render(11)
		print("Done!")
		self.Cleanup()

	def AddFrame(self):
		self.Frames.append(Frame(Image.new("RGB",self.size), TimeLine(*self.timelineargs),0,0,BkImage(*self.bkimageargs)))

	def getCommand(self,line, i, Commands):

		for cmd in Commands:
			if line.strip().startswith(cmd):
				for arg in line.split(",")[1:]:
					if "\"" in arg:
						cmd.args.append(arg.split("\"")[1])
					else:
						try:
							cmd.args.append(float(arg))
						except:
							print(f"Error at Line {i}:\n{line};\nCannot convert '{arg}' to float!")
							exit()
				
				return cmd
		print(f"Error at Line {i}:\n{line};\nUnrecognized command!")
		exit()

	def Preprocessor(self, Script):
		Commands = [
		Command(Functions.setframesize,"size")
		]

		for i,line in enumerate(Script):
			if line.startswith("#"):
				cmd = getCommand(line[1:], i,Commands)
				if cmd.func(self,*cmd.args)!=1:
					print(f"Error at Line {i}:\n{line};\n Function failed!")


	def Interpreter(self, Scriptfile):
		Commands = [
		Command(Functions.goto,"goto"), 
		Command(Functions.wait,"wait")
		]

		Script = open(Scriptfile).read().split(";")
		Preprocessor(Scriptfile)
		self.img = Image.new("RGB",self.size,0)

		for i,line in enumerate(Script):
			if not (line.startswith("//") or line.startswith("#")):
					self.checkCommand(line, i)

	def Cleanup(self):
		rmtree("Data\\"+self.name)

	def ThreadDraw(self, beg, end):
		print(beg,end)
		for i,Frame in enumerate(self.Frames[beg:end]):
			Frame.Draw()
			Frame.save("Data\\"+self.name+"\\Frame"+str(i+beg)+".png")

	def Render(self, Threads):
		picperthread=int(len(self.Frames)/Threads)
		threadarr=[]
		for i in range(0,Threads):
			threadarr.append(Thread(target=self.ThreadDraw,args=(picperthread*i,picperthread*(i+1),)))
			threadarr[i].start()
		for i in threadarr:
			i.join()
		os.system("Data\\ffmpeg -r {} -f image2 -i Data\\{}\\Frame%d.png -i Data\\musik.mp3 -acodec copy -vcodec mpeg4 -b 10M -shortest {}.mp4 -y".format(self.fps, self.name,self.name))

			
