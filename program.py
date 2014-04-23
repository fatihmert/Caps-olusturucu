#-*- coding: utf-8 -*-

# Release: 	Fatih Mert DOĞANCAN
# Date:		21.04.2014
# Mail:		fatihmertdogancan@hotmail.com

# Şablon sistemini, 2. versiyona düşünüyorum.
# OOP

import Tkinter as tk #içerisinde Image modülü olduğu için PIL ile çakışıyor, bu yüzden as tk
from PIL import Image, ImageDraw, ImageFont
import tkFileDialog as TkFD
from os import name as osName
from os import path as osPath
from random import randint
#import BmpImagePlugin #!TEHLİKE BURADA!
try:
	import cStringIO as StringIO #Bu daha hızlıdır
except ImportError: #cStringIO'nun olmama gibi bir durumu yok ama olursa, program biraz kasabilir
	import StringIO
import subprocess as sp
import ctypes
import re
from datetime import timedelta
import math #ceil kullanırkende nedenini bulamadığım bir çakışma var., bu yüzden tüm math :(

#SABITLER
FFMPEG_BIN = "ffmpeg" #linux
if osName == "nt": #windows
	FFMPEG_BIN = "ffmpeg.exe"
del osName
BITMAP_HEAD = 0x4d42
#SABITLER

