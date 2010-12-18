from IPython.frontend.terminal.kernelmanager import TKernelManager
k = TKernelManager()
k.start_kernel()
k.start_channels()
k.channels_running
k.xreq_channel.execute('x=10\n')
