"""A kernel manager relating notebooks and kernels

Authors:

* Brian Granger
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2013  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

from tornado import web

from IPython.kernel.multikernelmanager import MultiKernelManager
from IPython.utils.traitlets import (
    Dict, List, Unicode,
)

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------


class MappingKernelManager(MultiKernelManager):
    """A KernelManager that handles notebook mapping and HTTP error handling"""

    def _kernel_manager_class_default(self):
        return "IPython.kernel.ioloop.IOLoopKernelManager"

    kernel_argv = List(Unicode)
    kernels = []

    #-------------------------------------------------------------------------
    # Methods for managing kernels and sessions
    #-------------------------------------------------------------------------

    def _handle_kernel_died(self, kernel_id):
        """notice that a kernel died"""
        self.log.warn("Kernel %s died, removing from map.", kernel_id)
        self.remove_kernel(kernel_id)

    def start_kernel(self, **kwargs):
        """Start a kernel for a session an return its kernel_id.

        Parameters
        ----------
        session_id : uuid
            The uuid of the session to associate the new kernel with. If this
            is not None, this kernel will be persistent whenever the session
            requests a kernel.
        """
        kernel_id = None
        if kernel_id is None:
            kwargs['extra_arguments'] = self.kernel_argv
            kernel_id = super(MappingKernelManager, self).start_kernel(**kwargs)
            self.log.info("Kernel started: %s" % kernel_id)
            self.log.debug("Kernel args: %r" % kwargs)
            # register callback for failed auto-restart
            self.add_restart_callback(kernel_id,
                lambda : self._handle_kernel_died(kernel_id),
                'dead',
            )
        else:
            self.log.info("Using existing kernel: %s" % kernel_id)

        return kernel_id

    def shutdown_kernel(self, kernel_id, now=False):
        """Shutdown a kernel by kernel_id"""
        i = 0
        for kernel in self.kernels:
            if kernel['id'] == kernel_id:
                del self.kernels[i]
            i = i+1
        super(MappingKernelManager, self).shutdown_kernel(kernel_id, now=now)

    def kernel_model(self, kernel_id, ws_url):
        model = {"id":kernel_id, "ws_url": ws_url}
        self.kernels.append(model)
        return model

    def list_kernels(self):
        return self.kernels

    # override _check_kernel_id to raise 404 instead of KeyError
    def _check_kernel_id(self, kernel_id):
        """Check a that a kernel_id exists and raise 404 if not."""
        if kernel_id not in self:
            raise web.HTTPError(404, u'Kernel does not exist: %s' % kernel_id)
