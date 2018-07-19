'''
Bryon Kucharski
Wentworth Institute of Technology
Summer 2018

Common functions for sending recieving data from Unity
'''
class UnityInterface:
    def __init__(self,server):
        self.server = server

    def wait_for_phrase(self,phrase):
        """
            Blocking call - reads socket until the data is the same as phrase "start", "stop", "test", etc.

            Args:
                phrase: The string to listen to over the socket
        """
        while(self.server.getData() != phrase):
            print("waiting for" + phrase )

    def wait_for_number(self,num):
        """
            Blocking call - reads socket until the header is the same as num "0", "1", "2", etc.

            Args:
                num: The num to listen to over the socket

        """
        header = '-1'
        while header != num:
            data = self.server.getData().split(',')
            #print(data)
            header = data[0]
        return data

    def getReward(self):
        self.server.sendData('2')
        data = self.wait_for_number('2')
        reward = float(data[1])
        done = (data[2] == "True")
        return reward, done

    def step(self):
     
        header = '-1'
        self.server.sendData('3')
        data = self.wait_for_number('3')

        ball_x = int(data[2])
        robot_x = int(data[1])
        reward = float(data[3])
        done = (data[4] == "True")
        return [robot_x,ball_x],reward,done

    def send_action(self,a):
        """
        Sends the string over a socket in the form of '1,action'
        To move left, it would be the string '1,1'
        Unity is checking for the header to be 1
        """

        self.server.sendData('1,' + str(a))
        self.wait_for_number('1')

    def get_state_unity(self):
        """
        requst data from unity
        wait until socket header is 0
        parse data
        """

        self.server.sendData('0')
        header = '-1'
        data = self.wait_for_number('0')

        ball_x = float(data[2])
        robot_x = int(data[1])
        return [robot_x, ball_x]



