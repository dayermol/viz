import glob, os, random, sys
#from useful_functions_python3 import *
import random
from operator import itemgetter
import copy
import pandas as pd
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

def generateTrials(runTimeVars,runTimeVarsOrder):
	if not runTimeVars['subjCode']:
		sys.exit('Please provide a new subject code')
	try:
		random.seed(int(runTimeVars['seed']))
	except:
		sys.exit("Could not set seed. Check that there are no trailing spaces")

	targetInfo = pd.read_csv('trialList_'+runTimeVars['lang']+'.txt',sep="\t")
	numItems=[4,6,12]
	isPresent = ['present','absent']
	numPositions=12
	positionIndices = range(numPositions)
	(leftLocations,rightLocations) = (list(range(int(numPositions/2))), list(range(int(numPositions/2),numPositions)))
	blocksInTrialFile = list(set(list(targetInfo.block.values)))
	blocks = list(runTimeVars['blockOrder'])
	if set(blocks) != set(blocksInTrialFile):
		sys.exit("Blocks do not match. Check trialList.txt")		
	trialInfo={}
	for curBlock in blocks:
		curTrialIndex=0
		trialInfo[curBlock]=[]
		for curTargetName in set(targetInfo[(targetInfo.block == curBlock)]['targetName'].values):
			for curTargetPic in set(targetInfo[(targetInfo.targetName == curTargetName)]['targetPic'].values):
				for curDistractorName in set(targetInfo[(targetInfo.targetName == curTargetName)]['distractorName'].values):
					for curDistractorPic in  set(targetInfo[(targetInfo.distractorName == curDistractorName)]['distractorPic'].values):
						for curIsPres in isPresent:
							for curNumItems in numItems:
								for curTargetLocation in range(numPositions):
									(leftDistractors,rightDistractors) = (copy.copy(leftLocations),copy.copy(rightLocations))
									if curIsPres=="present":
										if curTargetLocation in leftDistractors:
											leftDistractors.remove(curTargetLocation)
											leftDistractors =  random.sample(leftDistractors,int((curNumItems-1)/2))
											rightDistractors = random.sample(rightDistractors,int(curNumItems/2))
										else:
											rightDistractors.remove(curTargetLocation)
											leftDistractors =  random.sample(leftDistractors,int(curNumItems/2))
											rightDistractors = random.sample(rightDistractors,int((curNumItems-1)/2))
									else:
										curTargetLocation="NA"
										leftDistractors =  random.sample(leftDistractors,int(curNumItems/2))
										rightDistractors = random.sample(rightDistractors,int(curNumItems/2))
										
									distractorLocations = leftDistractors + rightDistractors

									trialInfo[curBlock].append([])
									for curRuntimeVar in runTimeVarsOrder:
										trialInfo[curBlock][curTrialIndex].append(runTimeVars[curRuntimeVar])
						
									trialInfo[curBlock][curTrialIndex].extend([curBlock, curTargetName, curTargetPic, curDistractorName, curDistractorPic, curTargetLocation, curIsPres, curNumItems, distractorLocations])
									curTrialIndex+=1

	
	outputFile = open('trials/'+runTimeVars['subjCode']+'_trials.txt','w')
	header = runTimeVarsOrder
	header.extend (['block', 'targetName', 'targetPic', 'distractorName', 'distractorPic', 'targetLocation', 'isPresent', 'numItems', 'distractorLocations'])
	writeToFile(outputFile,header)
	for curBlock in blocks:
		trialBlock = trialInfo[curBlock]
		random.shuffle(trialBlock)
		for curTrial in trialBlock:
			writeToFile(outputFile,curTrial)
	outputFile.close()
	outputFile.close()
	return True

if __name__ == '__main__':
	generateTrials({'subjCode':'testSubj1', 'seed':'20', 'lang':'e','blockOrder':'LR'}, ['subjCode', 'seed', 'lang','blockOrder'])	
	generateTrials({'subjCode':'testSubj2', 'seed':'20', 'lang':'e','blockOrder':'RL'}, ['subjCode', 'seed', 'lang','blockOrder'])	

	