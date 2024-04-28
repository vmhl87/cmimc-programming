import json
import sys
import game2dboard

bd = game2dboard.Board(8, 9)
bd.title = "Blotto Swarm Visualizer by kjljixx"
bd.grid_color = "DarkSlateBlue"
bd.cell_color = "LightCyan"
bd.cell_size = 65

f = open(sys.argv[1])
j = json.load(f)

game_num = 0
pos_num = 0

def on_key_press(keysym):
  global game_num
  global pos_num
  if keysym == "Up":
    game_num += 1
  if keysym == "Down":
    game_num -= 1
  if keysym == "Left":
    pos_num -= 1
  if keysym == "Right":
    pos_num += 1
  game_num = max(min(game_num, 4), 0)
  pos_num = max(min(pos_num, 99), 0)
  for y in range(9):
    index = y
    if(index % 3 == 0):
      bd[0][y] = "|" + str(j["history"][game_num]["history"][pos_num]["board"][0][index]) + "-" + str(j["history"][game_num]["history"][pos_num]["board"][1][index]) + "|"
    else:
      bd[0][y] = str(j["history"][game_num]["history"][pos_num]["board"][0][index]) + "-" + str(j["history"][game_num]["history"][pos_num]["board"][1][index])
  for x in range(8):
    index = x + 8
    if(index % 3 == 0):
      bd[x][8] = "|" + str(j["history"][game_num]["history"][pos_num]["board"][0][index]) + "-" + str(j["history"][game_num]["history"][pos_num]["board"][1][index]) + "|"
    else:
      bd[x][8] = str(j["history"][game_num]["history"][pos_num]["board"][0][index]) + "-" + str(j["history"][game_num]["history"][pos_num]["board"][1][index])
  for y in range(9):
    index = 23 - y
    if(index % 3 == 0):
      bd[7][y] = "|" + str(j["history"][game_num]["history"][pos_num]["board"][0][index]) + "-" + str(j["history"][game_num]["history"][pos_num]["board"][1][index]) + "|"
    else:
      bd[7][y] = str(j["history"][game_num]["history"][pos_num]["board"][0][index]) + "-" + str(j["history"][game_num]["history"][pos_num]["board"][1][index])
  for x in range(1, 8):
    index = 30 - x
    if(index % 3 == 0):
      bd[x][0] = "|" + str(j["history"][game_num]["history"][pos_num]["board"][0][index]) + "-" + str(j["history"][game_num]["history"][pos_num]["board"][1][index]) + "|"
    else:
      bd[x][0] = str(j["history"][game_num]["history"][pos_num]["board"][0][index]) + "-" + str(j["history"][game_num]["history"][pos_num]["board"][1][index])
  bd[2][3] = "Game #" + str(game_num + 1)
  bd[2][4] = "Day #" + str(pos_num + 1)
  bd[3][3] = "Score:" 
  bd[3][4] = str(j["history"][game_num]["history"][pos_num]["score"][0])
  bd[3][5] = str(j["history"][game_num]["history"][pos_num]["score"][1])
  bd[4][3] = "Castles:"
  if(pos_num > 0):
    bd[4][4] = str(j["history"][game_num]["history"][pos_num]["score"][0] - j["history"][game_num]["history"][pos_num - 1]["score"][0])
    bd[4][5] = str(j["history"][game_num]["history"][pos_num]["score"][1] - j["history"][game_num]["history"][pos_num - 1]["score"][1])
  else:
    bd[4][4] = str(j["history"][game_num]["history"][pos_num]["score"][0])
    bd[4][5] = str(j["history"][game_num]["history"][pos_num]["score"][1])


bd.on_key_press = on_key_press
on_key_press("")
bd.show()
