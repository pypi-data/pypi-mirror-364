import random
import keyboard
import os


def cmd_2048():
    mp = [['.' for _ in range(4)] for _ in range(4)]
    wall = [[0 for _ in range(4)] for _ in range(4)]

    while(1):
        xi = random.randint(0, 3)
        yi = random.randint(0, 3)
        if mp[xi][yi] == '.':
            yi = random.randint(0, 3)
            z = random.randint(0, 99)
            if z >= 90:
                mp[xi][yi] = 4
            else:
                mp[xi][yi] = 2
            break

    score = 0
    while(1):
        wall = [[0 for _ in range(4)] for _ in range(4)]
        
        while(1):
            xi = random.randint(0, 3)
            yi = random.randint(0, 3)
            if mp[xi][yi] == '.':
                z = random.randint(0, 99)
                if z >= 90:
                    mp[xi][yi] = 4
                else:
                    mp[xi][yi] = 2
                break

        for i in mp:
            for j in i:
                ed = (5 - len(str(j))) * " "
                print(j,end=ed)
            print()
        print("score:" + str(score))

        finished = 1
        for j in range(0,4):
            for i in range(1,4):
                if mp[i][j] != '.' and wall[i][j] == 0:
                    if mp[i - 1][j] == mp[i][j] and wall[i - 1][j] == 0:
                        finished = 0
                    elif mp[i - 1][j] == ".":
                        finished = 0

        for j in range(0,4):
            for i in range(2,-1,-1):
                if mp[i][j] != '.' and wall[i][j] == 0:
                    if mp[i + 1][j] == mp[i][j] and wall[i + 1][j] == 0:
                        finished = 0
                    elif mp[i + 1][j] == ".":
                        finished = 0

        for j in range(0,4):
            for i in range(1,4):
                if mp[j][i] != '.' and wall[j][i] == 0:
                    if mp[j][i - 1] == mp[j][i] and wall[j][i - 1] == 0:
                        finished = 0
                    elif mp[j][i - 1] == ".":
                        finished = 0

        for j in range(0,4):
            for i in range(2,-1,-1):
                if mp[j][i] != '.' and wall[j][i] == 0:
                    if mp[j][i + 1] == mp[j][i] and wall[j][i + 1] == 0:
                        finished = 0
                    elif mp[j][i + 1] == ".":
                        finished = 0

        if finished:
            break

        nxt = 1
        while(nxt == 1):
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == 'up':
                    for j in range(0,4):
                        move = 1
                        while move == 1:
                            move = 0
                            for i in range(1,4):
                                if mp[i][j] != '.' and wall[i][j] == 0:
                                    if mp[i - 1][j] == mp[i][j] and wall[i - 1][j] == 0:
                                        mp[i - 1][j] = 2 * mp[i][j]
                                        score += 2 * mp[i][j]
                                        mp[i][j] = '.'
                                        wall[i - 1][j] = 1
                                        nxt = 0
                                        move = 1
                                        os.system('cls')

                                    elif mp[i - 1][j] == ".":
                                        mp[i - 1][j] = mp[i][j]
                                        mp[i][j] = '.'
                                        move = 1
                                        nxt = 0
                                        os.system('cls')

                elif event.name == 'down':
                    for j in range(0,4):
                        move = 1
                        while move == 1:
                            move = 0
                            for i in range(2,-1,-1):
                                if mp[i][j] != '.' and wall[i][j] == 0:
                                    if mp[i + 1][j] == mp[i][j] and wall[i + 1][j] == 0:
                                        mp[i + 1][j] = 2 * mp[i][j]
                                        score += 2 * mp[i][j]
                                        mp[i][j] = '.'
                                        wall[i + 1][j] = 1
                                        move = 1
                                        nxt = 0
                                        os.system('cls')

                                    elif mp[i + 1][j] == ".":
                                        mp[i + 1][j] = mp[i][j]
                                        mp[i][j] = '.'
                                        move = 1
                                        nxt = 0
                                        os.system('cls')

                elif event.name == 'left':
                    for j in range(0,4):
                        move = 1
                        while move == 1:
                            move = 0
                            for i in range(1,4):
                                if mp[j][i] != '.' and wall[j][i] == 0:
                                    if mp[j][i - 1] == mp[j][i] and wall[j][i - 1] == 0:
                                        mp[j][i - 1] = 2 * mp[j][i]
                                        score += 2 * mp[j][i]
                                        mp[j][i] = '.'
                                        wall[j][i - 1] = 1
                                        nxt = 0
                                        move = 1
                                        os.system('cls')

                                    elif mp[j][i - 1] == ".":
                                        mp[j][i - 1] = mp[j][i]
                                        mp[j][i] = '.'
                                        move = 1
                                        nxt = 0
                                        os.system('cls')

                elif event.name == 'right':
                    for j in range(0,4):
                        move = 1
                        while move == 1:
                            move = 0
                            for i in range(2,-1,-1):
                                if mp[j][i] != '.' and wall[j][i] == 0:
                                    if mp[j][i + 1] == mp[j][i] and wall[j][i + 1] == 0:
                                        mp[j][i + 1] = 2 * mp[j][i]
                                        score += 2 * mp[j][i]
                                        mp[j][i] = '.'
                                        wall[j][i + 1] = 1
                                        nxt = 0
                                        move = 1
                                        os.system('cls')

                                    elif mp[j][i + 1] == ".":
                                        mp[j][i + 1] = mp[j][i]
                                        mp[j][i] = '.'
                                        move = 1
                                        nxt = 0
                                        os.system('cls')
            
    print("Game Over!")
                    
