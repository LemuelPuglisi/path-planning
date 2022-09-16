import math

OBS_W = 50      # obstacle width (draw reference system)
OBS_H = 50      # obstacle height (draw reference system)

CNT_W = 50      # container width (draw reference system)
CNT_H = 50      # container height (draw reference system)

SCALE = 1000    # 1 pixel is 0.001 m in the simulation

PANEL_W=950     # drawing panel width (draw r.s.)
PANEL_H=550     # drawing panel height (draw r.s.)

DP_ROBOT_PIC_PATH = '/../../assets/icons/robot.png'
DP_OBSTACLE_PIC_PATH = '/../../assets/icons/bedrock.png'
DP_ITEM_PIC_PATH = '/../../assets/icons/diamond.png'
DP_CONTAINER_PIC_PATH = '/../../assets/icons/chest.png'

#-----------------------
# PHIDIAS integration.
#-----------------------

PHIDIAS_HANDLER_PORT = 6566

#-----------------------
# convenience constants.
#-----------------------

TWOPI = math.pi * 2