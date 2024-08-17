import os
import sys
import random 
import json
import math
import utils
import time
import config
import numpy
random.seed(73)

class Agent:
    def __init__(self, table_config) -> None:
        self.table_config = table_config
        self.prev_action = None
        self.curr_iter = 0
        self.state_dict = {}
        self.holes =[]
        self.ns = utils.NextState()


    def set_holes(self, holes_x, holes_y, radius):
        for x in holes_x:
            for y in holes_y:
                self.holes.append((x[0], y[0]))
        # print(self.holes)
        self.ball_radius = radius


    def action(self, ball_pos=None):
        ## Code you agent here ##
        ## You can access data from config.py for geometry of the table, configuration of the levels, etc.
        ## You are NOT allowed to change the variables of config.py (we will fetch variables from a different file during evaluation)
        ## Do not use any library other than those that are already imported.
        ## Try out different ideas and have fun!
        new_holes=[(80,80),(920,420),(920,80),(80,420),(500,80),(500,420)]
        
        # new_holes=[(920,420)]
        def new_centre(p,angles):
            if angles[1]>=0 and angles[1]<=0.5:
                return(p[0]+(2*self.ball_radius*math.cos(angles[0])),p[1]+(2*self.ball_radius*math.sin(angles[0])))
            elif angles[1]>=0.5 and angles[1]<1:
                return(p[0]+(2*self.ball_radius*math.cos(angles[0])),p[1]-(2*self.ball_radius*math.sin(angles[0])))
            elif angles[1]<=0 and angles[1]>=-0.5:
                return(p[0]-(2*self.ball_radius*math.cos(angles[0])),p[1]+(2*self.ball_radius*math.sin(angles[0])))
            else:
                return(p[0]-(2*self.ball_radius*math.cos(angles[0])),p[1]-(2*self.ball_radius*math.sin(angles[0])))
        
        def dist(p1,p2):
            return numpy.sqrt(((p1[0]-p2[0])*(p1[0]-p2[0]))+((p1[1]-p2[1])*(p1[1]-p2[1])))
        
        def force_calc(hole1,cue1,cue_or,angle):
            force1=dist(cue_or,cue1)+(dist(cue1,hole1)/abs(math.cos(angle)))
            # print(hole1,cue1,cue_or)
            force1=force1/1300
            if force1>1:
                force1=dist(cue_or,cue1)/1300
                # print("idhar",force1)
                # return force1
            if force1<=0.05:
                return 0.7
            
            return force1
        
        def angle_find(p1,p2):
            if p1[0]==p2[0]:
                if p2[1]>=p1[1]:
                    return (math.pi/2,-1)
                return (math.pi/2,0)
                
            slope=(abs(p1[1]-p2[1])/abs(p1[0]-p2[0]))
            angle_pi=math.atan(slope)
            angle=math.atan(slope)/(math.pi)
            if p1[0]>=p2[0] and p1[1]>=p2[1]:
                return (angle_pi,0.5-angle)
            if p1[0]>=p2[0] and p2[1]>=p1[1]:
                return (angle_pi,0.5+angle)
            if p2[0]>=p1[0] and p1[1]>=p2[1]:
                return (angle_pi,-1*(0.5-angle))
            if p2[0]>=p1[0] and p2[1]>=p1[1]:
                return (angle_pi,-1*(0.5+angle))
        
        def hit_ball(balla,angle):
            for i in range(3,10,2):
                f=i*0.1
                new_ball_pos=self.ns.get_next_state(ball_pos,(angle,f),42)
                if new_ball_pos==None:
                    return f
                if len(ball_pos)-len(new_ball_pos)>0:
                    return f
                if dist(ball_pos[balla],new_ball_pos[balla])>10:
                    return f
           
            return dist(ball_pos[balla],ball_pos[0])/1300
            
        
        # Actual Code
        ans_angle_angle=1
        ans_angle_force=1
        diff_angle=10
        diff_actual_angle=500
        ans_force_force=1
        ans_force_angle=1
        
        target=1
        # print(ball_pos)
        ball_hole_pairs=[]
        # print(self.holes)
        which_ball=0
        for ball in ball_pos:
            if ball=="white" or ball==0:
                continue
            for i in range(len(new_holes)):
                is_middle=None
                if i==1 or i==4:
                    is_middle=i
                cue_hole=angle_find(ball_pos[ball],new_holes[i])
                centre1=new_centre(ball_pos[ball],cue_hole)
                angle_this=angle_find(ball_pos[0],centre1)
                new_diff=abs(cue_hole[1]-angle_this[1])
                new_diff_actual=abs(cue_hole[0]-angle_this[0])
                force=force_calc(new_holes[i],centre1,ball_pos["white"],cue_hole[0]-angle_this[0])

                    
                ball_hole_pairs.append([force+0.05,angle_this[1],new_diff,is_middle])
                if force<ans_force_force:
                    ans_force_force=force
                    ans_force_angle=angle_this[1]
                    
                if new_diff<diff_angle:
                    which_ball=ball
                    target=cue_hole[1]
                    ans_angle_angle=angle_this[1]
                    ans_angle_force=force
                    diff_angle=new_diff
                    diff_actual_angle=new_diff_actual
        # if flag:
        #     return (ans_angle,0.2)

        angles_sorted=ball_hole_pairs
        angles_sorted.sort(key=lambda x:x[2])
        forces_sorted=ball_hole_pairs
        forces_sorted.sort(key=lambda x:x[0])
        # print(forces_sorted)
        
        for i in range(min(5,len(forces_sorted))):
            new_ball_pos=self.ns.get_next_state(ball_pos,(forces_sorted[i][1],forces_sorted[i][0]),42)
            diff_angle=forces_sorted[i][2]
            
            if len(ball_pos)-len(new_ball_pos)>0:
                # print("Force")
                    
                return (forces_sorted[i][1],forces_sorted[i][0])
            
        for i in range(min(3,len(angles_sorted))):
            # new_ball_pos=self.ns.get_next_state(ball_pos,(angles_sorted[i][1],angles_sorted[i][0]),42)
            for j in range(1,10,1):
                force=j*0.1
                new_ball_pos=self.ns.get_next_state(ball_pos,(angles_sorted[i][1],force),42)
                if len(ball_pos)-len(new_ball_pos)>0:
                    # print("Angle")
                    return(angles_sorted[i][1],force)
                
            # return (angles_sorted[i][1],angles_sorted[i][0])
            

                
        
        if(abs(diff_angle-0.5)<=0.05):
            # return (angle_find(ball_pos[0],(ball_pos[which_ball][0],ball_pos[which_ball][1]-self.ball_radius-3))[1],0.5)
            
            angle2=angle_find(ball_pos[0],(ball_pos[which_ball][0],ball_pos[which_ball][1]-self.ball_radius-3))[1]
            return (angle2,hit_ball(which_ball,angle2))
        
        # print("last")
        
        # print("fucl",ans_angle_angle)
        # print(abs(diff_actual_angle-90))
        return (ans_angle_angle,hit_ball(which_ball,ans_angle_angle))
       
        # angle_all_fail=angle_find(ball_pos[0],ball_pos[which_ball])
        # return (angle_all_fail[1],hit_ball(which_ball,angle_all_fail[1]))
     
        
        
         
                    

        return (-0.25,0.6)
