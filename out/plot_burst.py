import numpy as np
import matplotlib.pyplot as plt
#import plotfil.sp_spec as sp



dat = np.fromfile("test.dat", dtype="f4")
print(len(dat))
print(np.argmax(dat))
print(np.max(dat))
print(np.mean(dat))

time_interval = 1e-6
num_points = len(dat)
time_data = np.arange(num_points) * time_interval

plt.plot(time_data, dat)
plt.savefig("test.png")


debug = 0

if __name__ == "__main__":
    if not debug: 
        #plot_bursts()
        print()

