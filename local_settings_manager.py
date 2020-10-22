import logging
import os

from PyQt5 import QtCore
from PyQt5.QtCore import QCoreApplication

logger = logging.getLogger(__name__)
SOFTWARE_VERSION = "1.0"
ORGANIZATION_NAME = 'Fazialis-Nerv-Zentrum Jena'
ORGANIZATION_DOMAIN = 'hno.ukj.emotrics'
APPLICATION_NAME = 'Emotrics Facial Measurement'


class LocalSettings:
    def __init__(self, defaultValues=None):
        # Set Application Name globally e.g. for QSettings
        QCoreApplication.setApplicationName(ORGANIZATION_NAME)
        QCoreApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
        QCoreApplication.setApplicationName(APPLICATION_NAME)
        logger.info("Initialize QCore %s Application with: Domain-%s Organization-%s" % (APPLICATION_NAME,
                                                                                         ORGANIZATION_DOMAIN,
                                                                                         ORGANIZATION_NAME))
        self.settings = QtCore.QSettings()

        if isinstance(defaultValues, dict):
            self.__defaultValues = defaultValues
        else:
            self.__defaultValues = {
                '_CalibrationType': 'Iris',  # or Manual
                '_CalibrationValue': 11.77,
                '_ModelName': 'MEE',  # or iBUGS
                '_lastUsedImageFolder': os.path.expanduser('~') + os.path.sep + "Pictures"
            }
        # check if all keys are present, or not.
        # if they are not present, initialize the Datastore
        if not self.check_QSettingsDefaultKeys():
            self.__init_QSettings()

    def __init_QSettings(self):
        for key, value in self.__defaultValues.items():
            self.settings.setValue(key, value)
        self.settings.sync()

    def get_QSettingsType(self, value):
        """returns the QSettings type of the given python variable
            TODO is experimental
        Arguments:
            value {[type]} -- python variable

        Returns:
            [type] -- QSetting Type e.g. QStringList, or int, or float
        """
        if isinstance(value, str):
            return "QString"
        elif isinstance(value, float):
            return float
        elif isinstance(value, int):
            return int
        elif isinstance(value, bool):
            return True
        else:
            return None

    def check_QSettingsDefaultKeys(self) -> bool:
        return set(self.settings.allKeys()) == set(self.__defaultValues.keys())

    def get_setting(self, key):
        if key in self.__defaultValues:
            return self.settings.value(key,
                                       self.__defaultValues.get(key),
                                       self.get_QSettingsType(self.__defaultValues.get(key)))
        else:
            return None

    def set_setting(self, key="", value=None):
        if key in self.__defaultValues:
            self.settings.setValue(key, value)
            self.settings.sync()

    def init_QSettings_with_value(self, values={},
                                  resetToDefault=False):
        """
        make all default Settings available to the QSettings Store
        :param values:
        :param resetToDefault:
        :return:
        """
        for key, defaultValue in self.__defaultValues.items():
            if resetToDefault:
                self.settings.setValue(key, value=defaultValue)
            else:
                if key in values:
                    self.settings.setValue(key, value=values.get(key))
        self.settings.sync()

    def clean_settings(self):
        for key in self.settings.allKeys():
            self.settings.remove(key)
        self.settings.sync()

if __name__ == '__main__':
    settings = LocalSettings()
    settings