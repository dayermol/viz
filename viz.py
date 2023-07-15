"""Psychopy 
"""

import random
import time
import sys
import numpy as np
from psychopy import visual, core, event, gui
#from generateTrials import *
#from generateTrials2 import *

def importTrials(fileName, method="random", seed=random.randint(1, 100)):
    (trialList, fieldNames) = data.importConditions(fileName, returnFieldNames=True)
    trials = data.TrialHandler(trialList, 1, method=method,
                               seed=seed)  # seed is ignored for sequential; used for 'random'
    return (trials, fieldNames)


trialList = importTrials('trialList.txt')
for curTrial in trialList:
    curTrial['isMatch'] #contains 1/0 depending on whether the current trial is a match or mismatch

userVar = {'Name':'Enter your name'}
dlg = gui.DlgFromDict(userVar)

names = open('names.txt', 'r').readlines()
firstNames = [name.split(' ')[0] for name in names]

generateTrials(subjCode,seed)


win = visual.Window([800,600],color="black", units='pix')
firstNameStim = visual.TextStim(win,text="", height=40, color="white",pos=[0,0])
while True:
    nameShown = random.choice(firstNames)
    firstNameStim.setText(nameShown)
    firstNameStim.draw()
    win.flip()
    core.wait(.75)
    win.flip()
    core.wait(.15)

    if event.getKeys(['q']):
        break

categories = {'Happy':'H', 'Angry':'A'}
actors = ['BF1', 'BF2', 'BM1', 'BM2', 'WF1', 'WF2', 'WM1', 'WM2']
suffix = '_90_60.jpg'
positions = {'left':(-190,0), 'middle':(0,0), 'right':(190,0)}
responseMapping = {'left':'1','middle':'2','right':'3'}

def randomButNot(l,toExclude,num):
    chosen = random.sample(l,num)
    while toExclude in chosen:
        chosen = random.sample(l,num)
    return chosen

def generateTrials(numTrials):
    trials=[]
    for i in range(numTrials):
        targetCategory = random.choice(categories.keys())
        distractorCategories = randomButNot(categories.keys(),targetCategory,2)
        actorsToShow = np.random.choice(actors,3) 
            #this is the random.choice() function from the numpy library which samples 
            #with replacement. cf. random.sample() samples WITHOUT replacement
        targetLocation = random.choice(positions.keys())
        trials.append({
                    'emotionPrompt':targetCategory,
                    'targetImage':actorsToShow[0]+categories[targetCategory]+suffix,
                    'distractorImage1': actorsToShow[1]+categories[distractorCategories[0]]+suffix,
                    'distractorImage2': actorsToShow[2]+categories[distractorCategories[1]]+suffix,
                    'targetLocation': targetLocation
                    })
    return trials


def getRunTimeVars(varsToGet,order,expVersion):
   #Get run time variables, see http://www.psychopy.org/api/gui.html for explanation
    infoDlg = gui.DlgFromDict(dictionary=varsToGet, title=expVersion, fixed=[expVersion],order=order)
    if infoDlg.OK:
        return varsToGet
    else: 
        print ('User Cancelled')

order =  ['subjCode','seed','gender']
runTimeVars = getRunTimeVars({'subjCode':'test_101', 'seed':10, 'gender':['Choose', 'male','female']}, order, 'ver1')

trials = generateTrials(40)

win = visual.Window([1024,700],color="black", units='pix')
prompt = visual.TextStim(win=win,text='',color="white",height=60)
correctFeedback = visual.TextStim(win=win,text='CORRECT',color="green",height=60)
incorrectFeedback = visual.TextStim(win=win,text='ERROR',color="red",height=60)
pic1 = visual.ImageStim(win=win, mask=None,interpolate=True)
pic2 = visual.ImageStim(win=win, mask=None,interpolate=True)
pic3 = visual.ImageStim(win=win, mask=None,interpolate=True)

for curTrial in trials:
    win.flip()
    core.wait(.25)
    prompt.setText(curTrial['emotionPrompt'])
    prompt.draw()
    win.flip()
    core.wait(.5)

    win.flip()
    core.wait(.1)
    pic1.setImage('faces/'+curTrial['targetImage'])
    pic2.setImage('faces/'+curTrial['distractorImage1'])
    pic3.setImage('faces/'+curTrial['distractorImage2'])
    pic1.setPos(positions[curTrial['targetLocation']])
    distractorPositions = randomButNot(positions.keys(),curTrial['targetLocation'],2)
    pic2.setPos(positions[distractorPositions[0]])
    pic3.setPos(positions[distractorPositions[1]])

    pic1.draw()
    pic2.draw()
    pic3.draw()
    win.flip()
    response = event.waitKeys(keyList=responseMapping.values())[0]
    print(response,responseMapping[curTrial['targetLocation']])
    if response==responseMapping[curTrial['targetLocation']]:
        correctFeedback.draw()
    else:
        incorrectFeedback.draw()
    core.wait(.5)
