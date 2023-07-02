# -*- coding: utf-8 -*-

from psychopy import core, visual, prefs, event
import random, sys
from stimPresPsychoPy_python3 import *
#from useful_functions_python3 import *
#I added these base functions to get get runTimeVars to work
from baseDefsPsychoPy import *
from generateTrials import *
import webbrowser as web
import socket
import numpy as np
from distutils.util import strtobool
import psychopy.hardware.keyboard
from baseDefsPsychoPy import *
from stimPresPsychoPy import *
import constants

from psychopy import logging
logging.console.setLevel(logging.CRITICAL)

print (prefs.general)


class Exp:
	def __init__(self):
		expName='visSearch_blocked'
		self.subjInfo = {}

		while True:
			runTimeVarsOrder = ['subjCode','instructions', 'lang', 'showTargetImage', 'showTargetText', 'seed','gender','blockOrder']
			self.runTimeVars = getRunTimeVars({'subjCode':'vsb_101', 'instructions':['image','text'], 'seed':10, 'lang': ['e'], 'showTargetImage':['True','False'],'showTargetText':['True','False'], 'gender':['Choose', 'male','female'], 'blockOrder': ['Choose', 'RL', 'LR']},runTimeVarsOrder,expName)
			if 'Choose' in self.runTimeVars.values():
				popupError('Need to choose a value from a dropdown box')
			else:
				self.outputFile = open('data/' + self.runTimeVars['subjCode'] + '.tsv', 'w')
				if self.outputFile:
					break

		self.runTimeVars['room'] = socket.gethostname().upper()
		#self.runTimeVars['room'] = 'LiadLab'

		generateTrials(self.runTimeVars,runTimeVarsOrder)
	# 	commented this out 6/29/23
		(self.header,self.trialInfo) = importTrials('trials/'+self.runTimeVars['subjCode']+'_trials.tsv')
		self.trialInfo = list(self.trialInfo)

		#open the main window
		self.win = visual.Window(fullscr=True,allowGUI=False, color=[0,0,0], units='pix')
		#self.win = visual.Window([1280,800],allowGUI=True, color=[0,0,0], units='pix')


		self.pics =  loadFiles('stimuli/visual','.png','image', win=self.win)
		self.sounds =  loadFiles('stimuli/sounds','.wav','sound', win=self.win)
		self.postSoundDelayCorrect = .3
		self.postSoundDelayIncorrect = .75
		self.fixationWait = .5
		self.takeBreakEveryXTrials = 100
		self.numPracticeTrials = 5
		self.radius = 200
		angles = list(np.array(range(15,360,30))-90)
		self.locations = polarToRect(angles,self.radius)
		self.validResponses = {'up':'present','down':'absent'}
		
		self.instructionsText = {
				'e': "Thank you for participating!  In this experiment, your job is to search for a target image which you will see on the next screen. On each trial, you will see a display with some letters or letter-like characters. Sometimes the target will be among them. Other times not. If you spot the target, press the 'up' key. If not, press the 'down' key. You should respond as quickly and accurately as you can. If you make a mistake, you will hear a buzzing sound. \n\n The experimenter will go over these instructions with you and then you can begin.",
			#	'h': u".אבה ךסמב עיפותש הרטמה תוא תא שפחל איה םכתרטמ"+"\n"+u".תויתוא-ייומד וא תויתוא המכ םע ךסמ וארת בלש לכב"+"\n"+u".אל םימעפלו ןהיניב היהת הרטמה תוא םימעפל"+"\n"+u".'הלעמל' וצחל הרטמה תא םיאור םתא םא"+"\n"+u".'הטמל' וצחל אל םא"+"\n"+u".םכתלוכי לככ קיודמו רהמ ביגהל םכילע"+"\n"+u".שער ועמשת םתא תועט םתישע םא"+"\n\n"+u".ךישמהל ולכות זאו םכתא וללה תוארוהה לע רובעי ןייסנה"
				}
		self.practiceTrials = {
				'e': "We will begin with some practice trials. Press enter to continue.",
			#	'h': u".ןומיא יבלש המכ םע ליחתנ"+"\n"+u"וצחל אנ"+"\n"+"ENTER"+"\n"+u".ךישמהל ידכ"
				}
		self.realTrials = {
				'e': "Now we will begin the real experiment. Please let the experimenter know if you have any questions or press enter to continue.",
			#	'h': u".יתימאה יוסינה ליחתי וישכע"+"\n"+u"וצחל וא תופסונ תולאש םכל שי םא ןייסנל ועידוה אנא"+"\n"+"ENTER"+"\n"+u".ךישמהל ידכ" 
				}

		self.takeBreak = {
				'e': "Please take a short break.  Press enter when you are ready to continue.",
			#	'h': u".הרצק הקספה וחק אנא"+"\n"+u"וצחל ךישמהל םינכומ םתאשכ"+"\n"+"ENTER."
				}
		self.thanksText = {
				'e': "Thank you for participating! Please press enter to begin a short questionnaire.",
			#	'h': u"!םכתופתתשה לע הבר הדות"+"\n"+u"וצחל אנא"+"\n"+"ENTER"+"\n"+u".רצק ןולאש ליחתהל ידכב"
				}
		self.surveyURL = {
				'e' : "https://docs.google.com/forms/d/e/1FAIpQLScotg-r5Gd67RZHURBC8cYeCohkbWGxfzHsbqL9C4aTYrnylg/viewform",
			#	'h':  u"https://docs.google.com/forms/d/e/1FAIpQLScotg-r5Gd67RZHURBC8cYeCohkbWGxfzHsbqL9C4aTYrnylg/viewform"
				}
		self.surveyURL[self.runTimeVars['lang']] += '?entry.900342216=%s&entry.142747125=%s' % (self.runTimeVars['subjCode'], self.runTimeVars['room'])

	# def displayText(self,text,keyList=["enter","return"],pos=(0,0),show=True):
	# 	visual.TextBox(window=self.win,\
 #        	text=text,
 #        	font_name='Courier New',
 #        	font_color=[-1,-1,-1],
 #        	font_size=22,
 #            size=(800,600),
 #            pos=pos,
 #            grid_stroke_width=0,
 #            grid_horz_justification='center',
 #            grid_vert_justification='center',
 #            units='pix').draw()
	# 	if show:
	# 		self.win.flip()
	# 		event.waitKeys(keyList=keyList)

	def displayText(self,text,keyList=["enter","return"],pos=(0,0),show=True):
		visual.TextStim(self.win,\
        	text=text,
            pos=pos,
            units='pix').draw()
		if show:
			self.win.flip()
			print ('waiting for', keyList)
			event.waitKeys(keyList=keyList)



	def displayImage(self,image,keyList=["enter","return"],pos=(0,0),show=True):
		image.draw()
		if show:
			self.win.flip()
			event.waitKeys(keyList=keyList)


	def drawFixation(self):
		visual.TextStim(win=self.win,text='+',color="black",height=40).draw()

	def showTarget(self,targetPic,targetName,lang,showTargetImage,showTargetText):
		(showTargetImage,showTargetText) = (strtobool(showTargetImage), strtobool(showTargetText))
		if showTargetImage:
			self.pics[targetPic]['stim'].setPos([0,0])
			self.pics[targetPic]['stim'].draw()
		if lang=="e":
			if showTargetImage:
				self.displayText(text="Please search for the character below:", pos=[0,350],show=False)
			if showTargetText:
				self.displayText(text="Please search for " + targetName, pos=[0,150],show=False)
			if not showTargetImage and not showTargetText:
				self.displayText(text="If all the pictures are the same, press the down arrow. If one is different, press the up arrow." + targetName, pos=[0,200],show=False)
			else:
				self.displayText(text="If the target is present, press the up arrow. If not, press the down arrow.", pos=[0,-200],show=False)
			self.displayText(text="Press Enter when ready", pos=[0,-350],show=False)
		elif lang=="h":
			if showTargetImage:
				self.displayText(text=u":הטמלש תואה תא ושפח אנא", pos=[0,350],show=False)
			if showTargetText:
				self.displayText(text=u"תא ושפח אנא"+"\n" + targetName, pos=[0,150],show=False)
			if not showTargetImage and not showTargetText:
				self.displayText(text=u",תוהז תויתואה לכ םא"+"\n"+u"הטמל וצחל"+"\n"+u",הנוש תחא םא"+"\n"+u".הלעמל וצחל"+"\n", pos=[0,200],show=False)
			else:
				self.displayText(text=u",תאצמנ הרטמה םא"+"\n"+u"הלעמל וצחל"+"\n"+u",אל םא"+"\n"+u".הטמ וצחל", pos=[0,-200],show=False)
			self.displayText(text=u"וצחל"+"\n"+"ENTER"+"\n"+u".םינכומ םתאשכ", pos=[0,-350],show=False)

		self.win.flip()
		event.waitKeys()
		
	def showSearchTrial(self,curTrial,part,curTrialIndex):
		self.win.flip()
		core.wait(.100)
		self.drawFixation()
		self.win.flip()
		core.wait(self.fixationWait)
		
		self.drawFixation()
		if curTrial['isPresent']=="present":
			self.pics[curTrial['targetPic']]['stim'].setPos(self.locations[int(curTrial['targetLocation'])])
			self.pics[curTrial['targetPic']]['stim'].draw()
		
		for curDistractorLocation in curTrial['distractorLocations']:
			self.pics[curTrial['distractorPic']]['stim'].setPos(self.locations[int(curDistractorLocation)])
			self.pics[curTrial['distractorPic']]['stim'].draw()
			
		self.win.flip()
		(response,rt) = getKeyboardResponse(self.validResponses.keys())
		self.win.flip()
		
		isRight = int(self.validResponses[response]==curTrial['isPresent'])
		
		#if isRight:
		#	self.sounds['bleep']['stim'].play()
		#	core.wait(self.postSoundDelayCorrect)
		if not isRight:
			self.sounds['buzz']['stim'].play()
			core.wait(self.postSoundDelayIncorrect)

		curTrial['header']=self.header
		responses=[curTrial[_] for _ in curTrial['header']]
		#write dep variables
		responses.extend(
			[part,
			curTrialIndex,
			response,
			isRight,
			rt])
		writeToFile(self.outputFile,responses,writeNewLine=True)


