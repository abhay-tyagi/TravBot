from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from random import uniform
from threading import Timer

import random
import time 
import sys
import signal
import select

import pyautogui
pyautogui.FAILSAFE = False

import datetime
import pickle
import urllib
import requests


driver = None

screenSize = [1366, 768]
a = None
c = None
b = None


username = ''
password = ''

homeLink = 'https://ts6.anglosphere.travian.com/'
resourceLink = homeLink + 'dorf1.php'
buildBase = 'build.php?id='
buildLink = homeLink + buildBase
heroBase = 'hero.php'
heroLink = '?t='
reportBase = 'berichte.php'
villageChangeBase = '?newdid='
villageChangeLink = resourceLink + villageChangeBase

fieldNames = ['Iron Mine', 'Cropland', 'Woodcutter', 'Clay Pit']
fields = [
			{0: [1, 3, 14, 17], 2: [4, 7, 10, 11], 1: [5, 6, 16, 18], 3: [2, 8, 9, 12, 13, 15]}, 
			{0: [3, 14, 17], 2: [1, 4, 7, 10, 11], 1: [5, 6, 16, 18], 3: [2, 8, 9, 12, 13, 15]}
		 ]

oneTimeTasks = [[], []]
villages = ['00 Rome', '01 Ephesus']
newdid = ['3689', '9064']

adventureFile = "adventureCheck.txt"
messageFile = "messageCheck.txt"
reportFile = "reportCheck.txt"
farmFile = "farmSend.txt"
attackFile = "attackCheck.txt"
troopFile = "toTrain.txt"
taskFile = "buildTasks.txt"
defaultTaskFile = "defaultTasks.txt"

cropDifference = [400, 100]


def stop_handler(sig, frame):
	print("\nQuit Browser")
	driver.quit()
	sys.exit(0)
signal.signal(signal.SIGINT, stop_handler)


def pause_handler(signum, frame):
    print("\nPaused")
    signal.pause()
signal.signal(signal.SIGTSTP, pause_handler)


def goToElement(element):
	position = element.location
	pyautogui.moveTo(20 + position['x']*screenSize[0]/a, 15 + (position['y'] + c)*screenSize[1]/b, uniform(0.5, 2.5), tween=pyautogui.easeInOutQuad)


def enableVPN():
	pyautogui.moveTo(1270, 80, 3)
	pyautogui.click()
	pyautogui.moveTo(1100, 410, 3)
	pyautogui.click()


def writeToFile(fileName, msg):
	with open(fileName, 'w') as f:
		f.write(str(msg))

def readFromFile(fileName):
	ans = ''
	with open(fileName) as f:
		ans = f.read()

	return ans


def initTravian(startNow):
	global driver
	global a
	global b
	global c

	if startNow:
		options = webdriver.ChromeOptions()
		options.add_argument("--start-maximized")
		options.add_extension('./Browsec-VPN-Free-and-Unlimited-VPN_v3.21.10.crx')
		driver = webdriver.Chrome(chrome_options=options)

		a = driver.execute_script("return outerWidth")
		c = driver.execute_script("return outerHeight - innerHeight")
		b = driver.execute_script("return outerHeight")

		enableVPN()

	driver.get(homeLink)

	try:
		current_window = driver.current_window_handle
		new_window = [window for window in driver.window_handles if window != current_window][0]
		driver.switch_to.window(new_window)
		driver.close()
		driver.switch_to.window(current_window)
	except Exception as e:
		print(e.__class__.__name__)

	element_present = EC.presence_of_element_located((By.ID, "s1"))

	try:
		WebDriverWait(driver, 10).until(element_present)
	except Exception as e:
		print(e.__class__.__name__)
		driver.refresh()

	try:
		u = driver.find_element_by_name('name')
		u.send_keys(username)
		p = driver.find_element_by_name('password')
		p.send_keys(password)

		loginButton = driver.find_element_by_id('s1')
		goToElement(loginButton)
		loginButton.click()
	except Exception as e:
		print(e.__class__.__name__)
		return False

	return True


