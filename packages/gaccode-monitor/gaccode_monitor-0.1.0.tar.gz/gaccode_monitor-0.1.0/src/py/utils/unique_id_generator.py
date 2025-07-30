from ast import main
import time
import threading
import json
from utils.constants import CONFIG_FILE
from utils.log_util import default_logger as logger


class UniqueIDGenerator:
    """
    单例模式的唯一ID生成器
    基于时间戳和序列号生成6位唯一ID
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """
        单例模式实现，确保只创建一个UniqueIDGenerator实例

        Returns:
            UniqueIDGenerator: 唯一的类实例
        """
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.initial_time = int(time.time())
                cls._instance.sequence = 0
                cls._instance.load_config()
            return cls._instance

    def load_config(self):
        """
        从配置文件加载初始时间戳和序列号

        Returns:
            None
        """
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                self.config = json.load(f)
                self.initial_time = self.config["id"]["current_value"]
                self.sequence = self.config["id"]["current_value"]

    def save_config(self):
        """
        保存当前配置到配置文件

        Returns:
            None
        """
        self.config["id"]["current_value"] = self.sequence
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)
            logger.info(f"配置已保存到: {CONFIG_FILE},id:{self.sequence}") 

    def generate_id(self):
        """
        生成唯一ID
        Returns:
            str: 6位数字id 100000
        """

        with self._lock:
            self.sequence += 1
            self.save_config()
            logger.info(f"当前ID: {self.sequence}")
            return f"{self.sequence % 1000000:06d}"


def generate_ids(thread_id, count):
    """
    多线程环境下生成多个唯一ID

    Args:
        thread_id (int): 线程ID，用于标识不同线程
        count (int): 需要生成的ID数量
    """
    generator = UniqueIDGenerator()
    results = []
    for _ in range(count):
        results.append(generator.generate_id())
        time.sleep(0.001)
    print(f"线程 {thread_id} 生成的ID: {', '.join(results)}")


def test_thread_generate():
    """
    测试多线程生成ID
    """
    threads = []
    for i in range(10):  # 创建10个线程
        thread = threading.Thread(
            target=generate_ids, args=(i, 10)  # 每个线程生成10个ID
        )
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()


def test_single():
    """
    测试单线程生成ID
    """
    generator = UniqueIDGenerator()
    for i in range(10):
        print(generator.generate_id())


if __name__ == "__main__":
    test_thread_generate()
    # test_single()
