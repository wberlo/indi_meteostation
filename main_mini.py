
import time
import mlx90614
import BME280
from machine import I2C, Pin, RTC
import math

i2c = I2C(scl=Pin(5), sda=Pin(4), freq = 100000)
irsensor = mlx90614.MLX90614(i2c)
meteosensor = BME280.BME280(i2c=i2c)
rtc = RTC()

def DateTime2Str(dt):
    ymd = str(dt[0]) + '/' + str(dt[1])
    if (dt[2] < 10):
        ymd = ymd + '/0' + str(dt[2])
    else:
        ymd = ymd + '/' + str(dt[2])
    if (dt[4] < 9):
       hms = '0' + str(dt[4] + 1) + ':'
    else: 
        hms = str(dt[4] + 1) + ':'
    if (dt[5] < 10):
        hms = hms + '0' + str(dt[5]) + ':'
    else: 
        hms = hms + str(dt[5]) + ':'
    if (dt[6] < 10):
        hms = hms + '0' + str(dt[6])
    else: 
        hms = hms + str(dt[6])

    str_date_time = ymd + ' ' + hms
    return str_date_time

def DewPoint(tc, rh):
    hh = (math.log10(rh) - 2)/0.4343 + (17.62*tc)/(243.12 + tc)
    td = (243.12*hh) / (17.62 - hh)
    return td

def sgn(x):
    if (x > 0):
        return 1
    elif (x < 0):
        return -1
    else:
        return 0

def Tsky(Ta, Ti):
    K1 = 33
    K2 = 0
    K3 = 4
    K4 = 100
    K5 = 100
    
    Td = (K1/100)*(Ta - K2/10) + (K3/100)*pow((K4/1000*Ta), K5/100)
    return Ti - Td
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    t,p,h = meteosensor.read_compensated_data()
    t = t / 100
    p = p / 256
    p = p / 100
    h = h / 1024
    dewp = DewPoint(t, h)
    ir_a = irsensor.read_ambient_temp()
    ir_o = irsensor.read_object_temp()
    # limits for cloud is similar to AAG cloud watcher
    # does this work in sub 0 temperature?
    T_sky = Tsky(ir_a, ir_o)
    if (T_sky < -13.):
        clouds = 0
    elif (T_sky < 0):
        clouds = (13. + T_sky)/13
    else:
        clouds = 1
    clouds = clouds * 100
    tnow = rtc.datetime()
    strTimestamp = DateTime2Str(tnow)
    bme_t = '{0:.1f}'.format(t)
    bme_p = '{0:.0f}'.format(p)
    bme_h = '{0:.0f}'.format(h)
    bme_dp = '{0:.1f}'.format(dewp)
    ir_clouds = '{0:.0f}'.format(clouds)

    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.send('dataTime=' + strTimestamp +'\n')
    conn.send('temp=' + bme_t +'\n')
    conn.send('rain=0.00\n')
    conn.send('pressure=' + bme_p +'\n')
    conn.send('humidity=' + bme_h +'\n')
    conn.send('dewpoint=' + bme_dp +'\n')
    conn.send('clouds=' + ir_clouds +'\n')
    conn.send('wind=1.50\n')
    conn.close()
    time.sleep(5)