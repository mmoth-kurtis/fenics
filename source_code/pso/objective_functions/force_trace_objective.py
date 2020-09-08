import sys
import os
import numpy as np
from scipy import interpolate as interp
sys.path.append("/home/fenics/shared/")

# all objective function files should have the function "return_objective"
# due to memory issues, information is printed out and not passed as dictionary
# object functions will need access to particle output directory

# This will be a class for feeding pressure traces from the dyna 3 state paper
# as a target for the objective function

def init():
    objFunc_class = singlecell_force_trace()
    return objFunc_class

class singlecell_force_trace():

    def __init__(self):

        # Load in target force trace here
        f_trace = np.load('stress_array.npy')
        f_time = np.load('tarray.npy')
        self.f_time = f_time
        self.ftrace = f_trace

        #Create interpolation function to qinterpolate experimental data to simulation time points
        self.f = interp.interp1d(self.f_time,self.ftrace)


    def evaluate(self,output_dir,iter,p_num):

        os.getcwd()

        # load in particle active_stress
        #particle_active_stress_file = output_dir + "iter_" + str(iter) + "_particle_" + str(p_num) + "/stress_array.npy"
        particle_active_stress_file = output_dir + "stress_array.npy"
        #particle_time_file= output_dir + "iter_" + str(iter) + "_particle_" + str(p_num) + "/tarray.npy"
        particle_time_file = output_dir + "tarray.npy"
        particle_active_stress = np.load(particle_active_stress_file)
        particle_active_stress = particle_active_stress[:-1]


        #interpolate experimental pressure to same time points as simulation pressure
        # but get rid of first loading_num number of points (time independent loading)
        particle_time = np.load(particle_time_file)
        if len(particle_time) > len(particle_active_stress):
            particle_time = particle_time[:-1]
        interpolated_ftrace = self.f(particle_time)

        # Look at differences in experimental pressure and simulation predicted pressure
        particle_error_array = np.power(interpolated_ftrace-particle_active_stress,2*np.ones(len(particle_time)))
        particle_error = np.sum(particle_error_array)

        print "particle " + str(p_num) + " error is " + str(particle_error)

        return particle_error