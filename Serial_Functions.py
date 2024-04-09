import serial


# Open the COM port
def open_serial_port(comm, baudrate):
    ser = serial.Serial(comm, baudrate)
    return ser
    
def close_serial_port(ser):
    ser.flushInput()
    ser.flushOutput()
    ser.close()


def calculate_speed(data):
    # Step 1: Acquire & store the 4th and 5th bytes of data
    byte4 = data[3]
    byte5 = data[4]
    
    # Calculate speed value
    speed_value = (byte4 * 128) + byte5
    
    return speed_value

def calculate_torque(data, calibration_figure, torque_offset, calibration_range):
    # Step 1: Acquire & store the 1st 3 bytes of data
    byte1 = data[0]
    byte2 = data[1]
    byte3 = data[2]

    # Step 2: Subtract 128 from the 1st byte
    byte1 -= 128
    # Step 3: Calculate the intermediate result
    intermediate_result = (byte1 * 16384) + (byte2 * 128) + byte3
    
    # Step 4: Make the data bipolar if needed
    if intermediate_result > 1048576:
        intermediate_result = 0 - intermediate_result
    # Step 5: Divide by 10,000 to get mV/V
    mV_V = intermediate_result / 10000
    
    # Step 6: Calculate the torque
    torque = round((((mV_V / calibration_figure) * calibration_range ) + torque_offset), 2)

    return torque


def read_arduino(ser):
    try:
        line = ser.readline().decode()
        line = line.strip()
        
    except:
        line = "Error"
    return line

def read_datum(ser):
    data = ser.read(12)
    index = find_byte_with_msb(data)
    if index == -1:
        print("Error")
        data_result = 0
    else :
        data_result = data[index:index + 5]
    return data_result


def find_byte_with_msb(data):
    for i in range(len(data)):
        if data[i] & 0x80:  # Check if MSB (Most Significant Bit) is 1
            return i  # Return the index of the first byte with 1 in MSB
    return -1  # Return -1 if no such byte is found