def processTime(timeStr):
	if isinstance(timeStr, int):
		return int(timeStr)
	elif timeStr.isdigit():
		return int(timeStr)

	timeStr = list(timeStr)
	timeStr = timeStr[timeStr.index('>') + 1: len(timeStr)]
	timeStr = (str(timeStr)).split(':')

	waitingTime = 0
	multiple = 3600

	for item in timeStr:	
		timeSlice = ''
		for char in item:
			if char.isdigit():
				timeSlice += char

		waitingTime += multiple * int(timeSlice)
		multiple /= 60

	return waitingTime


def verifyLink(link):
	try:
		if driver.current_url != link:
			driver.get(link)
			return False
		
		return True
	except Exception as e:
		print("Trying to verify link. ", end='')
		print(e.__class__.__name__)


# def taskReward():
# 	try:
# 		newReward = driver.find_element_by_class_name('bigSpeechBubble')

# 		rewardButton = driver.find_element_by_class_name('reward')
# 		goToElement(rewardButton)
# 		rewardButton.click()

# 		element_present = EC.presence_of_element_located((By.CLASS_NAME, "questButtonGainReward"))
# 		WebDriverWait(driver, 60).until(element_present)		

# 		gainReward = driver.find_element_by_class_name('questButtonGainReward')
# 		goToElement(gainReward)
# 		gainReward.click()

# 		print("Collected Reward")
# 	except NoSuchElementException:
# 		pass


def upgradeField(id):
	driver.get(buildLink + str(id))

	try:
		waitingTime = driver.find_element_by_xpath("//div[@class='section1']/span[@class='clocks']").get_attribute('innerHTML')

		buildButton = driver.find_element_by_xpath("//div[@class='section1']/button[@class='green build']")
		goToElement(buildButton)
		buildButton.click()

		driver.get(resourceLink)
		return waitingTime
	except Exception as e:
		print("Trying to upgrade. ", end='')
		print(e.__class__.__name__)
		driver.get(resourceLink)
		return 0


def findLowestField(ind, resourceID):
	fieldList = fields[ind][resourceID]

	levels = []
	for field in fieldList:
		level = driver.find_element_by_xpath("//map[@id='rx']/area[@href='" + buildBase + str(field) + "']").get_attribute('alt')
		level = level.split(' ')
		level = level[len(level) - 1]
		levels.append(int(level))

	return [fieldList[levels.index(min(levels))], min(levels)]


def ongoingField():
	verifyLink(resourceLink)

	try:
		constructions = driver.find_elements_by_xpath("//div[@class='name']")

		for i in range(0, len(constructions)):
			constructions[i] = constructions[i].get_attribute('innerHTML')

		for construction in constructions:
			for field in fieldNames:
				if construction.find(field) != -1:
					print(field, end=' ')
					return True

		return False
	except NoSuchElementException:
		return False


def removeCrap(inputString):
	inputString = inputString.replace('\u202d', '')
	inputString = inputString.replace('\u202c', '')
	return inputString


def upgradeLowest(ind):
	try:
		verifyLink(resourceLink)

		if ongoingField():
			print("ongoing.")
			return 300

		upkeep = removeCrap(driver.find_element_by_id("stockBarFreeCrop").get_attribute('innerHTML'))

		flag = 0
		if int(upkeep) < 5:
			flag = 1

		lowestFields = []
		for i in range(0, 4):
			lowestFields.append(findLowestField(ind, i))

		if flag == 0:
			lowestFields.pop()

		targetField = None
		lowLevel = 1000
		for lowestField in lowestFields:
			if lowestField[1] < lowLevel:
				targetField = lowestField[0]
				lowLevel = lowestField[1]

		if flag == 1:
			targetField = lowestFields[len(lowestFields) - 1][0]

		return upgradeField(targetField)
	except Exception as e:
		print("Tried to upgrade lowest. ", end='')
		print(e.__class__.__name__)


def compareProduction(ind):
	try:
		verifyLink(resourceLink)

		if ongoingField():
			print("ongoing.")
			return 300

		upkeep = removeCrap(driver.find_element_by_id("stockBarFreeCrop").get_attribute('innerHTML'))

		flag = 0
		if int(upkeep) < 5:
			flag = 1

		element_present = EC.presence_of_element_located((By.ID, "production"))
		WebDriverWait(driver, 60).until(element_present)

		rateList = driver.find_elements_by_xpath("//table[@id='production']/tbody/tr/td[@class='num']")

		for i in range(0, len(rateList)):
			rateList[i] = int(removeCrap(rateList[i].get_attribute('innerHTML')))

		rateList[3] += cropDifference[ind]
		if flag == 1:
			rateList[3] -= 1000

		return upgradeField(findLowestField(ind, rateList.index(min(rateList)))[0])
	except Exception as e:
		print("Tried to compare production. ", end='')
		print(e.__class__.__name__)


