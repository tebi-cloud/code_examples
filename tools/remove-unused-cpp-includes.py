#!/usr/bin/env python
# tool by https://github.com/WojciechMula/cleanup-headers
import sys
import os
import os.path
import subprocess

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


class ProgramError(ValueError):
    pass


INCLUDE = '#include '
DELETE  = 'delete'
COMMENT = 'comment'

class File(object):
    def __init__(self, file):

        self.includes = []
        self.lines = []

        for line in file:
            tmp = line.strip()
            if tmp.startswith(INCLUDE):
                inc = IncludeLine(line)
                self.includes.append(inc)
                self.lines.append(inc)
            else:
                self.lines.append(line)


    def write(self, file):
        for l in self.lines:
            file.write(str(l))


    def write_stripped(self, file, callback):
        for l in self.lines:
            if type(l) is IncludeLine:
                ret = callback(l)
                if ret is not None:
                    file.write(ret)
            else:
                file.write(l)


class IncludeLine(object):
    def __init__(self, line):
        tmp = line.strip()[len(INCLUDE):]
        tmp = tmp[1:-1]

        self.line    = line
        self.path    = tmp
        self.enabled = True


    def enable(self, e):
        self.enabled = bool(e)


    def get_path(self):
        return self.path


    def __str__(self):
        if self.enabled:
            return self.line
        else:
            return '// %s' % self.line


class CommandLine(object):
    def __init__(self, args):
        self.args   = args[:]
        self.index  = None
        self.source = None

        for i, arg in enumerate(self.args):
            if arg.endswith('.c') or arg.endswith('.cpp'):
                self.index  = i
                self.source = arg
                break

        if self.index is None:
            raise ProgramError("Expected .c/.cpp file on argument list")


    def get_path(self):
        return self.source


    def set_path(self, path):
        self.args[self.index] = path


    def __str__(self):
        return ' '.join(self.args)


class GCCCommandLine(CommandLine):
    def __init__(self, args):
        super(GCCCommandLine, self).__init__(args)

        self.remove_optimization_options()
        self.quit_on_first_error()
        self.do_not_create_object()


    def remove_optimization_options(self):
        for opt in ['-O1', '-O2', '-O3']:
            while True:
                try:
                    self.args.remove(opt)
                except ValueError:
                    break


    def quit_on_first_error(self):
        self.args.append('-Wfatal-errors')


    def do_not_create_object(self):
        self.args.append('-fsyntax-only')


class Application:
    def __init__(self, config, cmdline):
        self.config  = config
        self.cmdline = cmdline

        self.out     = sys.stdout
        self.pid     = os.getpid()

        srcpath = self.cmdline.get_path()
        if not os.path.exists(srcpath):
            raise ProgramError("Can't open source file '%s'" % srcpath)

        with open(srcpath, 'rt') as f:
            self.file = File(f)


    def write(self, msg):
        self.out.write(msg)
        self.out.flush()


    def run(self):
        self.write('Checking compilation of %s... ' % self.cmdline.get_path())
        if not self.can_compile():
            self.write('failed\n')
            return
        else:
            self.write('OK\n')

        self.check()
        self.fix()


    def check(self):
        dirname, filename = os.path.split(self.cmdline.get_path())
        dstpath = 'ch-%x-%s' % (self.pid, filename)
        self.cmdline.set_path(dstpath)

        self.not_needed = []
        for index, include in enumerate(self.file.includes):
            self.write('Removing %s (%d/%d)... ' % (include.get_path(), index + 1, len(self.file.includes)))
            include.enable(False)
            try:
                with open(dstpath, 'wt') as f:
                    self.file.write(f)

                if self.can_compile():
                    self.write('OK\n')
                    self.not_needed.append(include)
                else:
                    include.enable(True)
                    self.write('not possible\n')
            finally:
                try:
                    os.remove(dstpath)
                except:
                    pass


    def fix(self):
        srcpath = self.cmdline.get_path()
        self.write('%s: ' % srcpath)
        if len(self.not_needed) == 0:
            self.write('no changes\n')
        else:
            tmp = [item.get_path() for item in self.not_needed]
            self.write('not required %s\n' % (', '.join(tmp)))

            if self.config.overwrite:
                with open(srcpath, 'wt') as f:
                    self.file.write_stripped(f, self.get_write_callback())

                self.write('%s was updated\n' % srcpath)

        self.write('\n')


    def get_write_callback(self):

        def remove_includes(include):
            if include.enabled:
                return str(include)

        def comment_out_includes(include):
            return str(include)

        if self.config.modification == DELETE:
            return remove_includes
        else:
            return comment_out_includes


    def can_compile(self):
        cmdline = str(self.cmdline)
        if self.config.quiet:
            cmdline += ' 2> /dev/null'

        ret = subprocess.call(cmdline, shell=True)
        return ret == 0


class ConfigParser(configparser.ConfigParser):
    def tryget(self, section, value, default):
        try:
            return self.get(section, value)
        except configparser.NoSectionError:
            return default
        except configparser.NoOptionError:
            return default

    def trygetboolean(self, section, value, default):
        try:
            return self.getboolean(section, value)
        except configparser.NoSectionError:
            return default
        except configparser.NoOptionError:
            return default


class Configuration(object):
    def __init__(self):
        self.load()

    def load(self):
        p = ConfigParser(allow_no_value=True)
        p.read([os.path.expanduser(path) for path in self.config_paths()])

        self.quiet        = p.trygetboolean('general', 'quiet', True)
        self.overwrite    = p.trygetboolean('general', 'overwrite', True)
        self.modification = p.tryget('general', 'modification', DELETE).lower()
        self.mode         = p.tryget('compiler', 'mode', None)

        if self.modification not in (DELETE, COMMENT):
            raise ProgramError("Setting general.modification must be either '%s' or '%s'" % (DELETE, COMMENT))


    def config_paths(self):
        try:
            yield os.environ['CLEANUP_HEADERS_CONFIG']
        except KeyError:
            pass

        yield '~/.config/cleanup-headers/config.ini'


def main():
    try:
        conf = Configuration()
        cmdlineclass = CommandLine
        if conf.mode == 'gcc':
            cmdlineclass = GCCCommandLine

        cmdline = cmdlineclass(sys.argv[1:])
        app = Application(conf, cmdline)
        app.run()
    except KeyboardInterrupt:
        sys.stdout.write('\nInterrupted\n')
        pass
    except ProgramError as e:
        sys.stderr.write(str(e))
        sys.stderr.write('\n')
    except:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()


