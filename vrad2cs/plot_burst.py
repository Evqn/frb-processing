import numpy as np
import matplotlib.pyplot as plt
import sp_spec as sp



def plot_bursts():
    sp.make_plot('out/slcp_p0-0001.fil', 219.46, tavg=100, tp=2, tdur=0.2, outfile = "out/burst.png")


dat = np.fromfile("out/test100.dat", dtype="f4")
print(dat)

time_interval = 1e-6
num_points = len(dat)
time_data = np.arange(num_points) * time_interval

plt.plot(time_data, dat)
plt.savefig("out/test101.png")


debug = 0

if __name__ == "__main__":
    if not debug: 
        #plot_bursts()
        print()

