
class SomethingError(Exception):
    pass

def make_error(x,y):
    try:
        a = x/y
        return a
    except:
        raise SomethingError('it broke')


try:
    a = make_error(1,0)
except SomethingError as e:
    print(str(e))
