#!/usr/bin/python

import serial
import crcmod
import re
import MySQLdb
import httplib
import base64


store_in_influx = True
store_in_postgres = True

# influx data submit configuration
influx_host_port = "192.168.0.120:8086"
influx_db = "ELECTRICVALUES"
influx_user_password = "admin:Solenoide"
influx_use_credentials = True


ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=30, parity=serial.PARITY_NONE, rtscts=0)


if store_in_postgres:
  db = MySQLdb.connect("192.168.0.120","root","Solenoide", "ELECTRICVALUES")


obis_codemap = {
        "1-3:0.2.8":   "Comsume",
        "0-0:1.0.0":   "Date",
        "0-0:96.1.1":  "TEXT_MESSAGE",
        "1-0:1.8.1":   "POWERFAILURE_LOG",
        "1-0:1.8.2":   "Time",
    }

# define value parser, to give uniform parsed values
def parse_value(value):
    if len(value) == 13 and (value.endswith("W") or value.endswith("S")):
        return "20" + value[0:2] + "-" + value[2:4] + "-" + value[4:6] + " " + value[6:8] + ":" + value[8:10] + ":" + value[10:12]


    value = re.sub("^0*([1-9])", "\\1", value)
    value = re.sub("\*.*", "", value)
    return value

# initialize result value set, and some other helper variables
values = { }
found_start = False
found_end = False
full_message = "-"
mbus_device_type = "-"

while not found_end:

    while not found_start:
        raw_line = ser.readline()
        if raw_line.startswith('/'):
           found_start = True
           values["HEADER"] = raw_line.strip()
           full_message = raw_line
           print values["HEADER"]

    raw_line = ser.readline()

    fields = line.replace(")", "").split("(")

    extra_print_data = ""

    line = raw_line.strip()




    if line.startswith('!'):
        full_message = full_message + "!"
        inputchecksum = line[1:]
        found_end = True
    else:
        full_message = full_message + raw_line

    if fields[0] in obis_codemap:
        field_name = obis_codemap[fields[0]]

        if mbus_device_type == "3" and field_name.startswith("MBUS") and field_name.endswith("_VALUE"):
            mbus_postfix = "_GAS_M3"
        elif mbus_device_type == "<TODO:fill-in-proper-value-here>" and field_name.startswith("MBUS") and field_name.endswith("_VALUE"):
            mbus_postfix = "_WATER_M3"
        else:
            mbus_postfix = ""


        if len(fields) == 3 and len(fields[1]) == 13:
            values[field_name + "Date"] = parse_value(fields[1])
            extra_print_data = ", " + field_name + "Date = \"" + parse_value(fields[1]) +"\""
            values[field_name + mbus_postfix] = parse_value(fields[2])
        elif field_name.endswith("LOG"):
            values[field_name] = str(fields[1:])
        else:
            values[field_name] = parse_value(fields[1])

        if field_name.startswith("MBUS") and field_name.endswith("_DEVICE_TYPE"):
            mbus_device_type = values[field_name]

        print line + " --> " + field_name + mbus_postfix + " = \"" + values[field_name + mbus_postfix] + "\"" + extra_print_data
    else:
        print line

ser.close()

print "\n" + str(values) + "\n"

crc16_function = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)
calculated_checksum = '{0:0{1}X}'.format((crc16_function(full_message)), 4)
checksum_ok = (inputchecksum == calculated_checksum)

if not checksum_ok:
    print "CHECKSUM ERROR, expected " + calculated_checksum
    exit(1)

print "CHECKSUM OK\n"


  print("Influx post body:\n\n" + body)

  conn = httplib.HTTPConnection(influx_host_port)

  if influx_use_credentials:
    auth_header = { "Authorization": "Basic " + base64.b64encode(influx_user_password.encode('ascii')).decode('ascii') }
    conn.request('POST', '/write?db=' + influx_db, body, auth_header)
  else:
    conn.request('POST', '/write?db=' + influx_db, body)

  response = conn.getresponse()
  print("influx postresponse " + str(response.status) + "\n")


if store_in_postgres:
  # insert into sql database
  cursor = db.cursor()

  insert_result = cursor.execute("""INSERT INTO `ELECTRICVALUES` (`Comsume','Date','TEXT_MESSAGE','POWERFAILURE_LOG','Time') VALUES (%s,%s,%s,%s,%s,)""", (values['Comsume'], values['Date'], values['TEXT_MESSAGE'], values['POWERFAILURE_LOG'], values['Time'],  str(values)))

  print("inserted " + str(insert_result) + " rows in db\n")

  db.commit()
  db.close()

print ("\n---\n");
