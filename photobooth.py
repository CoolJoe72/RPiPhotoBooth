#!/usr/bin/env python

# Raspberry Pi Photo-Booth
# created by cooljoe72@gmail.com
#

import os # command to the os for shutdown and file cleanup
import glob
import sys
from time import sleep, strftime # for timeing things and getting now
import picamera # to use the Raspberry Pi Camera
import pygame # for making a window to display images
from pgmagick import Image, ImageList # manipulates images for making animated gif
import pytumblr # connecting and sending the image to tumblr
from tumblr_keys import * # this imports content for tumblr
import RPi.GPIO as GPIO # access to the GPIO ports on the RPi setup buttons and lights
import atexit

#######################
### Variables Setup ###
#######################
getready_led = 15 # P1 pin 15
pose_led = 19 # P1 pin 19
upload_led = 21 # P1 pin 21
done_led = 23 # P1 pin 23
flash_relay = 13 # P1 pin 13 for flash relay
start_shoot = 22 # P1 pin 22 for the big red button to start the photo shoot
kill_rpi = 18 # P1 pin 18 button to shutdown the RPi
kill_booth = 16 # P1 pin 16 button to end this program.

total_pics = 4 # number of photos to be taken
capture_delay = 3 # number of seconds between photos
prep_delay = 4 # number of seconds at start of photo-shoot to getready
gif_delay = 100 # time for each frame of the animated gif in ms

file_path = '/home/pi/photobooth/pics/' # the path for images you are saving

w = 800 # width of screen in pixels
h = 480 # height of screen in pixels
imgsize_x = 640 # sets the width for camera and processing
imgsize_y = 480 # sets the height for camera and proccessing
offset_x = 80 # centers the image on the display
offset_y = 0 # distance from the top left corner
replay_delay = 1 # how long to wait between images displayed
replay_cycles = 4 # number of times the slideshow loops

###########################
### GPIO config & Setup ###
###########################
GPIO.setmode(GPIO.BOARD)
GPIO.setup(getready_led,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(pose_led,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(upload_led,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(done_led,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(flash_relay,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(start_shoot,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(kill_rpi,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(kill_booth,GPIO.IN, pull_up_down=GPIO.PUD_UP)

#################
### Functions ###
#################

def cleanup():
	print('Ended abruptly')
	pygame.quit()
	GPIO.cleanup()
atexit.register(cleanup)

def shut_it_down(channel):
	print "Shutting down..."
	GPIO.output(getready_led,True);
	GPIO.output(pose_led,True);
	GPIO.output(upload_led,True);
	GPIO.output(done_led,True);
	sleep(3)
	os.system("sudo halt")

def edit_photobooth(channel):
	print "Photo booth app ended. RPi still running"
	GPIO.output(getready_led,True);
	sleep(3)
	pygame.quit()
	sys.exit()

def is_connected():
	try:
		client = pytumblr.TumblrRestClient(
			consumer_key,
			consumer_secret,
			token_key,
			token_secret
		)
		return True
	except:
		pass
	return False

def display_pics(jpg_group):
	pygame.init()
	screen = pygame.display.set_mode((w,h),pygame.NOFRAME|pygame.OPENGL)
	pygame.display.set_caption('Photo Booth Pics')
	pugame.mouse.set_visible(False)
	for i in range(0, replay_cycles):
		for i in range(1, total_pics+1):
			filename = file_path + jpg_group + "-0" + str(i) + ".jpg"
			img = pygame.image.load(filename)
			#img = pygame.transform.scale(img,(imgsize_x,imgsize_y))
			screen.blit(img,(offset_x,offset_y))
			pygame.display.flip()
			time.sleep(replay_delay)

def setup_camera():
	camera = picamera.PiCamera()
	camera.resolution = (imgsize_x,imgsize_y)
	GPIO.output(flash_relay,True)
	camera.awb_mode = 'flash'
	camera.framerate = 30
	sleep(2)
	camera.shutter_speed = camera.exposure_speed
	camera.exposure_mode = 'off'
	g = camera.awb_gains
	camera.awb_mode = 'off'
	camera.awb_gains = g
	GPIO.output(flash_relay,False)

def 