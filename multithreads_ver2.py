import bpy
import random
import serial
import time
import queue
import multiprocessing
import threading
import sys

class myThread(threading.Thread):
    # Thread for reading the usb port and adding to the queue 
    _ser = None
    _open = None
    def __init__(self,name,q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q   
    def addBuffer1(self):
        try:
            if self._open == None:
                self.setup1()
                open = 1
                print("opened ser")
            #print("add buffer")
            quit = 0
            ctr = 0
            tempA = 0
            defA, defB, defC = None, None, None
            s = threading.currentThread()
            while getattr(s,"do_run", True): # waits for the event for the blender window
                try:
                    line = self._ser.readline()
                    line = line.decode('utf-8')
                    line = line.strip('\r\n')
                    line = line.split('\t')
                    print(line)
                    if len(line) == 4:
                        qlock.acquire()
                        a = float(line[1])
                        b = float(line[2])
                        c = float(line[3])
                        if ctr < 5:
                            print("aasi")
                            if (a == tempA):
                                ctr += 1
                                print(ctr)
                            else:
                                #print("else ctr")
                                ctr = 0
                            tempA = a
                            if ctr == 5:
                                defA, defB, defC = float(a), float(b), float(c)
                                ctr = 6
                                print("YAW alustettu")
                        if defA:
                            if a > defA + 30 or a < defA - 30 or b > defB + 30 or b < defB - 30 or c > defC + 30 or c < defC - 30:
                                #print(line)
                                q.put(line)
                    #print(line)
                    #q.put(line)
                        qlock.release()
                except UnicodeError:
                    print("unicode error")
                    continue
                except ValueError:
                    print("value error")
                    continue
                except KeyboardInterrupt:
                    print("KeyboardInterrupt!!!!")
                    
                    #ser.close()
                    quit = 1
                #finally:
                #    ser.close()
        except serial.serialutil.SerialException: # FileNotFoundError
            #closeSerial()
            #ser.close()
            print("Serial error!!")
        #ser.close()
    def setup1(self):
        # setup the serial connection
        self.openSerial()
        time.sleep(3)
        try:
            self._ser.write(str.encode('A')) # the arduino waits for a character to start sending data
            print("lähetys alko?")
        except :
            print("error")
        print("calibrating")
        time.sleep(10) # waits for 10 seconds so that the accelerometer values normalise
        print("done calibrating")

    def openSerial(self):
        #global ser
        # open serial connection
        self._ser = serial.Serial('/dev/ttyACM0',115200)
    def closeSerial(self):
        #global ser
        self._ser.close()

    def run(self):
        self.addBuffer1()

class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    limits = bpy.props.IntProperty(default=0)
    _timer = None
    #_ser = None
    
    #_r1 = None
    #_y1 = None
    #_p1 = None
    #_open = None
    #_defA, _defB, _defC = None, None, None
    #_queue = queue.Queue(100)
 
    def rotateObject(self):
        #try:
        obj = bpy.context.active_object
        #print("rota")
        if not p.q.empty():
            #print("ting")
            qlock.acquire()
            line = p.q.get();
            a = float(line[1])
            b = float(line[2])
            c = float(line[3])
            pi = 3.14159265358979
            qlock.release()
            #obj.rotation_euler = (b , c , a)
            
            
            if a > obj.rotation_euler.z + 30:
     #           rotation.append("+a")
                obj.rotation_euler.z -= pi/16
                #pass
                           
            if a < obj.rotation_euler.z - 30:
    #            rotation.append("-a")       
                obj.rotation_euler.z += pi/16
                #pass
                    
            if b > obj.rotation_euler.x + 30:
                #rotation.append("+b") 
                obj.rotation_euler.x += pi/16
                #pass     
            if b < obj.rotation_euler.x - 30:
                #rotation.append("-b")
                obj.rotation_euler.x -= pi/16
                #pass
                    
            if c > obj.rotation_euler.y + 30:
                #rotation.append("+c") 
                obj.rotation_euler.y += pi/16     
                #pass
            if c < obj.rotation_euler.y - 30:
                #rotation.append("-c")
                obj.rotation_euler.y -= pi/16
                #pass
            
            #time.sleep(0.1)
        #bpy.ops.transform.rotate(value=0.283/8, axis=(0,0,1))
        #except KeyboardInterrupt:

    def modal(self, context, event):
        
        if event.type in {'RIGHTMOUSE', 'ESC'} or self.limits > 30:
            self.limits = 0
            self.cancel(context)
            print("done")
            p.do_run = False
            p.closeSerial()
            p.join()
            quit = 1
            return {'FINISHED'}

        if event.type == 'TIMER':
            self.rotateObject()

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(time_step=0.01, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        


def register():
    bpy.utils.register_class(ModalTimerOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)


if __name__ == "__main__":
    register()
    #global q
    #global p
    qlock = threading.Lock() # thread lock
    q = queue.Queue() # the queue
    p = myThread('aasithread',q) # create the thread
    p.start()
    #p.join()
    print("avattu")
    # test call
    bpy.ops.wm.modal_timer_operator()