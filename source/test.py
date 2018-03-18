import time

def recursiveTest(n, depth):
	if depth <= 0:
		return
	for i in range(n):
		recursiveTest(n, depth-1)

originTime = time.time()
print(originTime)
print(str(time.localtime().tm_hour) + ":" + str(time.localtime().tm_min) + ":" + str(time.localtime().tm_sec))



recursiveTest(25, 7)

#6 = 36
#7 = 1064

print(str(time.localtime().tm_hour) + ":" + str(time.localtime().tm_min) + ":" + str(time.localtime().tm_sec))
print(time.time())
print("Total Time (sec):")
print(time.time() - originTime)