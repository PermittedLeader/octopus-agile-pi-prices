# this is the script you run every half hour by cron, best done about 20-30 seconds after the half hour to ensure
# that the right datetime is read in.
# For example --->   */30 * * * * sleep 20; /usr/bin/python3 octoprice_main_inky.py > /home/pi/cron.log

# NOTE - USAGE
# This script *won't work* unless you have run (python3 store_prices.py) at least once in the last 'n' hours (n is variable, it updates 4pm every day)
# You also need to update store_prices.py to include your own DNO region.

from inky.auto import InkyPHAT
from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium, HankenGroteskLight  # should you choose to switch to gross fonts
#from font_intuitive import Intuitive
from font_fredoka_one import FredokaOne  # this is the font we're currently using
from PIL import Image, ImageFont, ImageDraw

import sqlite3
import datetime
import pytz
import time
from urllib.request import pathname2url

version = "2.6.0"

print("Agile Prices, Portrait screen. version "+version)

##  -- Detect display type automatically
try:
    inky_display = InkyPHAT("red")
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

try:
    # connect to the database in rw mode so we can catch the error if it doesn't exist
    DB_URI = 'file:{}?mode=rw'.format(pathname2url('agileprices.sqlite'))
    conn = sqlite3.connect(DB_URI, uri=True)
    cur = conn.cursor()
except sqlite3.OperationalError as error:
    # handle missing database case
    raise SystemExit('Database not found - you need to run store_prices.py first.') from error

inky_display.set_border(inky_display.WHITE)
img = Image.new("P", (inky_display.HEIGHT,inky_display.WIDTH))
draw = ImageDraw.Draw(img)

# find current time and convert to year month day etc
the_now = datetime.datetime.now(datetime.timezone.utc)
the_now_local = the_now.astimezone(pytz.timezone('Europe/London'))

the_year = the_now.year
the_month = the_now.month
the_hour = the_now.hour
the_day = the_now.day
if the_now.minute < 30:
	the_segment = 0
else:
	the_segment = 1

red_threshold = 20

# select from db where record == the above
cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
		(the_year, the_month, the_day, the_hour, the_segment))

rows = cur.fetchall()

for row in rows:
	row[5]

# get price
current_price = row[5] # literally this is hardcoded tuple. DONT ADD ANY EXTRA FIELDS TO THAT TABLE on the sqlite db or you'll get something that isn't price.

# Find Next Price
# find current time and convert to year month day etc
the_now = datetime.datetime.now(datetime.timezone.utc)
now_plus_10 = the_now + datetime.timedelta(minutes = 30)
the_year = now_plus_10.year
the_month = now_plus_10.month
the_hour = now_plus_10.hour
the_day = now_plus_10.day
if now_plus_10.minute < 30:
	the_segment = 0
else:
	the_segment = 1


# select from db where record == the above
cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
		(the_year, the_month, the_day, the_hour, the_segment))

rows = cur.fetchall()

for row in rows:
	row[5]

# get price
next_price = row[5] # literally this is peak tuple. DONT ADD ANY EXTRA FIELDS TO THAT TABLE



# Find Next+1 Price
# find current time and convert to year month day etc
the_now = datetime.datetime.now(datetime.timezone.utc)
now_plus_10 = the_now + datetime.timedelta(minutes = 60)
the_year = now_plus_10.year
the_month = now_plus_10.month
the_hour = now_plus_10.hour
the_day = now_plus_10.day
if now_plus_10.minute < 30:
	the_segment = 0
else:
	the_segment = 1


# select from db where record = ^
cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
		(the_year, the_month, the_day, the_hour, the_segment))

rows = cur.fetchall()

for row in rows:
	row[5]



# get price
nextp1_price = row[5] # literally this is peak tuple. DONT ADD ANY EXTRA FIELDS TO THAT TABLE



# Find Next+2 Price
# find current time and convert to year month day etc
the_now = datetime.datetime.now(datetime.timezone.utc)
now_plus_10 = the_now + datetime.timedelta(minutes = 90)
the_year = now_plus_10.year
the_month = now_plus_10.month
the_hour = now_plus_10.hour
the_day = now_plus_10.day
if now_plus_10.minute < 30:
	the_segment = 0
else:
	the_segment = 1


# select from db where record == the above
cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
		(the_year, the_month, the_day, the_hour, the_segment))
rows = cur.fetchall()
for row in rows:
	row[5]
# get price
nextp2_price = row[5] # literally this is peak tuple. DONT ADD ANY EXTRA FIELDS TO THAT TABLE



# attempt to make an list of the next 42 hours of values
prices = []

