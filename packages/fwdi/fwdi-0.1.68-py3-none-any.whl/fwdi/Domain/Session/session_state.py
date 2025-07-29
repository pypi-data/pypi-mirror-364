from threading import Lock

from ...Domain.Session.user_session import UserSession

class SessionState():
    def __init__(self):
        self.__transcribe:dict[str:UserSession] = {}
        self.__lock__:Lock = Lock()
    
    def contain(self, key:str)->bool:
        return True if key in self.__transcribe else False

    def __getitem__(self, key:str)->UserSession:
        try:

            return self.__transcribe[key]
        finally:
            self.__lock__.release()

    def __setitem__(self, key:str, user_data:UserSession):
        self.__lock__.acquire()
        try:
            if not self.__transcribe.get(key, None):
                self.__transcribe[key] = user_data

        finally:
            self.__lock__.release()