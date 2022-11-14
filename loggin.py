import threading

n = 0
finish = True
def counter(c):
    finish = False
    c = c + 1
    print(c)
    finish = True


while True:
    if(finish):
        thread1 = threading.Thread(target=counter, args=(n,))
        thread1.start()