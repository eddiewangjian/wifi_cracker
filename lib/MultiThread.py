#coding=utf-8
import time
import threading

#需要返回结果时，需要使用MultiThread对象的thread成员作为并发队列元素，然后调用process
#不需要返回结果时，可直接使用t = threading.Thread(target=funcname, args=parameter)为并发队列元素，直接调用process
class MultiThread:
    def __init__(self, func, param):
        self.result = {}    #用于存放结果内容，用户可自定义其内容
        self.target = func  #多线程运行的函数接口型
        self.args = param   #接口参数，多参数时，这里建议使用dict，在func中对param进行解析，读取各个参数
        self.thread = threading.Thread(target=self.execute) #构造的真正用于运行的线程

    def execute(self):
        try:
            self.result = self.target(self.args)
        except:
            try:
                self.result = self.target()
            except:
                self.result = None

    @staticmethod
    def process(thread_list):
        #静态函数，用于运行线程队列中所有的子线程，线程元素t = threading.Thread(target=funcname, args=parameter),第二个参数可以缺省
        if thread_list == None:
            return
        for thread in thread_list:
            thread.thread.setDaemon(True)
            thread.thread.start()

        for thread in thread_list:
            thread.thread.join()


#code below is for test
def func1(res):
    print "1=", time.ctime()
    time.sleep(3)
    print "1=", time.ctime()
    return res

def func2():
    print "2=", time.ctime()
    time.sleep(3)
    print "2=", time.ctime()
    return 2

if __name__ == "__main__":
    print time.ctime()
    t1 = MultiThread(func1,1)
    t2 = MultiThread(func1,2)
    thread_list = [t1, t2]
    print thread_list
    MultiThread.process(thread_list)
    print t1.result
    print t2.result
    del t1, t2
    print time.ctime()





