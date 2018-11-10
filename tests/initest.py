from configparser import ConfigParser

point_system = input("Point Syster\n>")
p_ini = ConfigParser()
p_ini.read('../point_system.ini')
print(p_ini.sections())
if point_system not in p_ini.sections():
    point_system = 'default'
    print("Point system not found.")

print("Using", point_system)
point_table = {}
for pos in p_ini[point_system]:
    point_table[pos] = int(p_ini[point_system][pos])
