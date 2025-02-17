from bot import aria2, DOWNLOAD_DIR, LOGGER
from bot.helper.ext_utils.bot_utils import MirrorStatus, get_readable_time

def get_download(gid):
    try:
        return aria2.get_download(gid)
    except Exception as e:
        LOGGER.error(f'{e}: while getting torrent info')


class AriaDownloadStatus:

    def __init__(self, gid, listener):
        self.__gid = gid
        self.__download = get_download(gid)
        self.__listener = listener
        self.message = listener.message

    def path(self):
        return f'{DOWNLOAD_DIR}{self.__listener.uid}'

    def __update(self):
        self.__download = get_download(self.__gid)
        if self.__download.followed_by_ids:
            self.__gid = self.__download.followed_by_ids[0]

    def progress(self):
        """
        Calculates the progress of the mirror (upload or download)
        :return: returns progress in percentage
        """
        return self.__download.progress_string()

    def size_raw(self):
        """
        Gets total size of the mirror file/folder
        :return: total size of mirror
        """
        return self.__download.total_length

    def processed_bytes(self):
        return self.__download.completed_length

    def speed(self):
        self.__update()
        return self.__download.download_speed_string()

    def name(self):
        self.__update()
        return self.__download.name

    def size(self):
        return self.__download.total_length_string()

    def eta(self):
        seconds = self.__download.eta
        if seconds.total_seconds() >= 86400000000000:
            return '-'
        else:
            return f'{get_readable_time(seconds.total_seconds())}'
        # return self.__download.eta_string()

    def status(self):
        download = self.__download
        if download.is_waiting:
            return MirrorStatus.STATUS_WAITING
        elif download.is_paused:
            return MirrorStatus.STATUS_PAUSED
        else:
            return MirrorStatus.STATUS_DOWNLOADING

    def aria_download(self):
        return self.__download

    def download(self):
        return self

    def listener(self):
        return self.__listener

    def gid(self):
        self.__update()
        return self.__gid

    def Pemirror(self):
        return self.message

    def cancel_download(self):
        LOGGER.info(f"Cancelling Download: {self.name()}")
        self.__update()
        download = self.__download
        if download.is_waiting:
            self.__listener.onDownloadError("Download dibatalkan oleh user")
            aria2.remove([download], force=True, files=True)
            return
        if len(download.followed_by_ids) != 0:
            downloads = aria2.get_downloads(download.followed_by_ids)
            self.__listener.onDownloadError('Download distop oleh user!')
            aria2.remove(downloads, force=True, files=True)
            aria2.remove([download], force=True, files=True)
            return
        self.__listener.onDownloadError('Download distop oleh user!')
        aria2.remove([download], force=True, files=True)
