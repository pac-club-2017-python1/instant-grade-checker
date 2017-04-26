import fingerpi as fp
f = fp.FingerPi()
f.Open(True, True)
f.CmosLed(True)
f.DeleteAll()
f.CmosLed(False)
f.Close()