if __name__ == '__main__':
	exp = Exp()
#	printHeader(exp.header+['response','categoryChosen','exemplarChosen', 'isRight', 'rt'])
	

	if exp.runTimeVars['instructions']=='text' or exp.runTimeVars['lang']=='e':
		exp.displayText(exp.instructionsText[exp.runTimeVars['lang']],['z'])
	else:
		exp.displayImage(exp.pics['instructions']['stim'],['z'])
	
	exp.displayText(exp.practiceTrials[exp.runTimeVars['lang']])
	practiceTrialInfo = random.sample(exp.trialInfo[20:50],exp.numPracticeTrials) #take the practice trials from the first block
	exp.showTarget(practiceTrialInfo[0]['targetPic'],practiceTrialInfo[0]['targetName'],exp.runTimeVars['lang'],exp.runTimeVars['showTargetImage'],exp.runTimeVars['showTargetText'])
	for curTrialIndex,curTrial in enumerate(practiceTrialInfo):
		exp.showSearchTrial(curTrial,"practice",curTrialIndex)

	exp.displayText(exp.realTrials[exp.runTimeVars['lang']])
	for curTrialIndex,curTrial in enumerate(exp.trialInfo):
		if curTrialIndex>0 and curTrialIndex % exp.takeBreakEveryXTrials == 0:
			exp.displayText(exp.takeBreak[exp.runTimeVars['lang']]) #take a break
		try:
			if curTrialIndex==0 or exp.trialInfo[curTrialIndex-1]['targetPic'] != exp.trialInfo[curTrialIndex]['targetPic']:
				exp.showTarget(exp.trialInfo[curTrialIndex]['targetPic'],exp.trialInfo[curTrialIndex]['targetName'],exp.runTimeVars['lang'],exp.runTimeVars['showTargetImage'],exp.runTimeVars['showTargetText'])
		except:
			pass
		exp.showSearchTrial(curTrial,"real",curTrialIndex)
	exp.displayText(exp.thanksText[exp.runTimeVars['lang']])
	web.open(exp.surveyURL[exp.runTimeVars['lang']])





