#####################################################

# PCA Constants File
# More info: https://www.nxp.com/docs/en/data-sheet/PCA9956B.pdf
# Taken from PCA9956b.h

#####################################################

# i2c Addresses of driver ICs
ADDR1=0x05
ADDR2=0x0B
ADDR3=0x65
ADDR4=0x69

# Read/write Control with address
ADDR_READ=0x01
ADDR_WRITE=0x00

# Control registers addresses to read
CTRL_NO_AIF=0x00
CTRL_AIF=0x80

# Register addresses
MODE1=0x00
MODE2=0x01
LEDOUT0=0x02
LEDOUT1=0x03
LEDOUT2=0x04
LEDOUT3=0x05
LEDOUT4=0x06
LEDOUT5=0x07
GRPFREQ=0x09
OFFSET=0x3A
SUBADR1=0x3B
SUBADR2=0x3C
SUBADR3=0x3D
ALLCALLADR=0x3E
PWMALL=0x3F
IREFALL=0x40
PWM0=0x0A
PWM23=0x21

# Register values
MODE1_DATA=0b10100000 # auto increment on LED PWM registers, no subaddresses
LEDOUT_PWM=0b10101010 # LEDs controlled by PWM Registers
LEDOUT_ON=0b01010101 # LEDs always full on

# CURRENT VALUES to set
# Refer to page 24 graph, Example 2
# On the datasheet: https://www.nxp.com/docs/en/data-sheet/PCA9956B.pdf
IREFALL_4MA=0x10
IREFALL_7MA=0x20
IREFALL_10MA=0x27
IREFALL_15MA=0x40
IREFALL_22MA=0x60
IREFALL_30MA=0x80
IREFALL_40MA=0xAF
IREFALL_60MA=0xFF