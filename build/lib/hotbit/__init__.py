from hotbit import auth

def Hotbit(auth):
    if type(auth) == dict:
        from hotbit.reverseApi import Hotbit
        return Hotbit(auth)
    elif type(auth) == list:
        from hotbit.officialApi import Hotbit
        return Hotbit(auth[0], auth[1])