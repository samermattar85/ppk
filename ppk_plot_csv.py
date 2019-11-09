import csv
import matplotlib.pyplot as plt
import sys
import numpy as np
import time

if __name__ == "__main__":
    try:
        if len(sys.argv) == 2:
            csvfilename = sys.argv[1]
        else:
            print ('Usage: python ppk_plot_csv.py <ppk_file>.csv')
            exit()
    except:
        raise
        # csvfilename = '/home/daniel/PycharmProjects/plot_ppk_csv/ppk_out_comm_info.csv'

    fs = 7692

    with open(csvfilename, 'r') as f:
        reader = csv.reader(f)
        i = 0
        for row, row_val in enumerate(reader):
            i = i + 1
            print "line {}, raw_val = {}".format(i, row)
            data = np.array(row_val)
            data = data.astype(np.float)
            time = np.linspace(0, (len(data) - 1)/fs, num=len(data))
            plt.plot(time, data/1000)
            count = 0
            while True:
                count = count + 1
                t = [0, 0]
                print('Please click {}'.format(count))
                x = plt.ginput(2, timeout=-1, mouse_add=3, mouse_stop=2, mouse_pop=1)
                # print("clicked", x)
                if x[1][0] > x[0][0]:
                    t[0] = x[0][0]
                    t[1] = x[1][0]
                else:
                    t[0] = x[1][0]
                    t[1] = x[0][0]
                # print("dt = ", t)
                vec_ind = [0,0]
                for i, e in enumerate(time) :
                    if time[i] < t[0] and time[i + 1] > t[0]:
                        vec_ind[0] = i
                    if time[i] < t[1] and time[i + 1] > t[1]:
                        vec_ind[1] = i
                print('index = {} , {}'.format(vec_ind[0], vec_ind[1]))
                print('dt =  {:} msec'.format((t[1]-t[0])*1000))
                vec = np.array(data[vec_ind[0]:vec_ind[1]] / 1000)
                print('Mean  Value =  {:} mAmp'.format(np.mean(vec)))
                print('StDev Value =  {:} mAmp'.format(np.std(vec)))
                print('Max  Value  =  {:} mAmp'.format(np.max(vec)))
                print('Min  Value  =  {:} mAmp'.format(np.min(vec)))
                print('coulomb  =  {:} milicoulomb'.format(sum(vec)/fs))
                print('<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>')

                # plt.show()
