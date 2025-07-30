import random
from collections import deque
def cmd_minesweeping(a = 0, b = 0, c = 1):
    while a * b <= c:
        try:
            a, b, c = map(int,input("请输入行数，列数以及雷数：").split())
            if a * b <= c:
                print("雷太多了")
        except:
            print("你的输入有误，请再输一次")
            continue
    sizex = a
    sizey = b
    setbomb = c
    mp = [['.' for _ in range(sizey)] for _ in range(sizex)]
    bomb = [[0 for _ in range(sizey)] for _ in range(sizex)]
    # for i in mp:
    #     for j in i:
    #         print(j,end=" ")
    #     print()

    first_time = 1

    num_of_bomb = setbomb
    while(num_of_bomb > 0):
        try:
            x, y, z = map(int,input("请输入行，列，检测雷(1)或标记雷(2)：").split())
            x -= 1
            y -= 1
            if z != 1 and z != 2:
                print("你的输入有误，请再输一次")
                continue
            print()
            if mp[x][y] != '.':
                print("此格已被打开，请再输一次")
                continue

            if first_time == 1:
                labelnum = setbomb
                while(labelnum > 0):
                    xi = random.randint(0, sizex - 1)
                    yi = random.randint(0, sizey - 1)
                    if bomb[xi][yi] == 1 or (x == xi and y == yi):
                        continue
                    bomb[xi][yi] = 1
                    labelnum -= 1
                first_time = 0

            if (bomb[x][y] == 1 and z == 1) or (bomb[x][y] == 0 and z == 2):
                print("Game Over!")
                print("   ",end="")
                for i in range(1,sizey + 1):
                    print(i,end=" ")
                print()
                for i in range(sizex):
                    print(i + 1,end=" ")
                    if(i + 1 < 10):
                        print(" ",end="")
                    for j in range(sizey):
                        if bomb[i][j] == 1:
                            print('B',end=" ")
                        else:
                            print(mp[i][j],end=" ")
                    print()
                break

            print("   ",end="")
            for i in range(1,sizey + 1):
                print(i,end=" ")
            print()

            if bomb[x][y] == 1 and z == 2:
                mp[x][y] = 'B'
                num_of_bomb -= 1
                for i in range(sizex):
                    print(i + 1,end=" ")
                    if(i + 1 < 10):
                        print(" ",end="")
                    for j in range(sizey):
                        print(mp[i][j],end=" ")
                    print()
                print("剩余雷数：" + str(num_of_bomb))
                continue

            qx = deque()
            qy = deque()
            qx.append(x)
            qy.append(y)
            side = [-1,0,1]

            while len(qx) != 0:
                x = qx.popleft()
                y = qy.popleft()
                counts = 0
                for i in side:
                    if x + i < 0 or x + i > sizex - 1:
                        continue
                    for j in side:
                        if y + j < 0 or y + j > sizey - 1:
                            continue
                        if bomb[x + i][y + j] == 1:
                            counts += 1

                mp[x][y] = counts

                if counts == 0:
                    for i in side:
                        if x + i < 0 or x + i > sizex - 1:
                            continue
                        for j in side:
                            if y + j < 0 or y + j > sizey - 1:
                                continue
                            if bomb[x + i][y + j] != 1 and mp[x + i][y + j] == '.':
                                qx.append(x + i)
                                qy.append(y + j)
                

            
            for i in range(sizex):
                print(i + 1,end=" ")
                if(i + 1 < 10):
                    print(" ",end="")
                for j in range(sizey):
                    print(mp[i][j],end=" ")
                print()
            print("剩余雷数：" + str(num_of_bomb))

        except:
            print("你的输入有误，请再输一次")
            continue

    if num_of_bomb == 0:
        print("You win!")
        


