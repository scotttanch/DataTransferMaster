from readgssi.dzt import readdzt
import numpy as np
import time
import transfer_tools as tls
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

search_path = "C:\\Users\\Scott\\Desktop\\GPR_DATA\\Lincoln_Hill\\" 
File = "FILE____956.DZT"
header,array,_ = readdzt(search_path+File)
traces = array[0]
numTraces = header['shape'][1]
samples = 250
traces = traces + abs(np.min(traces))
map = np.divide(traces,np.max(traces))
map = np.dstack((map,map,map))
xs = np.arange(0,2683)
zs = np.arange(0,250)

X,Z = np.meshgrid(xs,-zs)
Y = np.sin((1/500)*X)
fig = plt.figure()
ax = fig.add_subplot(111,projection='3d')
ax.plot_surface(X,Y,Z,facecolors=map,cmap='Greys')
plt.show()

# plt.imshow(traces)
# plt.show()
# path_x = np.arange(0,np.shape(traces)[1]) 	# trace number (2683 for this file)
# path_y = np.sin((1/500)*path_x)
# path_z = np.arange(0,samples) 			# sample number (250 samples per a scan)

# x = []
# y = []
# z = []
# c = []

# for i in range(numTraces):
	# for j in range(samples):
		# x.append(path_x[i])
		# y.append(path_y[i])
		# z.append(-j)
		# c.append(traces[j,i])

# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# img = ax.surface(x, y, z)
# fig.colorbar(img)
# ax.set_xlim(0,path_x[-1])
# ax.set_ylim(0,path_x[-1])
# plt.savefig("f_scan.png",format='png')
# plt.show()