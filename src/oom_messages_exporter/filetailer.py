import logging
import os
from typing import TypedDict

def log_exception(where, err):
    logging.critical('An error occurred in "{}", exception:\n---\n{}\n---'.format(where, err))

class FileStat(TypedDict):
    inode: int
    size: int

class FileTailer:
    """
    The class works like the 'tail -F <file>' command and returns a set of lines if they've appeared in a given log file since last call.
    You need only initialize the class and use the tail() method, like this example:

    ft = FileTailer(file='/var/log/messages')
    while True:
        data = ft.tail()
        if len(data) > 0:
            process...(data)
        sleep(how many that you want)
    """
    def __init__(self, *, file) -> None:

        """
        :param file: a log that will be watched
        """

        self.file_name = file
        self.file_stats = FileStat # Data in this variable is useful for checking the given file rotate. 
        self.fd = None

        if self.__open_file():
            pass
        else:
            raise FileNotFoundError(file)
        
    def __open_file(self, pos=-1) -> (bool, str):

        """
        The method opens a file and moves a pointer to the last line.
        Also the method stores info about the opened file thought a call of the '__update_file_stat' method.
        """

        self.__update_file_stat()

        if not os.path.exists(self.file_name):
            logging.error('File "{}" does not exist.'.format(self.file_name))
            return(False)
        
        try:
            fd = open(self.file_name)
        except Exception as err:
            log_exception('open({})'.format(self.file_name), err)
            return(False)
        
        # If needed positions isn't set -> move a pointer in a fd to the end.
        self.fd = fd
        if pos < 0:
            self.fd.seek(self.file_stats['size'])

        return(True)

    def __get_stat(self) -> FileStat:

        """
        The method returns info about the give file. Size, inode, etc.
        This data is used for check a rotation of the file.
        """

        ret = {'inode': -1, 'size': -1}

        try:
            stat = os.stat(self.file_name)
            ret['inode'] = stat.st_ino
            ret['size'] = stat.st_size
        except Exception as err:
            log_exception('__get_stat', err)

        return(ret)
    
    def __update_file_stat(self) -> None:

        """
        This methods stores and updates info about the given file in the 'file_stats' variable.
        """

        self.file_stats = self.__get_stat()
    
    def __file_is_rotated(self) -> bool:

        """
        This method checks a rotation of the given log and returns 'True' if the log has been rotated.
        Rotations by move and by truncate are supported.
        """

        prev_inode = self.file_stats['inode']
        self.__update_file_stat()

        if self.file_stats['inode'] != prev_inode:
            logging.warning('The "{}" file is rotated, inode: {} -> {}'.format(self.file_name, prev_inode, self.file_stats['inode']))
            return(True)
        
        if self.file_stats['size'] < self.fd.tell():
            logging.warning('The "{}" file is truncated, size: {} -> {}'.format(self.file_name, self.fd.tell(), self.file_stats['size']))
            return(True)
        
        return(False)
    
    def tail(self) -> list[str]:

        """
        The main method of the class. Method returns a list of lines since the last call of the method.
        You have to call the method from time to time (few seconds). When the method will return a non empty list
        it's a mark that you can do smth with the returned lines.
        """

        ret = list()

        if self.file_stats['inode'] == -1 and self.__open_file(0) == False:
            logging.critical('Can not open the "{}" file.'.format(self.file_name))
            return(list())

        line = self.fd.readline()
        while line:
            ret.append(line.strip())
            line = self.fd.readline()

        if self.__file_is_rotated():
            if self.__open_file(0):
                logging.info('The "{}" file is reopened, inode: {}.'.format(self.file_name, self.file_stats['inode']))
            else:
                logging.critical('The "{}" file is NOT reopened, will try again next time'.format(self.file_name))

        return(ret)