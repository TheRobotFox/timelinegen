from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import numpy as np
import wave
import copy
import math

class VideoObject:
	def __init__(self):
		self.vars = {
		"layer"		: 	  0,
		"alpha"		: 	1.0,
		}
		self.audio_buff = []
	def setVar(self, arg, val):
		if arg in self.vars:
			if type(self.vars[arg])==type(val):
				self.vars[arg]=val
				return (0)
			else:
				return (1,f"Got {type(val)} expected {type(self.vars[arg])}")
		else:
			return (1,"Unknown variable")

	def Draw(self, frame):
		pass

	def getVar(self, arg):
		if arg in self.vars:
			return (0,self.vars[arg])
		else:
			return (1,"Unknown variable")

	def Render(self, img):
		pass

class Font(VideoObject):
	def __init__(self, name="twcen.TTF", size=102, color=(255,255,255)):
		VideoObject.__init__(self)
		self.vars["name"] = name
		self.vars["size"] = np.float64(size)
		self.vars["color"] = color

	def getfont(self):
		return ImageFont.truetype(self.vars["name"],int(self.vars["size"]))

	def getidentifier():
		return "Font"

fonts  = [Font("twcen.TTF")]

class Text(VideoObject):
	def __init__(self, text, x=0, y=0, font=0):
		VideoObject.__init__(self)
		self.vars["text"] = text
		if not font:
			font=fonts[0]
		self.vars["font"] = font
		self.vars["x"] = x
		self.vars["y"] = y

	def Draw(self, frame):
		d = ImageDraw.Draw(frame.img)
		textsize=d.textbbox((0,0), self.vars["text"],self.vars["font"].getfont())[2:]
		pos = (int(frame.img.size[0]/2+self.vars["x"]-textsize[0]/2),int(frame.img.size[1]/2-self.vars["y"]-textsize[1]/2))
		d.text(pos,str(self.vars["text"]),(int(self.vars["font"].vars["color"][0]),int(self.vars["font"].vars["color"][1]),int(self.vars["font"].vars["color"][2])),self.vars["font"].getfont())

	def getidentifier():
		return "Text"

class TimeLine(VideoObject):
	class Date:
		def __init__(self, year, font):
			self.year = year
			self.font = font

	def __init__(self, year, y_offset=.05, font=0, linewidth=25, sections=2, subsections=11, linecolor=(255,255,255), secwidth=22, secheigth=45, subwidth=12, subheigth=30):
		VideoObject.__init__(self)
		self.vars["year"] = np.float64(year)
		self.vars["linewidth"] = linewidth
		self.vars["sections"] = np.float64(sections)
		self.vars["Y"] = y_offset
		self.vars["subsections"] = int(subsections)
		self.vars["linecolor"] = linecolor
		self.vars["secwidth"] = secwidth
		self.vars["secheigth"] = secheigth
		self.vars["subwidth"] = subwidth
		self.vars["subheigth"] = subheigth
		self.ticktime=0
		self.tickbuff = wave.open("data/tick.wav","rb").readframes(-1)
		self.audio_time=0
		if not font:
			font=fonts[0]
		self.vars["font"] = font
		self.vars["SpecialDates"] = []

	def getfrac(self, num):
		return num-int(num)

	def Print(self, img, X, year):
		year=int(year)
		d = ImageDraw.Draw(img)
		color=self.vars["font"].vars["color"]
		font=self.vars["font"].getfont()
		for e in self.vars["SpecialDates"]:
			if e.year==year:
				color=e.font.vars["color"]
				font=e.font.getfont()
				break
		_,_,w,h = d.textbbox((0,0), str(year),font)
		d.text((X-w/2,self.Y-self.vars["secheigth"]-h),str(year),(int(color[0]),int(color[1]),int(color[2])),font)
	

	def Draw(self, frame):
		d = ImageDraw.Draw(frame.img)
		self.Y=frame.img.size[1]/2*(1+self.vars["Y"])
		pos=(0,self.Y,frame.img.size[0],self.Y)
		d.line(pos,self.vars["linecolor"],self.vars["linewidth"])

		center=frame.img.size[0]/2
		div=frame.img.size[0]/(self.vars["sections"]+1)
		sectionhalf=int(np.round(self.vars["sections"]/2))

		for i in range(-sectionhalf-3,sectionhalf+3):
			X=int(center+div*i-self.getfrac(self.vars["year"])*div)
			d.line((X,int(self.Y-self.vars["secheigth"]),X,int(self.Y+self.vars["secheigth"])),self.vars["linecolor"],int(self.vars["secwidth"]))
			self.Print(frame.img, X, self.vars["year"]+i)

			for sub in range(self.vars["subsections"]):
				subpos=X+div/(self.vars["subsections"]+1)*(sub+1)
				d.line((subpos,self.Y+self.vars["subheigth"],subpos,self.Y-self.vars["subheigth"]),self.vars["linecolor"],int(self.vars["subwidth"]))
	
	def getidentifier():
		return "TimeLine"

	def AddSpecialDate(self, year, color):
		self.vars["SpecialDates"].append(TimeLine.Date(year, color))

	def RemoveSpecialDate(self, year):
		for i in range(len(self.vars["SpecialDates"])):
			if self.vars["SpecialDates"][i].year==year:
				self.vars["SpecialDates"].remove(self.vars["SpecialDates"][i])

