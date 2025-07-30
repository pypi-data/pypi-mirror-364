import time
import random
import keyboard
import os
from collections import deque

def cmd_snake(x = 0, y = 0, z = 0):
    if x == 0 or y == 0:
        while 1:
            try:
                x, y = [int(i) for i in input("请输入地图长(>=8)和宽(>=8)：").split()]
                if x < 8 or y < 8:
                    continue
                break
            except:
                continue
    if z == 0:            
        while 1:
            try:
                z = int(input("请输入速度(1~5)："))
                if z < 1 or z > 5:
                    continue
                break
            except:
                continue
    mp = [['.' for _ in range(int(y))] for _ in range(int(x))]
    t = 0
    time_start = time.time()

    body = deque()
    head = (4,4)
    tail = (4,2)
    body.append(tail)
    body.append((4,3))
    body.append(head)
    mp[4][4] = 'O'
    mp[4][3] = 'o'
    mp[4][2] = 'o'

    while(1):
        xi = random.randint(0, int(x) - 1)
        yi = random.randint(0, int(y) - 1)
        if mp[xi][yi] == '.':
            mp[xi][yi] = '*'
            break

    direction = 'right'
    last = 'right'
    event = None
    score = 0
    while 1:
        os.system('cls')

        time_end = time.time()
        time_elapsed = time_end - time_start
        for i in mp:
            for j in i:
                print(j,end=" ")
            print()
        print("time:" + str(round(t, 2)) + " score:" + str(score))
        
        while time_elapsed < t:
            if keyboard.is_pressed('up') and last != 'down':
                direction = 'up'
            if keyboard.is_pressed('down') and last != 'up':
                direction = 'down'
            if keyboard.is_pressed('left') and last != 'right':
                direction = 'left'
            if keyboard.is_pressed('right') and last != 'left':
                direction = 'right'
            time_end = time.time()
            time_elapsed = time_end - time_start
        
        if direction == 'right':
            if mp[head[0]][(head[1] + 1) % int(y)] == '.' or tail == (head[0], (head[1] + 1) % int(y)):
                mp[tail[0]][tail[1]] = '.'
                body.popleft()
                tail = (body[0][0], body[0][1])
                mp[head[0]][head[1]] = 'o'
                mp[head[0]][(head[1] + 1) % int(y)] = 'O'
                head = (head[0], (head[1] + 1) % int(y))
                body.append(head)
                last = 'right'
            elif mp[head[0]][(head[1] + 1) % int(y)] == '*':
                score += z
                mp[head[0]][head[1]] = 'o'
                mp[head[0]][(head[1] + 1) % int(y)] = 'O'
                head = (head[0], (head[1] + 1) % int(y))
                body.append(head)
                while(1):
                    xi = random.randint(0, int(x) - 1)
                    yi = random.randint(0, int(y) - 1)
                    if mp[xi][yi] == '.':
                        mp[xi][yi] = '*'
                        break
                last = 'right'
            else:
                break

        if direction == 'left':
            lasth = head[1] - 1
            if head[1] - 1 < 0:
                lasth = int(y) - 1
            if mp[head[0]][lasth] == '.' or tail == (head[0], lasth):
                mp[tail[0]][tail[1]] = '.'
                body.popleft()
                tail = (body[0][0], body[0][1])
                mp[head[0]][head[1]] = 'o'
                mp[head[0]][lasth] = 'O'
                head = (head[0], lasth)
                body.append(head)
                last = 'left'
            elif mp[head[0]][lasth] == '*':
                score += z
                mp[head[0]][head[1]] = 'o'
                mp[head[0]][lasth] = 'O'
                head = (head[0], lasth)
                body.append(head)
                while(1):
                    xi = random.randint(0, int(x) - 1)
                    yi = random.randint(0, int(y) - 1)
                    if mp[xi][yi] == '.':
                        mp[xi][yi] = '*'
                        break
                last = 'left'
            else:
                break

        if direction == 'down':
            if mp[(head[0] + 1) % int(x)][head[1]] == '.' or tail == ((head[0] + 1) % int(x), head[1]):
                mp[tail[0]][tail[1]] = '.'
                body.popleft()
                tail = (body[0][0], body[0][1])
                mp[head[0]][head[1]] = 'o'
                mp[(head[0] + 1) % int(x)][head[1]]  = 'O'
                head = ((head[0] + 1) % int(x), head[1])
                body.append(head)
                last = 'down'
            elif mp[(head[0] + 1) % int(x)][head[1]]  == '*':
                score += z
                mp[head[0]][head[1]] = 'o'
                mp[(head[0] + 1) % int(x)][head[1]]  = 'O'
                head = ((head[0] + 1) % int(x), head[1])
                body.append(head)
                while(1):
                    xi = random.randint(0, int(x) - 1)
                    yi = random.randint(0, int(y) - 1)
                    if mp[xi][yi] == '.':
                        mp[xi][yi] = '*'
                        break
                last = 'down'
            else:
                break

        if direction == 'up':
            lasth = head[0] - 1
            if head[0] - 1 < 0:
                lasth = int(x) - 1
            if mp[lasth][head[1]] == '.' or tail == (lasth, head[1]):
                mp[tail[0]][tail[1]] = '.'
                body.popleft()
                tail = (body[0][0], body[0][1])
                mp[head[0]][head[1]] = 'o'
                mp[lasth][head[1]] = 'O'
                head = (lasth, head[1])
                body.append(head)
                last = 'up'
            elif mp[lasth][head[1]] == '*':
                score += z
                mp[head[0]][head[1]] = 'o'
                mp[lasth][head[1]] = 'O'
                head = (lasth, head[1])
                body.append(head)
                while(1):
                    xi = random.randint(0, int(x) - 1)
                    yi = random.randint(0, int(y) - 1)
                    if mp[xi][yi] == '.':
                        mp[xi][yi] = '*'
                        break
                last = 'up'
            else:
                break
            
        gap = 1 - z * 0.2
        if gap == 0:
            gap = 0.1

        t += gap

    print("Game Over!将在10秒后关闭……")
    time.sleep(10)