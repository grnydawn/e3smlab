
import sys
import os
import subprocess

from microapp import App
from e3smlab import kgcompiler


STR_EX = b'execve('
STR_EN = b'ENOENT'
STR_UF = b'<unfinished'
STR_RE = b'resumed>'


class InspectCompile(App):

    _name_ = "inspectcompile"
    _version_ = "0.1.1"

    def __init__(self, mgr):

        self.add_argument("casedir", type=str, help="E3SM case top directory")
        self.add_argument("--removed", type=str, help="ouput a list of source files that are compiled but removed.")
        self.register_forward("data", help="json object")

    def perform(self, args):

        casedir = args.casedir["_"]

        if not os.path.isdir(casedir):
            raise Exception("Given case directory does not exist: %s" % casedir)

        cwd = os.getcwd()
        os.chdir(casedir)

        buildcmd = [os.path.join(str.encode(casedir), b"case.build")]
        cleancmd = buildcmd + [b"--clean-all"]

        # clean
        cleancmd_output = subprocess.check_output(cleancmd)

        # build with strace
   
        stracecmd = b'strace -f -q -s 100000 -e trace=execve -v -- /bin/sh -c "%s"'% b" ".join(buildcmd)

        try:

            tmpsrcid = 0

            flags = {}

            process = subprocess.Popen(stracecmd, stdin=subprocess.PIPE, \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                        shell=True)

            while True:

                #line = process.stdout.readline()
                line = process.stderr.readline()

                if line == b'' and process.poll() is not None:
                    break

                if line:
                    pos_execve = line.find(STR_EX)
                    if pos_execve >= 0:
                        pos_enoent = line.rfind(STR_EN)
                        if pos_enoent < 0:
                            pos_last = line.rfind(STR_UF)
                            if pos_last < 0:
                                pos_last = line.rfind(b']')
                            else:
                                pos_last -= 1
                            if pos_last >= 0:
                                try:
                                    lenv = {}
                                    exec(b'exepath, cmdlist, env = %s'%line[pos_execve+len(STR_EX):(pos_last+1)], None, lenv)

                                    exepath = lenv["exepath"]
                                    cmdlist = lenv["cmdlist"]
                                    env = lenv["env"]

                                    compid = cmdlist[0].split('/')[-1]
                                    if exepath and cmdlist and compid==cmdlist[0].split('/')[-1]:
                                        compiler = kgcompiler.CompilerFactory.createCompiler(compid)
                                        if compiler:
                                            srcs, incs, macros, openmp, options = compiler.parse_option(cmdlist, self._getpwd(env))
                                            if len(srcs)>0:
                                                for src in srcs:
                                                    print("Compiled: %s" % src)
                                                    #print("   with macros: %s" % str(macros))
                                                    if src in flags:
                                                        flags[src].append((exepath, incs, macros, openmp, options))

                                                    else:
                                                        flags[src] = [ (exepath, incs, macros, openmp, options) ]
                                except Exception as err:
                                    raise
                                    pass

            # get return code
            retcode = process.poll()
                                         
        #except Exception as err:
        #    raise
        finally:
            pass

        self.add_forward(data=flags)

        os.chdir(cwd)

    def _getpwd(self, env):
        for item in env:
            if item.startswith('PWD='):
                return item[4:]
        return None






























