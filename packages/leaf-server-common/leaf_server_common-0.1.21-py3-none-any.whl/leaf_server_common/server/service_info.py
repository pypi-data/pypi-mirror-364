
# Copyright (C) 2019-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# leaf-server-common SDK Software in commercial settings.
#
# END COPYRIGHT

from datetime import datetime
import time

from leaf_common.persistence.easy.easy_txt_persistence \
    import EasyTxtPersistence


class ServiceInfo():
    """
    A class which populates a dictionary with service information.
    """

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, name=None, start_time_since_epoch=None, status="OK",
                 persist_path=None, persist_mechanism=None):
        """
        Constructor.

        :param name: The name of the service. Default None
        :param start_time_since_epoch: The start time of the service.
                        Get with time.time(). Default None.
        :param status: The status of the service. Default None.
        :param persist_path: The persist_path of the service. Default None.
        :param persist_mechanism: The persist_mechanismpath of the service.
                                Default None.
        """
        self.name = name
        self.start_time_since_epoch = start_time_since_epoch
        self.status = status
        self.persist_path = persist_path
        self.persist_mechanism = persist_mechanism

    def get_service_info(self):
        """
        Return a dictionary with service information in it.
        """

        # Template dict
        service_info = {
            "version": self.get_version(),
            "uptime": self.get_uptime(),
            "start_time": self.get_start_time(),
            "status": self.status,
            "persist_path": self.persist_path,
            "persist_mechanism": self.persist_mechanism,
            "latest_commit": self.get_last_commit(),
            "name": self.name
        }

        return service_info

    @staticmethod
    def get_version():
        """
        :return: the service version
        """
        persistence = EasyTxtPersistence(base_name="service_version")
        version = persistence.restore()
        if version is not None:
            version = version.strip()
        return version

    @staticmethod
    def get_last_commit():
        """
        :return: the last commit
        """
        persistence = EasyTxtPersistence(base_name="last_commit")
        last_commit = persistence.restore()
        if last_commit is not None:
            last_commit = last_commit.strip()
        return last_commit

    def get_start_time(self):
        """
        :return: The start time in iso format
        """
        if self.start_time_since_epoch is None:
            return None

        start_datetime = datetime.fromtimestamp(self.start_time_since_epoch)
        iso_timestamp = start_datetime.isoformat()
        return iso_timestamp

    def get_uptime(self):
        """
        :return: The start time in iso format
        """
        if self.start_time_since_epoch is None:
            return None

        now = time.time()
        now_datetime = datetime.fromtimestamp(now)
        start_datetime = datetime.fromtimestamp(self.start_time_since_epoch)

        delta = now_datetime - start_datetime
        up_time = str(delta)

        return up_time
