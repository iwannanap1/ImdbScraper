from abc import ABC, abstractmethod
from qrlib.QRObserver import QRPublisher
from qrlib.QREnv import QREnv
from qrlib.QRDecorators import run_item
from qrlib.QRQueue import QRQueue
from qrlib.QRStorageBucket import QRStorageBucket
from qrlib.QRRunItem import QRRunItem
import qrlib.QRUtils


class QRBot(ABC, QRPublisher):

    def __init__(self):
        for base_class in QRBot.__bases__:
             base_class.__init__(self)

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def teardown(self):
        pass

    @run_item(is_ticket=False, post_error=False)
    def setup_platform_components(self, *args, **kwargs):
        run_item: QRRunItem = kwargs['run_item']
        for vault_name in QREnv.VAULT_NAMES:
            try:
                QREnv.VAULTS[vault_name] = qrlib.QRUtils.get_secret(vault_name)
                run_item.logger.info(f"Retrieved vault: {vault_name}")
            except Exception as e:
                run_item.logger.error(f"Failed to retrieve vault: {vault_name}")
                run_item.notification.set(subject=f"Warning! {QREnv.BOT_NAME} bot has stopped unexpectedly", data={"reason":f"Failed to retrieve vault: {vault_name}"})
                raise e

        for queue_name in QREnv.QUEUE_NAMES:
            try:
                queue = QRQueue(queue_name)
                queue.get_info()
                QREnv.QUEUES[queue_name] = queue
                run_item.logger.info(f"Retrieved queue info: {queue_name}")
            except Exception as e:
                run_item.logger.error(f"Failed to retrieve queue info: {queue_name}")
                run_item.notification.set(subject=f"Warning! {QREnv.BOT_NAME} bot has stopped unexpectedly", data={"reason":f"Failed to retrieve queue info: {queue_name}"})
                raise e

        for storage_name in QREnv.STORAGE_NAMES:
            try:
                storage = QRStorageBucket(storage_name)
                storage.get_info()
                QREnv.STORAGES[storage_name] = storage
                run_item.logger.info(f"Retrieved storage info: {storage_name}")
            except Exception as e:
                run_item.logger.error(f"Failed to retrieve storage info: {storage_name}")
                run_item.notification.set(subject=f"Warning! {QREnv.BOT_NAME} bot has stopped unexpectedly", data={"reason":f"Failed to retrieve storage info: {storage_name}"})
                raise e

