import time


if __name__ == "__main__":

    start = int(time.time()*1000)

    for x in range(100000000):

        pass

    end = int(time.time()*1000)

    print (end-start)