#So, this will be just an addition method of input, I think. Also, maybe this can hold both the agents AND the keyboard input.
import display
#from display import Direction
import Tkinter
from Tkinter import *
from board import *
import time
import copy
import makuUtil
from makuUtil import Directions
import conf
from conf import *
import random
from collections import deque

class Input:
	def __init__(self, parent):
		self.parent = parent
class KeyboardInput(Input):
	def __init__(self, parent):
		self.parent = parent
		self.master = Tk()
		self.master.title("Tetris")
		self.master.geometry("300x300")
		Label(self.master, text = "Play Tetris!\n\n").pack()
		Label(self.master,text="Click here for keyboard input").pack()
		self.master.bind("<Key>",self.pressedKey)
	def pressedKey(self,key):
		self.parent.pressedKey(key)
	def newTurn(self):
		print "New turn started"#this is only used in agent

class State:
	def __init__(self,tetroBoxList,parent,depth=0,boolGridAdditions=[]):
		#Can we not pass the boolGrid?
		#self.boolGrid = boolGrid #This is a dict
		#print "generating state"
		#print "tetroBoxList: ",tetroBoxList
		#print "parent: ",parent
		#print "\n\n\n"
		self.boolGridAdditions = boolGridAdditions
		self.tetroBoxList = makuUtil.sortCoords(tetroBoxList)
		self.parent = parent
		self.depth = depth
	def __getitem__(self,index): #Doesn't include tetro
		#print "self: ",self
		#print "thing: ",self.tetroBoxList
		#print "self.parent: ",self.parent
		#print "self.parent.parent: ",self.parent.parent
		if index in self.tetroBoxList:
			return False
		if index in self.boolGridAdditions: 
			print "in the additions"
			return True
		return self.parent.parent.gameGrid[tuple(index)]
		#return self.boolGrid[tuple(index)]
	def __setitem__(self,index,value):
		if not value==True:
			print "TRYING TO SET AS NOT TRUE"
		if not index in self.boolGridAdditions:
			self.boolGridAdditions.append(tuple(index))
	def getPossibleEndStates(self,depth=0,onlyBest=False):
		#print "1"
		def isTerminalState(state):
			for box in state.tetroBoxList:
				if (box[1]+1)>=boardDepth or state[(box[0],box[1]+1)]:
					return True
			return False
		#print "Se",self.tetroBoxList
		topBoxes = tuple([tuple(box) for box in self.tetroBoxList])
		#print "topBoxes: ",topBoxes
		initialDownPush = getInitialDownPush(topBoxes,self)
		startBoxes = makuUtil.sortCoords(tuple([(box[0],box[1]+initialDownPush) for box in self.tetroBoxList]))
		#print "startBoxes: ",startBoxes
		startState = State(startBoxes,self.parent)
		frontier = deque([startBoxes])
		explored = {startBoxes:tuple([Directions.D]*initialDownPush)} #dict to actions
		startSorted = makuUtil.sortCoords(startBoxes)
		tempState = State(startBoxes,self.parent)
		boxesToState = {startBoxes:startState}
		terminalStates = []
		bestTerminalVal = 0
		while frontier:
			#print "lenFrontier: ",len(frontier)
			front = frontier.popleft()
			frontState = boxesToState[front]
			oldActions = list(explored[front])
			newActions = frontState.getLegalActions()
			for newAction in newActions:
				newState = frontState.generateSuccessor(newAction)
				newBoxes = tuple([tuple(box) for box in newState.tetroBoxList])
				sortedNewBoxes = makuUtil.sortCoords(newBoxes)
				if not newBoxes in explored:
					explored[newBoxes] = tuple(oldActions+[newAction])
					boxesToState[newBoxes] = newState
					frontier.append(newBoxes)
					if isTerminalState(newState):
						if onlyBest:
							newVal = newState.evaluationFunction()
							if newVal>bestTerminalVal:
								bestTerminalVal = newVal
								terminalStates = []
							if newVal>=bestTerminalVal:
								terminalStates.append(newState)
						else:
							terminalStates.append(newState)
		#print "got terminal states"
		#print "terminalStates: ",terminalStates
		return terminalStates
	#def getComboGrid(self):
	#	comboGrid = copy.copy(self.boolGrid)
	#	for tetroBox in self.tetroBoxList:
	#		comboGrid[tuple(tetroBox)] = True
	#	return comboGrid
	def evaluationFunction(self):
		def getComboSpot(col,row,state):
			if (col,row) in state.tetroBoxList:
				return True
			return state[col,row]
		boxes = self.tetroBoxList
		#comboGrid = self.getComboGrid()
		
		#self.boolGridAdditions = self.boolGridAdditions + list(boxes)
		runningScore = 0.0
		for row in range(boardDepth-1,0,-1):
			for col in range(boardWidth):
				if getComboSpot(col,row,self):
					height = float(boardDepth - row)
					runningScore+=(1/(height*2))
		runningScore+=self.parent.parent.points * boardWidth * 2
		return runningScore
	def getLegalActions(self):
		originalActions = [d for d in Directions.legalMoves]
		actions = [d for d in Directions.legalMoves]
		for direction in originalActions:
			if direction in Directions.rotations:
				rotatedBoxes = makuUtil.getRotatedCoords(self.parent.parent.gameGrid.asDict(),self.tetroBoxList)
				if not rotatedBoxes:
					actions.remove(direction)
					continue
				for newBox in rotatedBoxes:
					if makuUtil.coordsAreIllegal(self.parent.parent.gameGrid.asDict(),newBox):
						if direction in actions:
							actions.remove(direction)
							continue
			else:
				for box in self.tetroBoxList:
					newBox = (box[0]+Directions.colMod[direction],box[1]+Directions.rowMod[direction])
					if makuUtil.coordsAreIllegal(self.parent.parent.gameGrid.asDict(),newBox):
						if direction in actions:
							actions.remove(direction)
							continue
		return actions
			
	def generateSuccessor(self,direction):
		newBoxes = []
		if direction in Directions.directions:
			newBoxes = [[box[0]+Directions.colMod[direction],box[1]+Directions.rowMod[direction]] for box in self.tetroBoxList]
		elif direction in Directions.rotations:
			newBoxes = makuUtil.getRotatedCoords(self.parent.parent.gameGrid.asDict(),self.tetroBoxList)
		newState = State(newBoxes,self.parent,boolGridAdditions = self.boolGridAdditions)
		return newState
	def __str__(self):
		s = ""
		for row in range(boardDepth):
			for col in range(boardWidth):
				if (col,row) in self.tetroBoxList: #Is this list and not tuple?
					s+='T'
				elif self[col,row]:
					s+='#'
				else:
					s+='0'
			s+="\n"
		s+="Falling blocks: "+str(self.tetroBoxList)+"\n"
		s+="Additional true spaces: "+str(self.boolGridAdditions)+"\n"
		return s
	def expectimax(self):
		if self.depth >= maxDepth:
			return self.evaluationFunction()
		else:
			possibleNewTetros = [Tetro(tetro,self.parent.parent.board) for tetro in Tetro.types]
			possibleNewTurns = [self.generateNewTurn(tetro) for tetro in possibleNewTetros]
			possibleNewTurnVals = []
			for i in range(len(possibleNewTurns)):#possibleNewTurns:
				#print "1"
				possibleNewEndStatesInNewTurn = possibleNewTurns[i].getPossibleEndStates()
				#print "2"
				#bestNewEndStatesInNewTurn = [possibleNewEndStateInNewTurn for possibleNewEndStateInNewTurn in possibleNewEndStatesInNewTurn if not possibleNewEndStateInNewTurn.didSomethingStupid()]#[possibleNewEndStatesInNewTurn[i] for i in range(len(possibleNewEndStatesInNewTurn)) if evalVals[i]==bestEvalVal]
				#print "3"
				expectivalSum = 0
				expectivalCounter = 0
				#print "2"
				for possibleNewEndStateInNewTurn in possibleNewEndStatesInNewTurn:
					possibleNewEndStateInNewTurn.depth = self.depth+1
					expectival = possibleNewEndStateInNewTurn.expectimax()
					expectivalSum += expectival
					expectivalCounter+=1
				#print "3"
				expectivalAvg = 0 if (expectivalCounter == 0) else float(expectivalSum)/expectivalCounter
				possibleNewTurnVals.append(expectivalAvg)
			expectivalAvg = makuUtil.avg(possibleNewTurnVals)
			return expectivalAvg
			
	def generateNewTurn(self,tetro):
		print "ay: ",self.tetroBoxList
		boolGridAdditions = self.boolGridAdditions + [tuple(coord) for coord in self.tetroBoxList]
		newCoords = copy.copy(tetro.spaces)
		newDepth = self.depth+1
		newTurnState = State(newCoords,self.parent,depth=newDepth,boolGridAdditions = boolGridAdditions)
		return newTurnState
	#def generateEndTurnBoolGrid(self):
	#	newBoolGrid = copy.copy(self.boolGrid)
	#	for coord in self.tetroBoxList:
	#		newBoolGrid[tuple(coord)] = True
	#	return newBoolGrid
	def didSomethingStupid(self):
		#This is for checking for stuff like blocking spaces
		#def getSmallerBoolGrid(state):
		#	comboGrid = state.getComboGrid()
		#	highestGridRow = 19
		#	for row in range(boardDepth-1,0,-1):
		#		for col in range(boardWidth):
		#			if comboGrid[col,row]:
		#				highestGridRow = row
		#	smallerGrid = {(col,row-highestGridRow):bool(comboGrid[col,row]) for col in range(boardWidth) for row in range(highestGridRow,boardDepth)}
		#	return smallerGrid
		#smallerGrid = getSmallerBoolGrid(self)
		#gridDepth = max([coord[1] for coord in smallerGrid])+1
		#gridWidth = boardWidth
		for row in range(boardDepth):
			for col in range(boardWidth):
				currentCoord = (col,row)
				blocked = True
				for direction in [Directions.U,Directions.L,Directions.R]:
					coordToDirection = makuUtil.getCoordToDirection(currentCoord,direction)
					if not makuUtil.coordsAreIllegal(self.parent.parent.gameGrid.asDict(),coordToDirection):
						blocked = False
				if blocked:
					return True
		return False
		
