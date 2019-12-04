
import time
import mlx90614
import BME280
from machine import I2C, Pin, RTC
import math
rtc = RTC()
tnow = rtc.datetime()
ymd = str(tnow[0]) + str(tnow[1])
if (tnow[2] < 10):
    ymd = ymd + '0' + str(tnow[2])
else:
    ymd = ymd + str(tnow[2])
if (tnow[4] < 9):
    hms = '0' + str(tnow[4] + 1) + ':'
else: 
    hms = str(tnow[4] + 1) + ':'
if (tnow[5] < 10):
    hms = hms + '0' + str(tnow[5]) + ':'
else: 
    hms = hms + str(tnow[5]) + ':'
if (tnow[6] < 10):
    hms = hms + '0' + str(tnow[6])
else: 
    hms = hms + str(tnow[6])

str_date_time = ymd + '-' + hms
print(str_date_time)

oldmins = tnow[5]

i2c = I2C(scl=Pin(5), sda=Pin(4), freq = 100000)
irsensor = mlx90614.MLX90614(i2c)
meteosensor = BME280.BME280(i2c=i2c)

def DewPoint(tc, rh):
    hh = (math.log10(rh) - 2)/0.4343 + (17.62*tc)/(243.12 + tc)
    td = (243.12*hh) / (17.62 - hh)
    return td

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)


while True:
    tnow = rtc.datetime()
    ymd = str(tnow[0]) + str(tnow[1])
    if (tnow[2] < 10):
        ymd = ymd + '0' + str(tnow[2])
    else:
        ymd = ymd + str(tnow[2])
    if (tnow[4] < 9):
        hms = '0' + str(tnow[4] + 1) + ':'
    else: 
        hms = str(tnow[4] + 1) + ':'
    if (tnow[5] < 10):
        hms = hms + '0' + str(tnow[5]) + ':'
    else: 
        hms = hms + str(tnow[5]) + ':'
    if (tnow[6] < 10):
        hms = hms + '0' + str(tnow[6])
    else: 
        hms = hms + str(tnow[6])

    str_date_time = ymd + ' ' + hms
    newmins = -1
    if (newmins != oldmins):
    # update every minute
        oldmins = newmins
        file = open("index.html", "w")
        file.write('<html>\n<head><title>MeteoStation</title></head>\n<body>\n')
        ir_a = irsensor.read_ambient_temp()
        ir_o = irsensor.read_object_temp()
        # limits for cloud is similar to AAG cloud watcher
        # does this work in sub 0 temperature?
        if (ir_o < -8.):
            clouds = 0
        elif (ir_o < 0):
            clouds = (8. - ir_o)/8
        else:
            clouds = 1
        t,p,h = meteosensor.read_compensated_data()
        t = t / 100
        p = p / 256
        p = p / 100
        h = h / 1024
        dewp = DewPoint(t, h)
        file.write('timestamp=' + str_date_time + ' <br />\n')
        file.write('ir_ambient={0:.2f}'.format(ir_a) + ' <br />\n')
        file.write('ir_sky={0:.2f}'.format(ir_o) + ' <br />\n')
        file.write('forecast={0:.3f}'.format(clouds) + ' <br />\n')
        file.write('temperature={0:.2f}'.format(t) + ' <br />\n')
        file.write('pressure={0:.2f}'.format(p) + ' <br />\n')
        file.write('humidity={0:.2f}'.format(h) + ' <br />\n')
        file.write('dew_point={0:.2f}'.format(dewp) + ' <br />\n')
        file.write('</body>\n</html>\n')
        file.close()

    file = open("index.html", "r")
    response = file.read()
    file.close()
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
