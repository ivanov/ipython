"""Kernel manager for a terminal environment.
"""

from IPython.utils.traitlets import Type

from IPython.zmq.kernelmanager import KernelManager, SubSocketChannel, \
    XReqSocketChannel, RepSocketChannel, HBSocketChannel

class TSubSocketChannel(SubSocketChannel):
    def call_handlers(self, msg):
        print 'Message received, type:', msg['msg_type']

class TXReqSocketChannel(XReqSocketChannel):
    def call_handlers(self, msg):
        print 'Message received, type:', msg['msg_type']

class TRepSocketChannel(RepSocketChannel):
    def call_handlers(self, msg):
        print 'Message received, type:', msg['msg_type']

class THBSocketChannel(HBSocketChannel):
    def call_handlers(self, msg):
        print 'Message received, type:', msg['msg_type']

class TKernelManager(KernelManager):
    
    sub_channel_class = Type(TSubSocketChannel)
    xreq_channel_class = Type(TXReqSocketChannel)
    rep_channel_class = Type(TRepSocketChannel)
    hb_channel_class = Type(THBSocketChannel)