for offset in range(0, 48):  ##24h = 48 segments
	min_offset = 30 * offset
	the_now = datetime.datetime.now(datetime.timezone.utc)
	now_plus_offset = the_now + datetime.timedelta(minutes=min_offset)
	the_year = now_plus_offset.year
	the_month = now_plus_offset.month
	the_hour = now_plus_offset.hour
	the_day = now_plus_offset.day
	if now_plus_offset.minute < 30:
		the_segment = 0
	else:
		the_segment = 1
	cur.execute("SELECT * FROM prices WHERE year=? AND month=? AND day=? AND hour=? AND segment=?",
				(the_year, the_month, the_day, the_hour, the_segment))
	# rows = cur.fetchall()
	# get price
	row = cur.fetchone()
	if row is None:
		prices.append(999) # we don't have that price yet!
	else:
		prices.append(row[5])

two_hour_average = []
for i in range(0,len(prices)-3):
	two_hour_average.append((prices[i]+prices[i+1]+prices[i+2]+prices[i+3])/4)

if (inky_display.WIDTH == 212): #low res display
	print("Assembling draw")
	font = ImageFont.truetype(HankenGroteskMedium, 10)
	message = (str(the_now_local.time())[0:5])
	w, h = font.getsize(message)
	#x = (inky_display.WIDTH / 2) - (w / 2)
	#y = (inky_display.HEIGHT / 2) - (h / 2)
	x = inky_display.HEIGHT - w
	y = 0
	draw.text((x, y), message, inky_display.BLACK, font)

	font = ImageFont.truetype(HankenGroteskLight, 10)
	message = "v" + version
	w, h = font.getsize(message)
	#x = (inky_display.WIDTH / 2) - (w / 2)
	#y = (inky_display.HEIGHT / 2) - (h / 2)
	x = 0
	y = 0
	draw.text((x, y), message, inky_display.BLACK, font)


	font = ImageFont.truetype(HankenGroteskMedium, 35)
	message = "{0:.1f}".format(current_price) + "p"
	w2, h2 = font.getsize(message)
	x = (inky_display.HEIGHT / 2) - (w2 / 2)
	#y = (inky_display.HEIGHT / 2) - (h / 2)
	y = h

	if (current_price > red_threshold):
		draw.text((x, y), message, inky_display.RED, font)
	else:
		draw.text((x, y), message, inky_display.BLACK, font)


	right_column = 0
	second_row = 75
	third_row = 120
	fourth_row = 165

	# NEXT
	time_change = datetime.timedelta(minutes=30) 
	new_time = the_now_local + time_change 
	message = (str(new_time.time())[0:5])
	font = ImageFont.truetype(HankenGroteskLight, 15)
	w2, h2 = font.getsize(message)
	x = 0
	y = fourth_row
	draw.text((x, y), message, inky_display.BLACK, font)
	
	time_change = datetime.timedelta(minutes=30) 
	new_time = the_now_local + time_change 
	message = "{0:.1f}".format(next_price) + "p"
	font = ImageFont.truetype(HankenGroteskMedium, 15)
	w2, h2 = font.getsize(message)
	x = inky_display.HEIGHT - w2
	y = y
	if (next_price > red_threshold):
		draw.text((x,y), message, inky_display.RED, font)
	else:
		draw.text((x, y), message, inky_display.BLACK, font)

	# NEXT
	time_change = datetime.timedelta(minutes=60) 
	new_time = the_now_local + time_change 
	message = (str(new_time.time())[0:5])
	font = ImageFont.truetype(HankenGroteskLight, 15)
	w2, h2 = font.getsize(message)
	x = 0
	y = y + h2
	draw.text((x, y), message, inky_display.BLACK, font)

	message = "{0:.1f}".format(nextp1_price) + "p"
	font = ImageFont.truetype(HankenGroteskMedium, 15)
	w3, h3 = font.getsize(message)
	x = inky_display.HEIGHT - w3
	y = y

	if (nextp1_price > red_threshold):
		draw.text((x,y), message, inky_display.RED, font)
	else:
		draw.text((x, y), message, inky_display.BLACK, font)

	# NEXT
	time_change = datetime.timedelta(minutes=90) 
	new_time = the_now_local + time_change 
	message = (str(new_time.time())[0:5])
	font = ImageFont.truetype(HankenGroteskLight, 15)
	w2, h2 = font.getsize(message)
	x = 0
	y = y + h2
	draw.text((x, y), message, inky_display.BLACK, font)

	message = "{0:.1f}".format(nextp2_price) + "p"
	font = ImageFont.truetype(HankenGroteskMedium, 15)
	w3, h3 = font.getsize(message)
	x = inky_display.HEIGHT - w3
	y = y

	if (nextp2_price > red_threshold):
		draw.text((x,y), message, inky_display.RED, font)
	else:
		draw.text((x, y), message, inky_display.BLACK, font)

	pixels_per_h = 1.5  # how many pixels 1p is worth
	pixels_per_w = 2  # how many pixels 1/2 hour is worth
	chart_base_loc = 104  # location of the bottom of the chart on screen in pixels
	#chart_base_loc = 85  # location of the bottom of the chart on screen in pixels
	number_of_vals_to_display = 48 # 36 half hours = 18 hours

	# plot the graph
	#lowest_price_next_24h = min(i for i in prices if i > 0)
	lowest_price_next_24h = min(i for i in prices)
	if (lowest_price_next_24h < 0):
		chart_base_loc = 104 + lowest_price_next_24h*pixels_per_h - 2 # if we have any negative prices, shift the base of the graph up! 

	# go through each hour and get the value

	for i in range(0,number_of_vals_to_display):
		if prices[i] < 999:
			scaled_price = prices[i] * pixels_per_h # we're scaling it by the value above

			if prices[i] < 0: 
				ink_color = inky_display.RED
			else:
				if prices[i] >= red_threshold:   
					ink_color = inky_display.RED
				else:
					ink_color = inky_display.BLACK

			# takes a bit of thought this next bit, draw a rectangle from say x =  2i to 2(i-1) for each plot value
			# pixels_per_w defines the horizontal scaling factor (2 seems to work)
			draw.rectangle((1+pixels_per_w*i,chart_base_loc,((pixels_per_w*i)-pixels_per_w),(chart_base_loc-scaled_price)),ink_color)
			if i%6 == 0 and i > 0:
				message = str(int(i/2))+"h"
				font = ImageFont.truetype(HankenGroteskMedium, 7)
				w, h = font.getsize(message)
				draw.text(((1+pixels_per_w*i)-(w/2),chart_base_loc+3), message[0:2], inky_display.BLACK, font)
			if i == 0:
				message = ""
				font = ImageFont.truetype(HankenGroteskMedium, 7)
				draw.text((1,chart_base_loc+3), message, inky_display.BLACK, font)


	#draw minimum value on chart  <- this doesn't seem to work yet
	# font = ImageFont.truetype(FredokaOne, 15)
	# msg = "{0:.1f}".format(lowest_price_next_24h) + "p"
	# draw.text((4*(minterval-1),110),msg, inky_display.BLACK, font)

	# draw the bottom right min price and how many hours that is away
	font = ImageFont.truetype(HankenGroteskMedium, 10)
	msg = "min:"+"{0:.1f}".format(lowest_price_next_24h) + "p"
	draw.text((0,third_row), msg, inky_display.BLACK, font)
	# we know how many half hours to min price, now figure it out in hours.
	minterval = (round(prices.index(lowest_price_next_24h)/2))
	msg = "in:"+str(minterval)+"hrs"

	# and convert that to an actual time
	# note that this next time will not give you an exact half hour if you don't run this at an exact half hour eg cron
	# because it's literally just adding n * 30 mins!
	# could in future add some code to round to 30 mins increments but it works for now.

	min_offset = prices.index(lowest_price_next_24h) * 30
	time_of_cheapest = the_now_local + datetime.timedelta(minutes=min_offset)
	time_of_cheapest_formatted = (str(time_of_cheapest.time())[0:5])
	font = ImageFont.truetype(HankenGroteskMedium, 10)
	draw.text((0,third_row+10), msg+" ("+time_of_cheapest_formatted+")", inky_display.BLACK, font)

	draw.line((0,third_row+12),width=1)

	lowest_period_next_24h = min(i for i in two_hour_average)
	# draw the bottom right min price and how many hours that is away
	font = ImageFont.truetype(HankenGroteskMedium, 10)
	msg = "best 2hr: "+"{0:.1f}".format(lowest_period_next_24h) + "p"
	draw.text((0,third_row+22), msg, inky_display.BLACK, font)
	# we know how many half hours to min price, now figure it out in hours.
	minterval = (round(two_hour_average.index(lowest_period_next_24h)/2))
	msg = "in:"+str(minterval)+"hrs"

	# and convert that to an actual time
	# note that this next time will not give you an exact half hour if you don't run this at an exact half hour eg cron
	# because it's literally just adding n * 30 mins!
	# could in future add some code to round to 30 mins increments but it works for now.

	min_offset = two_hour_average.index(lowest_period_next_24h) * 30
	time_of_cheapest = the_now_local + datetime.timedelta(minutes=min_offset)
	time_of_cheapest_formatted = (str(time_of_cheapest.time())[0:5])
	font = ImageFont.truetype(HankenGroteskMedium, 10)
	draw.text((0,third_row + 32), msg+" ("+time_of_cheapest_formatted+")", inky_display.BLACK, font)