class TuringMaschine(VideoObject):
	def __init__(self, tape="", pos=0, x=0, y=0, font=0, cells=8, linecolor=(255,255,255)):
		VideoObject.__init__(self)
		self.vars["tape"] = dict(enumerate(tape))
		self.vars["position"] = np.float64(pos)

		if not font:
			font=fonts[0]
		self.vars["font"] = font
		self.vars["x"] = x
		self.vars["y"] = y
		self.vars["cells"] = cells
		self.vars["linecolor"] = linecolor
		self.vars["marks"] = {}

	def getidentifier():
		return "TuringMaschine"
	def getFont(self, d, goal):
		font = copy.deepcopy(self.vars["font"])
		c='[]'
		jumpsize = 75

		fontsize = 75
		while True:
			bbox = d.textbbox((0,0), c, font=font.getfont())[2:]
			if bbox[1] <= goal:
				fontsize += jumpsize
			else:
				jumpsize = jumpsize // 2
				fontsize -= jumpsize
			font.setVar("size", np.float64(fontsize))
			if jumpsize <= 1:
				break
		return font
	def setTape(self, c):
		pos = int(self.vars['position'])
		if not len(c):
			if pos in self.vars["tape"]:
				del self.vars['tape'][pos]
		else:
			self.vars['tape'][pos] = c
	def addMark(self, p, c):
		self.vars["marks"][p] = c
	def rmMark(self, p):
		del self.vars["marks"][p]

	def Draw(self, frame):
		d = ImageDraw.Draw(frame.img)

		y=frame.img.size[1]/2*(1+self.vars["y"])

		squareS = frame.img.size[0]/self.vars["cells"]
		font = self.getFont(d, squareS).getfont()

		start=frame.img.size[0]/2 - squareS*(self.vars['cells']/2+0.5+(self.vars['position'])%1)
		s = math.floor(self.vars['position']-(self.vars['cells']/2))

		def DrawCell(i):
			d.rectangle((squareS*i+start, y-squareS/2,squareS*(i+1)+start,y+squareS/2), outline=self.vars['linecolor'], width=lw)
			p = s+i
			txt = self.vars['tape']
			if p in txt:
				c = txt[p]
			else:
				c = '[]'
			_,_,w,h = d.textbbox((0,0), c, font)
			if p in self.vars["marks"]:
				color = tuple(int(c) for c in self.vars["marks"][p])
			else:
				color = (255,255,255)
			d.text((start+squareS*(i+0.5)-w/2, y-h*6/10), c, font=font, fill=color)

		lw = frame.img.size[0]//500
		for i in range(-1, self.vars['cells']+2):
			DrawCell(i)

		d.rectangle((frame.img.size[0]/2-squareS/2, y-squareS/2, frame.img.size[0]/2+squareS/2,y+squareS/2), outline=self.vars['linecolor'], width=lw*4)
