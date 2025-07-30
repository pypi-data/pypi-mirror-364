# Keys
PH = "ph"
CPH = "cph"
ORP = "orp"
CORP = "corp"
PPM = "ppm"
CPPM = "cppm"
WARN = "warn"
ALARM = "alarm"
TEMP = "temp"
MAN_AUTO = "man_auto"
CORP_MAN = "corp_man"
V_CELL = "v_cell"
I_CELL = "i_cell"
SALT = "salt"
RELAYS = "relays"


keys = PH, CPH, ORP, CORP, PPM, CPPM, WARN, ALARM, TEMP, MAN_AUTO, CORP_MAN, V_CELL, I_CELL, SALT

# Commands
ph_cmd = b"\x3fp\x04"
cph_cmd = b"\x3fP\x04"
orp_cmd = b"\x3fo\x04"
corp_cmd = b"\x3fO\x04"
ppm_cmd = b"\x3fe\x04"
cppm_cmd = b"\x3fE\x04"
warn_cmd = b"\x3fw\x04"
alarm_cmd = b"\x3fA\x04"
temp_cmd = b"\x3fW\x04"
man_auto_cmd = b"\x3fm\x04"
corp_man_cmd = b"\x3fT\x04"
v_cell_cmd = b"\x3fV\x04"
i_cell_cmd = b"\x3fC\x04"
salt_cmd = b"\x3fN\x04"
relay_status_command = b'\x3fR\4'

commands = (ph_cmd, cph_cmd, orp_cmd, corp_cmd, ppm_cmd, cppm_cmd, warn_cmd, alarm_cmd, temp_cmd, man_auto_cmd,
            corp_man_cmd, v_cell_cmd, i_cell_cmd, salt_cmd)

# Multipliers
ph_multi = 0.01
cph_multi = 0.01
orp_multi = 1
corp_multi = 1
ppm_multi = 0.01
cppm_multi = 0.01
warn_multi = 1
alarm_multi = 1
temp_multi = 1
man_auto_multi = 1
corp_man_multi = 1
v_cell_multi = 1
i_cell_multi = 1
salt_multi = 1


multipliers = (ph_multi, cph_multi, orp_multi, corp_multi, ppm_multi, cppm_multi, warn_multi, alarm_multi, temp_multi,
               man_auto_multi, corp_man_multi, v_cell_multi, i_cell_multi, salt_multi)

# Relays

relay_names = ['relay1', 'relay2', 'relay3', 'relay4']


def base_parser(data: list, multiplier):
    """Basic sensor parser"""
    result = '0'
    try:
        result = str((data[1] + (data[2] * 256)) * multiplier)
    except IndexError:
        print(f'Data: {data} has only 2 fiels!')
    return result

def single_parser(data: list, multiplier):
    """Single sensor parser"""
    return str(data[1])

def temp_parser(data: list, multiplier):
    """Temperature sensor parser"""
    return str(abs(data[1]) if data[2] == 1 else data[1])

def bit_parser(data, multiplier):
    status_byte = data[1]
    status_bits = f"{status_byte:08b}"
    relay_mode = [bool(int(status_bits[i])) for i in [6, 4, 2, 0]]
    relay_status = [bool(int(status_bits[i])) for i in [7, 5, 3, 1]]
    return [{'is_active': value} for value in relay_status], [{'is_active': value} for value in relay_mode]


parsers = (base_parser, base_parser, base_parser, base_parser, base_parser,
           base_parser, single_parser, single_parser, temp_parser, single_parser,
           single_parser, base_parser, single_parser, base_parser)