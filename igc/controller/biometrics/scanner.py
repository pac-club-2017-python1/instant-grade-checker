import time

import fingerpi as fp


def enroll():
    f = fp.FingerPi()
    f.Open(extra_info=True, check_baudrate=True)
    f.ChangeBaudrate(115200)
    print "Put your fingerprint on the scanner"
    f.CmosLed(True)

    while not isFingerPressed(f):
        time.sleep(1)
    id = int(f.GetEnrollCount()[0]["Parameter"]) + 1
    f.DeleteId(id)

    #Enroll Start
    enrollStart = f.EnrollStart(id)
    print "Using ID: " + str(id)
    print "Enroll Start done " + str(enrollStart)

    #Capture Finger
    f.CaptureFinger(best_image=True)
    time.sleep(1)

    #Enroll 1
    enroll1 = f.Enroll1()
    print "Enroll 1 done " + str(enroll1)

    #Wait using fingerPressed
    while not isFingerPressed(f):
        time.sleep(1)

    #Capture Finger
    f.CaptureFinger(best_image=True)
    time.sleep(1)

    #Enroll 2
    enroll2 = f.Enroll2()
    print "Enroll 2 done " + str(enroll2)

    #Wait using fingerPressed
    while not isFingerPressed(f):
        time.sleep(1)

    #Capture Finger
    f.CaptureFinger(best_image=True)
    time.sleep(1)

    #Enroll 3
    enroll3 = f.Enroll3_()
    print "Enroll 3 done " + str(enroll3)

    f.CmosLed(False)
    print "Enrolled :" + str(f.GetEnrollCount()[0]["Parameter"])
    f.Close()

    if enroll3 and enroll3[0] and enroll3[0]["ACK"]:
        return bool(enroll3[0]["ACK"]), id
    else:
        return False, -100


def identify():
    f = fp.FingerPi()
    f.Open(extra_info=True, check_baudrate=True)
    #f.ChangeBaudrate(115200)
    print "Put your fingerprint on the scanner"
    f.CmosLed(True)

    times = 0
    while not isFingerPressed(f):
        time.sleep(1)
        times += 1

        if times > 10:
            break
    if times > 5:
        f.CmosLed(False)
        return False, -1000

    f.CaptureFinger(best_image=False)
    f.CmosLed(False)
    ide = f.Identify()

    if ide and ide[0] and ide[0]["ACK"]:
        print bool(ide[0]["ACK"]), int(ide[0]["Parameter"])
        return bool(ide[0]["ACK"]), int(ide[0]["Parameter"])
    else:
        return False, -1000

def isFingerPressed(fp):
    return int(fp.IsPressFinger()[0]["Parameter"]) == 0