def checkAdventure():
	try:
		lastAdventureCheck = readFromFile(adventureFile)
		if datetime.datetime.strptime(lastAdventureCheck, '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(seconds=random.randint(1500, 1800)) > datetime.datetime.now():
			return
	except Exception as e:
		print(e.__class__.__name__)
		print("No last adventure check")

	verifyLink(resourceLink)
	try:
		writeToFile(adventureFile, datetime.datetime.now())

		heroPresent = driver.find_element_by_class_name('uhero')
		driver.get(homeLink + heroBase + heroLink + str(3))

		adventure = driver.find_element_by_xpath("//td[@class='goTo']/a")
		goToElement(adventure)
		adventure.click()

		finalSend = driver.find_element_by_xpath("//form[@class='adventureSendButton']/div/button")
		goToElement(finalSend)
		finalSend.click()
			
		print("Sent on adventure")
	except Exception as e:
		print("Trying to check adventures. ", end='')
		print(e.__class__.__name__)

	driver.get(resourceLink)


def tryGold():
	try:
		npc = driver.find_element_by_xpath("//button[@value='Exchange resources']")

		if npc.get_attribute('class') == 'gold disabled':
			return False
		else:
			goToElement(npc)
			npc.click()

			element_present = EC.presence_of_element_located((By.XPATH, "//button[@value='Distribute remaining resources.']"))
			WebDriverWait(driver, 10).until(element_present)

			distributeButton = driver.find_element_by_xpath("//button[@value='Distribute remaining resources.']")
			goToElement(distributeButton)
			distributeButton.click()

			element_present = EC.presence_of_element_located((By.ID, "npc_market_button"))
			WebDriverWait(driver, 10).until(element_present)

			finalButton = driver.find_element_by_id('npc_market_button')
			goToElement(finalButton)
			finalButton.click()

			return True
	except:
		return False


def startTraining(numberTroops, link=''):
	if link != '' and driver.current_url != link:
		driver.get(link)

	try:
		goToElement(numberTroops)
		numberTroops.click()

		trainButton = driver.find_element_by_class_name('startTraining')
		goToElement(trainButton)
		trainButton.click()
	except:
		print("Tried to start Training. ", end=' ')
		print(e.__class__.__name__)


def trainSettlers():
	driver.get(homeLink + "build.php?s=1&id=21")
	try:
		numberTroops = driver.find_element_by_xpath("//div[@class='details']/a")

		if str(numberTroops.get_attribute('innerHTML')) != '0':
			startTraining(numberTroops, homeLink + "build.php?s=1&id=21") 
		elif tryGold():
			startTraining(numberTroops, homeLink + "build.php?s=1&id=21")
		else:
			print("Not enough resources for a settler")

	except Exception as e:
		print("Tried to train settler. ", end=' ')
		print(e.__class__.__name__)

	driver.get(resourceLink)


def buildTroops(ind, category):
	if category == 'Infantry':
		driver.get(buildLink + str(32))
	else:
		driver.get(buildLink + str(27))

	try:
		with open(troopFile) as f:
			trainData = f.readlines()

		trainData = trainData[ind].strip()
		numberTroops = driver.find_elements_by_xpath("//div[@class='details']/a")[int(trainData) - 1]

		if str(numberTroops.get_attribute('innerHTML')) == '0':
			print("Not enough resources for troops")
		else:
			startTraining(numberTroops)

	except Exception as e:
		print("Trying to build troops. ", end='')
		print(e.__class__.__name__)

	driver.get(resourceLink)


def createTradeRoutes(ind):
	try:
		for hr in range(0, 24):
			driver.get(buildLink + str(22))

			createRoute = driver.find_element_by_xpath("//a[contains(@href, 'gid=17&option=1')]")
			goToElement(createRoute)
			createRoute.click()

			for res in range(1, 5):
				amountField = driver.find_element_by_id("r" + str(res))
				goToElement(amountField)
				amountField.click()
				amountField.send_keys(str(300) if res == 4 else str(500))

			timeOfSupply = driver.find_element_by_xpath("//select[@id='userHour']/option[@value='" + str(hr) + "']")
			timeOfSupply.click()

			saveButton = driver.find_element_by_id('tradeSaveButton')
			goToElement(saveButton)
			saveButton.click()
	except Exception as e:
		print("Tried to create trade routes. ", end='')
		print(e.__class__.__name__)

	driver.get(resourceLink)


def sendFarms():
	try:
		lastFarmlist = readFromFile(farmFile)
		if datetime.datetime.strptime(lastFarmlist, '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(seconds=random.randint(2700, 2800)) > datetime.datetime.now():
			return
	except Exception as e:
		print(e.__class__.__name__)
		print("No last farmlist sent")

	driver.get('https://ts6.anglosphere.travian.com/build.php?tt=99&id=39')


	try:
		selectAll = driver.find_element_by_xpath("//div[@class='markAll']/input")
		goToElement(selectAll)
		selectAll.click()

		sendButton = driver.find_element_by_xpath("//button[@value='Start raid']")
		goToElement(sendButton)
		sendButton.click()

		writeToFile(farmFile, datetime.datetime.now())

	except Exception as e:
		print("Trying to send farmlist. ", end='')
		print(e.__class__.__name__)

	driver.get(resourceLink)


def takeTask(defaultTask, ind):
	i, o, e = select.select([sys.stdin], [], [], 5)

	if (i):
		return sys.stdin.readline().strip()
	else:
		print("No task received. Continuing default routine")
		return defaultTask[ind]


def gotoVillage(ind):
	driver.get(resourceLink)

	try:
		villageString = villageChangeBase + newdid[ind]		
		villageName = driver.find_element_by_xpath("//li/a[contains(@href, '" + villageString + "')]")
		goToElement(villageName)
		villageName.click()

	except Exception as e:
		print("Tried to change village. ", end='')
		print(e.__class__.__name__)


def findDefaultTasks():
	defaultTask = []

	with open(defaultTaskFile) as f:
		tasks = f.readlines()

	for task in tasks:
		defaultTask.append(task.strip())

	return defaultTask


def findBuildTargets():
	buildTarget = [[], []]

	with open(taskFile) as f:
		targets = f.readlines()

	i = 0
	for target in targets:
		target = target.strip()
		target = target.split(',')

		for task in target:
			buildTarget[i].append(target)
		i += 1

	return buildTarget


def playTravian():
	try:
		while(initTravian(True) == False):
			initTravian(False)

		while True:
			defaultTask = findDefaultTasks()
			buildTarget = findBuildTargets()

			for ind in range(0, len(villages)):
				gotoVillage(ind)

				print("Enter a task for village ", ind + 1, ": ")
				defaultTask[ind] = takeTask(defaultTask, ind)

				if defaultTask[ind] == 'Fields':
					timeString = compareProduction(ind)
				elif defaultTask[ind] == 'Infantry' or defaultTask[ind] == 'Cavalry':
					buildTroops(ind, defaultTask[ind])
				elif defaultTask[ind] == 'Hybrid':
					timeString = upgradeLowest(ind)

					if buildTarget[ind] != []:
						for building in buildTarget[ind]:
							timeString = upgradeField(building)

							if timeString != 0:
								break

				elif defaultTask[ind] == 'Build':
					timeString = upgradeField(35)

				for task in oneTimeTasks[ind]:
					if task == 'TradeRoute':
						createTradeRoutes(ind)

				oneTimeTasks[ind] = []

			waitingTime = random.randint(300, 600)

			gotoVillage(0)
			checkAdventure()
			sendFarms()

			print("Waiting from " + str(datetime.datetime.now()) + " to " + str(datetime.datetime.now() + datetime.timedelta(seconds=waitingTime)) + "\n\n")
			time.sleep(waitingTime)

		driver.quit()
	except Exception as e:
		print(e.__class__.__name__)


if __name__ == "__main__":
	while True:
		playTravian()

		try:
			driver.quit()
		except Exception as e:
			print("Tried to quit driver. ", end='')
			print(e.__class__.__name__)
