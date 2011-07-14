"""benchmarking through py.test"""

from math import ceil, floor, log10
import time
import timeit

from inspect import getsource


# from IPython.Magic.magic_timeit
#units = ["s", "ms", "\xc2\xb5s", "ns"]
units = ["s", "ms", "us", "ns"]
scaling = [1, 1e3, 1e6, 1e9]

unitn = dict((s,i) for i,s in enumerate(units))

precision = 3

def pytest_configure(config):
    config.inicfg.config.sections['pytest']['python_files'] = 'bench_*.py'
    config.inicfg.config.sections['pytest']['python_functions'] = 'bench_'
    config.benchlog = []

def pytest_runtest_call(item, __multicall__):
    t0 = time.time()
    try:
        __multicall__.execute()
    finally:
        item.benchtime = time.time() - t0

        # extract benchmark title
        if item.obj.func_doc is not None:
            item.benchtitle = item.obj.func_doc
        else:
            src = getsource(item.obj)
            item.benchtitle = src.splitlines()[1].strip()
        item.config.benchlog.append(item)

def pytest_terminal_summary(terminalreporter):
    print_bench_results(terminalreporter, terminalreporter.config.benchlog)


class BenchSession:

    def header(self, colitems):
        #self.out.sep("-", "benchmarking starts")
        super(BenchSession, self).header(colitems)

    def footer(self, colitems):
        super(BenchSession, self).footer(colitems)
        #self.out.sep("-", "benchmarking ends")

        self.out.write('\n')
        self.print_bench_results()


def print_bench_results(out, benchlog):
    out.write('==============================\n')
    out.write(' *** BENCHMARKING RESULTS *** \n')
    out.write('==============================\n')
    out.write('\n')

    # benchname, time, benchtitle
    results = []

    for item in benchlog:
        best = item.benchtime

        if best is None:
            # skipped or failed benchmarks
            tstr = '---'

        else:
            # from IPython.Magic.magic_timeit
            if best > 0.0:
                order = min(-int(floor(log10(best)) // 3), 3)
            else:
                order = 3

            tstr = "%.*g %s" % (precision, best * scaling[order], units[order])

        results.append( [item.name, tstr, item.benchtitle] )

    # dot/unit align second column
    # FIXME simpler? this is crappy -- shame on me...
    wm = [0]*len(units)
    we = [0]*len(units)

    for s in results:
        tstr = s[1]
        n,u = tstr.split()

        # unit n
        un = unitn[u]

        try:
            m,e = n.split('.')
        except ValueError:
            m,e = n,''

        wm[un] = max(len(m), wm[un])
        we[un] = max(len(e), we[un])

    for s in results:
        tstr = s[1]
        n,u = tstr.split()

        un = unitn[u]

        try:
            m,e = n.split('.')
        except ValueError:
            m,e = n,''

        m = m.rjust(wm[un])
        e = e.ljust(we[un])

        if e.strip():
            n = '.'.join((m,e))
        else:
            n = ' '.join((m,e))


        # let's put the number into the right place
        txt = ''
        for i in range(len(units)):
            if i == un:
                txt += n
            else:
                txt += ' '*(wm[i]+we[i]+1)

        s[1] = '%s %s' % (txt, u)


    # align all columns besides the last one
    for i in range(2):
        w = max(len(s[i]) for s in results)

        for s in results:
            s[i] = s[i].ljust(w)

    # show results
    for s in results:
        out.write('%s  |  %s  |  %s\n' % tuple(s))


def main(args=None):
    # hook our Directory/Module/Function as defaults
    from py.__.test import defaultconftest

    defaultconftest.Directory   = Directory
    defaultconftest.Module      = Module
    defaultconftest.Function    = Function

    # hook BenchSession as py.test session
    config = py.test.config
    config._getsessionclass = lambda : BenchSession

    py.test.cmdline.main(args)