else: #high res display

	font = ImageFont.truetype(FredokaOne, 72)
	message = "{0:.1f}".format(current_price) + "p"
	w, h = font.getsize(message)
	#x = (inky_display.WIDTH / 2) - (w / 2)
	#y = (inky_display.HEIGHT / 2) - (h / 2)
	x = 0
	y = -10

	if (current_price > red_threshold):
		draw.text((x, y), message, inky_display.RED, font)
	else:
		draw.text((x, y), message, inky_display.BLACK, font)

	right_column = 0
	second_row = 75
	fourth_row = 150

	# NEXT
	message = "2:" + "{0:.1f}".format(next_price) + "p"
	font = ImageFont.truetype(FredokaOne, 23)
	w2, h2 = font.getsize(message)
	x = 0
	y = second_row
	if (next_price > red_threshold):
		draw.text((x,y), message, inky_display.RED, font)
	else:
		draw.text((x, y), message, inky_display.BLACK, font)

	# NEXT
	message = "3:" + "{0:.1f}".format(nextp1_price) + "p"
	font = ImageFont.truetype(FredokaOne, 23)
	w3, h3 = font.getsize(message)
	x = 0
	y = second_row + 23

	if (nextp1_price > red_threshold):
		draw.text((x,y), message, inky_display.RED, font)
	else:
		draw.text((x, y), message, inky_display.BLACK, font)

	# NEXT
	message = "4:" + "{0:.1f}".format(nextp2_price) + "p"
	font = ImageFont.truetype(FredokaOne, 23)
	w3, h3 = font.getsize(message)
	x = 0
	y = second_row + 46

	if (nextp2_price > red_threshold):
		draw.text((x,y), message, inky_display.RED, font)
	else:
		draw.text((x, y), message, inky_display.BLACK, font)

	pixels_per_h = 2.3  # how many pixels 1p is worth
	pixels_per_w = 3  # how many pixels 1/2 hour is worth
	chart_base_loc = 121  # location of the bottom of the chart on screen in pixels
	#chart_base_loc = 85  # location of the bottom of the chart on screen in pixels
	number_of_vals_to_display = 48 # 36 half hours = 18 hours

	# plot the graph
	#lowest_price_next_24h = min(i for i in prices if i > 0)
	lowest_price_next_24h = min(i for i in prices)
	if (lowest_price_next_24h < 0):
		chart_base_loc = 104 + lowest_price_next_24h*pixels_per_h - 2 # if we have any negative prices, shift the base of the graph up! 

	print("lowest price Position:", prices.index(lowest_price_next_24h))
	print("low Value:", lowest_price_next_24h)

	# go through each hour and get the value

	for i in range(0,number_of_vals_to_display):
		if prices[i] < 999:
			scaled_price = prices[i] * pixels_per_h # we're scaling it by the value above

			if prices[i] <= (lowest_price_next_24h + 1):   # if within 1p of the lowest price, display in black
				ink_color = inky_display.BLACK
			else:
				ink_color = inky_display.RED

			# takes a bit of thought this next bit, draw a rectangle from say x =  2i to 2(i-1) for each plot value
			# pixels_per_w defines the horizontal scaling factor (2 seems to work)
			draw.rectangle((pixels_per_w*i,chart_base_loc,((pixels_per_w*i)-pixels_per_w),(chart_base_loc-scaled_price)),ink_color)

	#draw minimum value on chart  <- this doesn't seem to work yet
	# font = ImageFont.truetype(FredokaOne, 15)
	# msg = "{0:.1f}".format(lowest_price_next_24h) + "p"
	# draw.text((4*(minterval-1),110),msg, inky_display.BLACK, font)

	# draw the bottom right min price and how many hours that is away
	font = ImageFont.truetype(FredokaOne, 16)
	msg = "min:"+"{0:.1f}".format(lowest_price_next_24h) + "p"
	draw.text((right_column,69), msg, inky_display.BLACK, font)
	# we know how many half hours to min price, now figure it out in hours.
	minterval = (round(prices.index(lowest_price_next_24h)/2))
	print ("minterval:"+str(minterval))
	msg = "in:"+str(minterval)+"hrs"
	draw.text((right_column,85), msg, inky_display.BLACK, font)

	# and convert that to an actual time
	# note that this next time will not give you an exact half hour if you don't run this at an exact half hour eg cron
	# because it's literally just adding n * 30 mins!
	# could in future add some code to round to 30 mins increments but it works for now.

	min_offset = prices.index(lowest_price_next_24h) * 30
	time_of_cheapest = the_now_local + datetime.timedelta(minutes=min_offset)
	print("cheapest at " + str(time_of_cheapest))
	print("which is: "+ str(time_of_cheapest.time())[0:5])
	time_of_cheapest_formatted = "at " + (str(time_of_cheapest.time())[0:5])
	font = ImageFont.truetype(FredokaOne, 16)
	draw.text((right_column,101), time_of_cheapest_formatted, inky_display.BLACK, font)

# render the actual image onto the display
inky_display.set_image(img.rotate(90, expand=True))
inky_display.show()
print('Drawn')
exit(0)