import os
import numpy as np
import cv2
import pyudev
import shutil

MNT="/mnt"
frame = None
def init_udev_monitor():

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block',device_type='partition')  # Remove this line to listen for all devices.
    monitor.start()
    return monitor



os.chdir("/root")
key = ["a","z","e","r","t","y","u","i","o","p"]

moviez = { key[i] : cv2.VideoCapture('movies/%i.mov'%(i+1)) for i in xrange(10) }
cap=moviez["a"]
current = "a"


def key_movie(k):
    global moviez
    global cap
    global current
    try:
        k=chr(k)
        if k in key and k != current:
            cap=moviez[k]
            current = k

    except ValueError:pass


def update_movies():
    global moviez
    global cap
    global current
    global key

    moviez = { key[i] : cv2.VideoCapture('/root/movies/%i.mov'%(i+1)) for i in xrange(10) }
    cap=moviez["a"]
    current = "a"

def dialog(msg):
    global frame
    
    cv2.rectangle(frame,(0,0),(1920,1080),(255,0,0), -1)
    text_color = (255,255,255)
    (w,h),x = cv2.getTextSize(msg,cv2.FONT_HERSHEY_SIMPLEX,3., 3)
    cv2.putText(frame,msg, ((1920-w)/2,(1080-h)/2), cv2.FONT_HERSHEY_SIMPLEX, 3., text_color, thickness=3)
    cv2.imshow("frame",frame)
    k=cv2.waitKey()
    try:
        k=chr(k)
        if k == 'a':
            return True
        return False
    except Exception,e:
        print "dialog ", str(e)

def check_for_update():
    try:
        f=open("%s/update.txt"%MNT)
        count=0
        lst=[]
        for f in os.listdir("%s/movies"%MNT):
            if f[-4:]==".mov":
                count+=1
                lst.append(f)

        msg="Got %d files : Press A to update...."%count
        if dialog(msg):
            [shutil.copyfile("%s/movies/%s"%(MNT,f),"/root/movies/%s"%f) for f in lst]
            msg="copied %d file : press any key"%count
            dialog(msg)
            update_movies()

        else:
            dialog("canceled : press any key")



    except Exception,e:
        print e

def handle_usb_key(dev):#,frame):
    global MNT
    global frame
    if dev.action == "add":
       ret=os.system("mount %s %s"%(dev.device_node,MNT))
       if ret==0:
            check_for_update()
            os.system("umount %s"%dev.device_node)

monitor = init_udev_monitor()

while True:
    ret, frame = cap.read()
    position=cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)	
    tot_frame=cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
    
    cv2.imshow('frame',frame)
    for e in [cv2.waitKey(33), monitor.poll(0.001)]:
        if type(e) == int:
           key_movie(e)
        if type(e) == pyudev.device.Device:
            print "UDEV", e.device_node
            handle_usb_key(e)#,frame)
    	

    
    if position >= tot_frame - 1:
        #print "looping"
        cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)

for k, v in moviez.items():
	v.release() 
cv2.destroyAllWindows()