class Agent(Input):
	def __init__(self, parent):
		self.parent = parent
		self.grid = self.parent.gameGrid.asDict()
		self.state = None
	def newTurn(self):
		self.grid = self.parent.gameGrid.asDict()
		#print "AEJOEA",self.parent.fallingBlocks
		startCoords = tuple([tuple(block) for block in self.parent.fallingBlocks])
		#print "AEJOEA",startCoords
		self.state = State(startCoords,self)
		#print "in3onn2"
		actionsToTake = self.getActions()
		time.sleep(0.1)
		for action in actionsToTake:
			time.sleep(0.01)
			self.parent.pressedKeyChar(action)
			time.sleep(0.01)
	def getActions(self):
		#Call when a new tetro is added
		#This should return a list of actions (directions) to get the tetro to a good place
		startState = State(self.parent.fallingBlocks,self)
		possibleEndStates = startState.getPossibleEndStates()
		possibleEndStateVals = [possibleEndState.evaluationFunction() for possibleEndState in possibleEndStates]
		bestVal = max(possibleEndStateVals)
		bestEndStates = [possibleEndStates[i] for i in range(len(possibleEndStates)) if (possibleEndStateVals[i]==bestVal)]
		endState = random.choice(bestEndStates)
		#print "StartState1: \n",startState
		#print "endState1: \n",endState
		path = getPath(startState,endState)
		return path
			
		
		
		
		
