import os
import glob
import time
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

#importing the library that is used to be able to communicate with Raspberry Pi (and sensors attached to it)
import RPi.GPIO as GPIO
import time
 
count = 0
#GPIO SETUP
channel = 21 #using GPIO 21 pin to connect soil moisture sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
sendNotification=0
 
def callback(channel):
        global count, sendNotification
        if GPIO.input(channel):
                print("No Moisture Detected!")
                count = count+1
                print(count)
                if count==3 and sendNotification==0:
                    sendNotification=1
		    #Takepicture()
                    emailSent(sendNotification)
                    print("Mail about needing to water plant sent.")
        else:
                print("Moisture Detected!")
                count = 0
 
GPIO.add_event_detect(channel, GPIO.BOTH)  #lets us know when the pin goes HIGH or LOW
GPIO.add_event_callback(channel, callback)  #assign function to GPIO PIN, Run function on change
print(count)

#code to detect temperature using the on-board temperature sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')
device_file = device_folder[0]+ '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

#sends email from one specified Gmail account (with attachments) to another
def emailSent(sendNotification):
    import smtplib 
    from email.mime.multipart import MIMEMultipart 
    from email.mime.text import MIMEText 
    from email.mime.base import MIMEBase 
    from email import encoders 
     
    #for privacy purposes, a made up email address has been entered below
    fromaddr = "hello@gmail.com"
    toaddr = "hello@gmail.com"
       
    #instance of MIMEMultipart 
    msg = MIMEMultipart() 
      
    #storing the senders email address   
    msg['From'] = fromaddr 
      
    #storing the receivers email address  
    msg['To'] = toaddr 
      
    #storing the subject  
    msg['Subject'] = "Plant details with moisture update"
      
    #string to store the body of the mail 
    body = "This is your plant" + ".  The current temperature is : "+str(read_temp())+"."
    if sendNotification==1:
        body=body+"Low moisture...Please water your plant."
      
    #attach the body with the msg instance 
    msg.attach(MIMEText(body, 'plain')) 
      
    #open the file to be sent  
    filename = "Plant.jpg"
    attachment = open("/home/pi/Plant.jpg", "rb") 
      
    #instance of MIMEBase and named as p 
    p = MIMEBase('application', 'octet-stream') 
      
    #To change the payload into encoded form 
    p.set_payload((attachment).read()) 
      
    #encode into base64 
    encoders.encode_base64(p) 
       
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
      
    #attach the instance 'p' to instance 'msg' 
    msg.attach(p) 
      
    #creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
      
    #start TLS for security 
    s.starttls() 
      
    #Authentication 
    s.login(fromaddr, "password") 
      
    #Converts the Multipart msg into a string 
    text = msg.as_string() 
      
    #sending the mail 
    s.sendmail(fromaddr, toaddr, text) 
      
    #terminating the session 
    s.quit()

#code that makes use of a camera attached to Raspberry Pi to take a picture of the plant
def Takepicture():
        import picamera
        
        print("Capturing")
        camera = picamera.PiCamera()
        camera.capture("Plant.jpg")
        
        print("Done")

while True:
    print(str(read_temp()))
    time.sleep(1)
    
