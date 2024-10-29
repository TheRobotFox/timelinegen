import numpy as np
import random
import wave

from numpy.random import randint

samplerate=48000

def beziere(start, end, t, slope):
	return start+(end-start)*((np.arctan((t-0.5)/slope*360*0.4)/np.arctan(180/slope*0.4))/2+0.5)

class Actor:
	def __init__(self, VideoObject, time_start, duration):
		self.VideoObject = VideoObject
		self.time_start = time_start
		self.duration = duration

	def work(self,currenttime):
		if currenttime >= self.time_start and currenttime <= self.time_start+self.duration:
			return self.act(currenttime-self.time_start)
		return 0

	def act(self,currenttime):
		#Overwrite
		pass

	def gettime(self):
		#Overwrite
		return self.duration

	def getidentifier():
		#Overwrite
		pass

class Actor_bez(Actor):
	def __init__(self, VideoObject, start, arg, destination, time=3, slope=8):
		Actor.__init__(self, VideoObject, start, time)
		self.arg = arg
		self.start=VideoObject.getVar(arg)[1]
		self.destination=destination
		self.time=time
		self.slope=slope

	def getidentifier():
		return "bez"

	def act(self,currenttime):
		time=currenttime/self.time
		res=0
		if type(self.destination)==tuple or type(self.destination)==list :
			val=[]
			for i in range(len(self.destination)):
				val.append(beziere(self.start[i],self.destination[i],time,self.slope))
			res=self.VideoObject.setVar(self.arg,tuple(val))
		elif type(self.destination)==str:
			string=""
			length = beziere(len(self.start),len(self.destination),time,self.slope*2)
			def getChar(start, dest, time, i, cl):
				brightness=" `.-':_,=;><+!rc*/z?sLfI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"
				def getBrightness(text, i):
					if i>=len(text):
						return 0

					cs = brightness.find(text[i])
					if cs<0:
						cs=random.randint(10, len(brightness)-1)
					return cs

				sl = len(start)
				dl = len(dest)
				if time>=1:
					if i<dl:
						return dest[i]
					else:
						return ""

				cs = getBrightness(start, i)
				cd = getBrightness(dest, i)

				df = round(beziere(cs,cd,time, self.slope))
				if i<sl:
					if start[i]=='\n':
						return '\n'
				if i<dl:
					if dest[i]=='\n':
						return '\n'
				return brightness[df]


			for i in range(int(length)):

				t = time + (beziere(0, 1, 1-(i+1)/length, self.slope)  if len(self.start)<len(self.destination) else beziere(0, time, (i+1)/length, self.slope))
				string+=getChar(self.start, self.destination, t, i, length)
			res=self.VideoObject.setVar(self.arg,string)
		else:
			res=self.VideoObject.setVar(self.arg,beziere(self.start,self.destination,time,self.slope))
		return res

class Actor_goto(Actor_bez):
	def __init__(self, VideoObject,start, destination, time=3, slope=8):
		Actor_bez.__init__(self, VideoObject, start, "year", destination, time, slope)
		self.lastyear=self.start

	def act(self,currenttime):
		tickspeed=12000000
		year=beziere(self.start,self.destination,currenttime/self.time,self.slope)
		length=int(((self.time_start+currenttime)-self.VideoObject.audio_time)*samplerate)
		yeardifference=year-self.lastyear
		ticks = np.sqrt(np.abs(yeardifference*tickspeed))
		if yeardifference<0:
			ticks*=-1



		for i in range(length):
			index=(int(self.VideoObject.ticktime+ticks*(i/length))*4)%len(self.VideoObject.tickbuff)
			#index=(int(beziere(self.VideoObject.ticktime,yeardifference*tickspeed,i/length,0.2))*4)%len(self.VideoObject.tickbuff)
			self.VideoObject.audio_buff.append(self.VideoObject.tickbuff[index])
			self.VideoObject.audio_buff.append(self.VideoObject.tickbuff[index+1])
			self.VideoObject.audio_buff.append(self.VideoObject.tickbuff[index+2])
			self.VideoObject.audio_buff.append(self.VideoObject.tickbuff[index+3])

		res=self.VideoObject.setVar(self.arg,year)
		self.VideoObject.audio_time=self.time_start+currenttime
		self.lastyear=year
		self.VideoObject.ticktime+=ticks
		return res

	def getidentifier():
		return "goto"

class Actor_setVar(Actor):
	def __init__(self,VideoObject,start,arg,val):
		Actor.__init__(self,VideoObject,start,0)
		self.arg=arg
		self.val=val
	def getidentifier():
		return "setVar"

	def act(self,currenttime):
		return self.VideoObject.setVar(self.arg,self.val)

class AddSpecialDate(Actor):
	def __init__(self,VideoObject,start,year,font):
		Actor.__init__(self,VideoObject,start,0)
		self.year = year
		self.font = font

	def act(self,currenttime):
		self.VideoObject.AddSpecialDate(self.year,self.font)

	def getidentifier():
		return "addSpecialDate"

class RemoveSpecialDate(Actor):
	def __init__(self,VideoObject,start,year):
		Actor.__init__(self,VideoObject,start,0)
		self.year = year

	def act(self,currenttime):
		self.VideoObject.RemoveSpecialDate(self.year)

	def getidentifier():
		return "removeSpecialDate"

class Wait(Actor):
	def __init__(self,VideoObject,start,sek):
		Actor.__init__(self,VideoObject,start,sek)

	def getidentifier():
		return "wait"

class SetTape(Actor):
	def __init__(self,VideoObject,start,c):
		Actor.__init__(self,VideoObject,start,0)
		self.c = c

	def act(self,currenttime):
		self.VideoObject.setTape(self.c)

	def getidentifier():
		return "setTape"

class addMark(Actor):
	def __init__(self,VideoObject,start, p, c=None):
		Actor.__init__(self,VideoObject,start,0)
		if c==None:
			self.c = p
			self.p = None
		else:
			self.p = p
			self.c = c

	def act(self,currenttime):
		if self.p==None:
			self.p = round(self.VideoObject.getVar("position")[1])
		self.VideoObject.addMark(self.p, self.c)

	def getidentifier():
		return "addMark"
class rmMark(Actor):
	def __init__(self,VideoObject,start, p):
		Actor.__init__(self,VideoObject,start,0)
		self.p = p

	def act(self,currenttime):
		self.VideoObject.rmMark(self.p)

	def getidentifier():
		return "rmMark"
