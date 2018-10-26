from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time 
import sys
import signal
import pyautogui
import datetime
import pickle
import urllib
import requests
from random import uniform


driver = None

screenSize = [1366, 768]
a = None
c = None
b = None

homeLink = 'https://ts6.anglosphere.travian.com/'
resourceLink = homeLink + 'dorf1.php'
buildBase = 'build.php?id='
buildLink = homeLink + buildBase

fieldNames = ['Iron Mine', 'Cropland', 'Woodcutter', 'Clay Pit']
fields = {0: [1, 3, 14, 17], 2: [4, 7, 10, 11], 1: [5, 6, 16, 18], 3: [2, 8, 9, 12, 13, 15]}


def signal_handler(sig, frame):
	print("Quit Browser")
	driver.quit()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def goToElement(element):
	position = element.location
	pyautogui.moveTo(position['x']*screenSize[0]/a, (position['y'] + c)*screenSize[1]/b, uniform(0.5, 2.5))


def initTravian(startNow):
	global driver
	global a
	global b
	global c

	if startNow:
		options = Options()	
		# options.add_argument("--headless")
		# options.set_preference("dom.webnotifications.enabled", False)	
		driver = webdriver.Firefox()
		
		a = driver.execute_script("return outerWidth")
		c = driver.execute_script("return outerHeight - innerHeight")
		b = driver.execute_script("return outerHeight")

		# options = webdriver.ChromeOptions()
		# options.add_extension('./UltraSurf-Security,-Privacy-&-Unblock-VPN_v1.5.4.crx')
		# driver = webdriver.Chrome(chrome_options=options)

	driver.get(homeLink)

	element_present = EC.presence_of_element_located((By.ID, "s1"))
	WebDriverWait(driver, 60).until(element_present)

	username = driver.find_element_by_name('name')
	username.send_keys('')
	password = driver.find_element_by_name('password')
	password.send_keys('')

	loginButton = driver.find_element_by_id('s1')
	goToElement(loginButton)
	loginButton.click()


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
	if driver.current_url != link:
			driver.get(link)


def taskReward():
	try:
		newReward = driver.find_element_by_class_name('bigSpeechBubble')

		rewardButton = driver.find_element_by_class_name('reward')
		goToElement(rewardButton)
		rewardButton.click()

		element_present = EC.presence_of_element_located((By.CLASS_NAME, "questButtonGainReward"))
		WebDriverWait(driver, 60).until(element_present)		

		gainReward = driver.find_element_by_class_name('questButtonGainReward')
		goToElement(gainReward)
		gainReward.click()

		print("Collected Reward")
	except NoSuchElementException:
		print("No new reward")


def upgradeField(id):
	driver.get(buildLink + str(id))

	try:
		waitingTime = driver.find_element_by_xpath("//div[@class='section1']/span[@class='clocks']").get_attribute('innerHTML')

		buildButton = driver.find_element_by_xpath("//div[@class='section1']/button[@class='green build']")
		goToElement(buildButton)
		buildButton.click()

		return waitingTime
	except NoSuchElementException:
		driver.back()
		return 0


def findLowestField(resourceID):
	fieldList = fields[resourceID]

	levels = []
	for field in fieldList:
		level = driver.find_element_by_xpath("//map[@id='rx']/area[@href='" + buildBase + str(field) + "']").get_attribute('alt')
		level = level.split(' ')
		level = level[len(level) - 1]
		levels.append(int(level))

	print(levels)
	target = fieldList[levels.index(min(levels))]

	print(target)
	return upgradeField(target)


def ongoingField():
	verifyLink(resourceLink)

	try:
		constructions = driver.find_elements_by_xpath("//div[@class='name']")

		for i in range(0, len(constructions)):
			constructions[i] = constructions[i].get_attribute('innerHTML')

		for construction in constructions:
			for field in fieldNames:
				if construction.find(field) != -1:
					print(field)
					return True

		return False
	except NoSuchElementException:
		print("No constructions.")
		return False


def compareProduction():
	verifyLink(resourceLink)

	if(ongoingField()):
		print("Ongoing construction")
		return 300

	element_present = EC.presence_of_element_located((By.ID, "production"))
	WebDriverWait(driver, 60).until(element_present)

	rateList = driver.find_elements_by_xpath("//table[@id='production']/tbody/tr/td[@class='num']")

	for i in range(0, len(rateList)):
		rateStr = list(rateList[i].get_attribute('innerHTML'))
		rateStr = rateStr[rateStr.index('\u202d') + 1: rateStr.index('\u202c')]

		number = ''
		for digit in rateStr:
			number += digit
		rateList[i] = int(number)

	rateList[3] += 20
	return findLowestField(rateList.index(min(rateList)))


def checkAdventure():
	verifyLink(resourceLink)

	try:
		heroPresent = driver.find_element_by_class_name('uhero')

		adventuresBubble = driver.find_element_by_xpath("//div[@class='speechBubbleContent']")
		numberAdventures = adventuresBubble.get_attribute('innerHTML')

		if numberAdventures.isdigit():
			adventureButton = driver.find_element_by_class_name('adventureWhite')
			goToElement(adventureButton)
			adventureButton.click()

			adventure = driver.find_element_by_xpath("//td[@class='goTo']/a")
			goToElement(adventure)
			adventure.click()

			finalSend = driver.find_element_by_xpath("//form[@class='adventureSendButton']/div/button")
			goToElement(finalSend)
			finalSend.click()

			print("Sent on adventure")
		else:
			print("No adventures available")

	except NoSuchElementException:
		print("No new adventures")
		return


if __name__ == "__main__":

	initTravian(True)

	while True:
		if driver.current_url == homeLink:
			initTravian(False)

		verifyLink(resourceLink)

		time.sleep(2)

		timeString = compareProduction()
		waitingTime = processTime(timeString)

		print("Will wait for: " + str(waitingTime) + " at " + str(datetime.datetime.now()))
		checkAdventure()
		taskReward()

		if waitingTime > 0:
			time.sleep(waitingTime)
		else:
			time.sleep(300)


	a = input()
	driver.quit()