def getPath(startState,endState):
	def checkPath(startState,endState,actions):
		tempState = startState
		for action in actions:
			tempState = tempState.generateSuccessor(action)
		tempStateBoxCheck = tuple([tuple(box) for box in tempState.tetroBoxList])
		endStateBoxCheck = tuple([tuple(box) for box in endState.tetroBoxList])
		if tempStateBoxCheck == endStateBoxCheck:
			return tuple(list(actions)+[Directions.D])
		else:
			print "temp: ",tempStateBoxCheck
			print "end: ",endStateBoxCheck
	def pathFinder(startState,endState):
		print "startState: \n",startState
		print "endState: \n",endState
		topBoxes = tuple([tuple(box) for box in startState.tetroBoxList])
		initialDownPush = getInitialDownPush(topBoxes,startState)
		startBoxes = tuple([(box[0],box[1]+initialDownPush) for box in startState.tetroBoxList])
		startState = State(startBoxes,startState.parent,startState.boolGridAdditions)
		frontier = deque([startBoxes])
		explored = {startBoxes:tuple([Directions.D]*initialDownPush)} #dict to actions
		debDict = {startBoxes:(startBoxes)}
		#tempState = State(startBoxes,startState.parent,startState)
		boxesToState = {startBoxes:startState}
		terminalStates = []
		testEndBoxes = tuple([tuple(box) for box in endState.tetroBoxList])
		while frontier:
			front = frontier.popleft()
			frontState = boxesToState[front]
			oldActions = list(explored[front])
			newActions = frontState.getLegalActions()
			for newAction in newActions:
				newState = frontState.generateSuccessor(newAction)
				newBoxes = tuple([tuple(box) for box in newState.tetroBoxList])
				if not newBoxes in explored:
					explored[newBoxes] = tuple(oldActions+[newAction])
					debDict[newBoxes] = tuple(list(debDict[front])+[newBoxes])
					boxesToState[newBoxes] = newState
					if newBoxes == testEndBoxes:
						pathActions = tuple(list(explored[front])+[newAction])
						return pathActions
					frontier.append(newBoxes)
	pathFound = pathFinder(startState,endState)
	endState.didSomethingStupid()
	approvedPath = checkPath(startState,endState,pathFound)
	print "path: ",approvedPath
	return approvedPath
def getInitialDownPush(startBoxes,state):
	deepestBoxRow = max([box[1] for box in startBoxes])
	highestGridRow = 19
	for row in range(boardDepth-1,0,-1):
		for col in range(boardWidth):
			if state[col,row]:
				highestGridRow = row
	calculatedDownPush = highestGridRow-deepestBoxRow-1
	return max(0,calculatedDownPush)