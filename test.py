import pygdbmi.parser
import pygdbmi.objects
import sys


def print_done(rr):
    print('DONE')

    for r in rr.results:
        print(r)


def print_connected(rr):
    print('CONNECTED')


def print_error(rr):
    print('ERROR')
    print('msg:  {}'.format(rr.msg))
    print('code: {}'.format(rr.code))


def print_exit(rr):
    print('EXIT')


parser = pygdbmi.parser.OutputParser()
rr = parser.parse(sys.argv[1] + '\n')

print('TOKEN={}'.format(rr.token))

rr_map = {
    pygdbmi.objects.DoneResultRecord: print_done,
    pygdbmi.objects.ConnectedResultRecord: print_connected,
    pygdbmi.objects.ErrorResultRecord: print_error,
    pygdbmi.objects.ExitResultRecord: print_exit,
}

print(rr_map[type(rr)](rr))