class capsGen(object):
	def __init__(self):
		#self.getFFMPEG() #geliştirici için kontrol
		self.appHead() #program static bilgileri
		self.windHead() #pencere static bilgileri
		self.windItemOpt() #pencere elemanlarının static ayarları
		self.windUI() #pencere elemanları
	
	#ARACLAR
	def codingFix(self,i):
		#or ifadeleri, utf-8 ve cp1254 fix
		return "%s"%i or u"%s"%i or i
		
	def subprocessToString(self,popen):
		"""
		@param: popen
			subprocess object
		"""
		#subprocess.Popen(komut, stdin=sp.PIPE, stdout=sp.PIPE,  stderr=sp.PIPE), olmak zorunda
		if popen:
			popen.terminate()
			return popen.stderr.read()
	
	def getBase(self,dosyaPath):
		"""
		@param: dosyaPath
			C:\Users\user\Desktop\Caps olusturucu\test.mp4 -> test.mp4
		"""
		return osPath.basename(dosyaPath)
	
	def hex2rgba(self, deger):
		return tuple(int(deger.lstrip('#')[i:i+2], 16) for i in range(0, 6, 2))+(1,)
		
	def size2tuple(self,deger):
		"""
		@param: deger
			100x150 -> (100,150)
		"""
		nesne = re.search("([0-9]+)[x]([0-9]+)",deger)
		return tuple([int(nesne.group(1)),int(nesne.group(2))])
	
	#ARACLAR
	
	def getFFMPEG(self):
		#geliştirici için
		if ffmpeg:
			print 'VERSION:', get_ffmpeg_version()
			print 'INFO:', get_ffmpeg_info()
			print 'CODECS:', get_codecs()
			print 'FORMATS:', get_formats()
			print 'PIXEL_FORMATS:', get_pixel_formats()
			#print 'info of video:', get_info('test.mp4')
		else:
			print "!"
	
	
	def setCmdFFPMEG(self,path):
		"""
		@param: argv
			list
		"""
		komut = [FFMPEG_BIN,'-i',path,'-t','duration']
		if sp:
			pipe = sp.Popen(komut, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
			pipe.stdout.readline() #çıktıyı oku, eğer okumazsa return nesne boş döner
			return pipe
			
	
	def getDuration(self,path):
		return re.findall("Duration: (([0-9]+):([0-9]+):([0-9]+))",self.subprocessToString(self.setCmdFFPMEG(path)))
			
	def getEncoder(self,path):
		return re.findall("encoder\\s+: (.*)",self.subprocessToString(self.setCmdFFPMEG(path)))
			
	def getFPS(self,path):
		return re.findall("([0-9]{2})\\s?fps",self.subprocessToString(self.setCmdFFPMEG(path)))
	
	def getFileName(self,path):
		return re.findall("Input\\s?.*?,\\s?from\\s?['](.*)[']:",self.subprocessToString(self.setCmdFFPMEG(path)))
	
	def getCTarih(self,path):
		return re.findall("creation_time\\s+?:\\s?(.*)",self.subprocessToString(self.setCmdFFPMEG(path)))
		
	def getSize(self,path):
		#buff -> return asagidakiIfade[0]'de
		return re.findall("([0-9]+[x][0-9]+)",self.subprocessToString(self.setCmdFFPMEG(path)))
		
	def getBoyut(self,path):
		if osPath.getsize(path) >> 20 == 0:
			return str(osPath.getsize(path) >> 10) + "KB"
		else:
			return str(osPath.getsize(path) >> 20) + "MB"
			
	def getFrame2Sn(self,toplamFrame,fps):
		toplamSn = int(toplamFrame) / fps #fps float olmak zorunda
		sonuc = timedelta(seconds=math.ceil(toplamSn))
		return str(sonuc)
	
	def videoHead(self,dosyaPath):
		#ffmpeg._attempt_ffmpeg()
		self.topSure = self.getDuration(dosyaPath)[0][0]
		self.sureSaat = self.getDuration(dosyaPath)[0][1]
		self.sureDakika = self.getDuration(dosyaPath)[0][2]
		self.sureSaniye = self.getDuration(dosyaPath)[0][3]
		self.encoder = self.getEncoder(dosyaPath)[0]
		self.fps = self.getFPS(dosyaPath)[0] #kullanırken float'a dönüştür
		self.dosyaIsmi = self.getFileName(dosyaPath)[0]
		self.olusturulma = self.getCTarih(dosyaPath)[0][0]
		self.boyut = self.getSize(dosyaPath)[1]
		self.Byte = self.getBoyut(dosyaPath)
		#self.getBuff = self.getSize(dosyaPath)[0]
		self.SabitBoyut = "493x258" #self.size2tuple()
	
	def videoyuIsle(self,path):
		iv = InputVideoStream()
		iv.openFFMPEG(path)
		self.videoHead(path)
		kareleriAyristir = list(enumerate(iv.readframe())) #bmp io -> [caps][1]
		self.toplamKare = kareleriAyristir[-1][0]
		#16 resim
		self.capsResim = []
		resimSimdi = 0
		while True:
			if resimSimdi < 16:
				self.capsResim.append(randint(1,self.toplamKare))
				resimSimdi = resimSimdi + 1 
			else:
				break
		
		
		kaynak = Image.open(self.capsTemplate)
		kaynak.load() #artık "işlenebilir" bir resim oldu
		ciz = ImageDraw.Draw(kaynak)
		ft = ImageFont.truetype("arial.ttf",32)
		ciz.text((190,15),self.dosyaIsmi,font=ft,fill=self.hex2rgba("#FFFFFF")) #dosyaAdi
		ciz.text((190,55),"%spx - %s - %fFPS"%(self.boyut,self.Byte,float(self.fps)),font=ft,fill=self.hex2rgba("#FFFFFF")) #boyut,büyüklük,fps
		ciz.text((190,100),self.topSure,font=ft,fill=self.hex2rgba("#FFFFFF")) #süre
		
		#print "Sıfır sıfır sıfır!: " + str(self.hex2rgba("#000000"))
		
		# YAPI
		
		#sabit değerler enumerate olacak! yada self.capsResim den for'a sokulur
		#sabitDegerler["Sablon01"][1(enum)][x]
		sabitDegerler = { #photoshoptan cetvellerle hesaplandı
			"Sablon01":{
				1:{
					"x":15, #margin x
					"y":165 #margin y
				},2:{"x":523,"y":165},3:{"x":1029,"y":165},4:{"x":1534,"y":165}, #satır1
				5:{"x":15,"y":450},6:{"x":523,"y":450},7:{"x":1029,"y":450},8:{"x":1534,"y":450}, #satır2
				9:{"x":15,"y":740},10:{"x":523,"y":740},11:{"x":1029,"y":740},12:{"x":1534,"y":740}, #satır3
				13:{"x":15,"y":1023},14:{"x":523,"y":1023},15:{"x":1029,"y":1023},16:{"x":1534,"y":1023} #satır34
			}
		}
		
		# YAPI
		
		#print kareleriAyristir[5][0]
		for no, i in enumerate(self.capsResim):
			no = no + 1
			yeniResim = Image.open(StringIO.StringIO(kareleriAyristir[i][1]))
			yeniDraw = ImageDraw.Draw(yeniResim)
			#sağ alt köşeye geçerli karenin süresini yaz
			yeniDraw.text((yeniResim.size[0]-125,yeniResim.size[1]-40),self.getFrame2Sn(int(i),float(self.fps)),font=ft,fill=self.hex2rgba("#FFFFFF"))
			#süreler yazılıyor mu kontrol amaçlı kaydet, geliştirici için
			#yeniResim.save("%s.jpg"%i)
			if yeniResim.mode !=  kaynak.mode:
				yeniResim.convert('RGB')
				kaynak.convert('RGB')
			yeniResim.resize((493,278))
			kaynak.paste(yeniResim,(sabitDegerler["Sablon01"][no]["x"],sabitDegerler["Sablon01"][no]["y"]))
			#kaynak.paste
			#resim["frame"] = int(i)
			#resim["saat"] = self.getFrame2Sn(int(i),float(self.fps))
			#resim["io"] = StringIO.StringIO(kareleriAyristir[i][1])
			#print "%s :: Margin X:%s  ::  Margin Y:%s"%(self.getFrame2Sn(self.toplamKare,self.fps),sabitDegerler["Sablon01"][no+1]["x"],sabitDegerler["Sablon01"][no+1]["y"])
			#print self.getFrame2Sn(int(i),float(self.fps))
		#	resim = Image.open(StringIO.StringIO(kareleriAyristir[i][1])) #base io -> [capsNo][1]
		#	resim.save("%s.png"%i)
		
		kaynak.save("caps.png")

		#print "Bu video: " + self.sureSaat + " saat " + self.sureDakika + " dakika " + self.sureSaniye + " saniyedir"
	
	def appHead(self): #static bilgiler nHead
		#Genel ifadeler
		self._, self.__ = (" ","-")
		#Program bilgileri, belki başka yerlerde kullanıabilir bu yüzden "self"
		self.appAdi = self.codingFix("Caps Oluşturucu")
		self.appVer = self.codingFix("0.1")
		self.appDev = self.codingFix("Fatih Mert DOĞANCAN")
		
		self.appTamAd = self.appAdi + self._ + self.appVer + self._ + self.__ + self._ + self.appDev
		self.appTamAd = self.codingFix(self.appTamAd) #tekrar
		
		#Varsayılan Şablon
		self.capsTemplate = "kaynak.jpg"
		
		#print ""
		
	
	def windHead(self):
		self.pencere = tk.Tk()
		self.pencere.title(self.appTamAd)
		self.pencere.geometry("500x250+0+0") #sol üst köşede başlat
		self.pencere.resizable(width=tk.FALSE, height=tk.FALSE) #genişlik ve yükseklik değiştirilemez
	
	def windUp(self): #güncelleme
		self.pencere.update_idletasks()
		
	def windItem(self): #nesneler
		pass
	
	def windItemOpt(self): #nesne ayarları
		self.capsVideoFopt = ayars = {}
		ayars["filetypes"] = [(self.codingFix("Tüm dosyalar"),".*"),(self.codingFix("Windows Media Video File"),".wmv"),(self.codingFix("Real Media File"),".rm"),(self.codingFix("	MPEG-4 Video File"),".mp4"),(self.codingFix("MPEG Video File"),".mpg"),(self.codingFix("Audio Video Interleave File"),".avi"),(self.codingFix("Apple QuickTime Movie"),".mov"),(self.codingFix("WebM Video File"),".webm"),(self.codingFix("Flash Video File"),".flv"),(self.codingFix("MPEG Movie"),".mpeg"),(self.codingFix("Matroska Video File"),".mkv")] #(self.codingFix(""),".") desteklenen türler, ffmpeg modülüne göre, eklenecek
		ayars["title"] = self.codingFix("Caps oluşturmak istediğiniz video dosyasını seçin")
		#ayars["mode"] = 'r' #read, askopenfilename de hata verir, çünkü askopenfilename sadece dosya adını döndürür
		#self.bolderOpt = {}
		#self.bolderOpt["weight"] = 'bold'
		#self.bolderOpt['underline'] = False
	
	def windUI(self):
		capsVideoSec = tk.Button(text=self.codingFix("Gözat.."), command=self.getDosyaAdi).pack()
		capsVideoLabel_ = tk.Label(text=self.codingFix("Aşağıdaki yolda seçmiş olduğunuz dosyanın Caps'i oluşturulmuştur")).pack()
		#capsVideoLabel_.config(text=self.getDosyaAdi)
		self.bosStringVar = tk.StringVar()
		self.bosStringVar.set(" ")
		capsVideoLabel = tk.Label(textvariable=self.bosStringVar).pack()
		

	
	def getDosyaAdi(self):
		self.dosyaAdi = TkFD.askopenfilename(**self.capsVideoFopt)
		self.bosStringVar.set(self.dosyaAdi)
		self.videoyuIsle(self.getBase(self.bosStringVar.get()))
		self.windUp()
		#return 

def sread(fd,cobj):
	ctypes.memmove(ctypes.pointer(cobj),ctypes.c_char_p(fd.read(ctypes.sizeof(cobj))),ctypes.sizeof(cobj))

class InputVideoStream:
    def __init__(self, path=None):
        self.rate = 15
        self.ivcodec = 'bmp'
        self.frames = 10
        self.iformat = 'image2pipe'
		
    def openFFMPEG(self, path):
        self.filepath = path
        cmd = [FFMPEG_BIN,'-i', self.filepath,'-f', self.iformat,'-vcodec', self.ivcodec,'-']
        self.p = sp.Popen(cmd,stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.PIPE) #,
		
    def readframe(self):
    	"""her kareyi bmp turunde "iterator" nesnesi yapar"""
    	while True:
            bmfheader = BitmapFileHeader()
            sread(self.p.stdout, bmfheader)
            if bmfheader.bfType != BITMAP_HEAD: # son kareden sonra "while True" ifadesini parçalaa
                break
            # stringe donustur
            bmp = ctypes.string_at(ctypes.pointer(bmfheader), ctypes.sizeof(bmfheader))
            # BitmapFileHeader ve rest data
            bmp += self.p.stdout.read(bmfheader.bfSize - ctypes.sizeof(bmfheader))
            yield bmp #koy iterator'üü

        self.p.stdin.close()
        #del self.p
		
class BitmapFileHeader(ctypes.LittleEndianStructure):
    _pack_ = 2
    _fields_ = [
        ('bfType', ctypes.c_int16),
        ('bfSize', ctypes.c_int32),
        ('bfRsv1', ctypes.c_int16),
        ('bfRsv2', ctypes.c_int16),
        ('bfOffBits', ctypes.c_int32),
    ]



calistir = capsGen()

tk.mainloop()
