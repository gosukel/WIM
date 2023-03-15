from win_ui_manager import WinWarehouse
# from lin_ui_manager import LinWarehouse
from sys import platform

print(platform)
if platform.lower() == "win32":
    print('running on windows')
    warehouse = WinWarehouse()


# elif platform.lower() == "linux": 
#     print('running on linux')
#     warehouse = LinWarehouse()
# else:
#     print('invalid os')
