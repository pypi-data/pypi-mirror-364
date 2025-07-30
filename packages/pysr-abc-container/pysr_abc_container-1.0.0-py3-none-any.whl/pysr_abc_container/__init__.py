from typing import Any
from abc import ABC, abstractmethod


class ABCContainer(ABC):
    """
    Описывает интерфейс контейнера, который предоставляет методы для чтения его записей.
    """

    @abstractmethod
    def get(self, name: str) -> Any:
        """
        Находит запись в контейнере по идентификатору и возвращает её.

        :param name: Идентификатор записи для поиска
        :raises NotFoundExceptionInterface: Если запись не найдена
        :raises ContainerExceptionInterface: Ошибка при получении записи
        :return: Запись любого типа
        """
        pass

    @abstractmethod
    def has(self, name: str) -> bool:
        """
        Возвращает True, если контейнер может вернуть запись по данному идентификатору.
        Возвращает False в противном случае.

        Возврат True не гарантирует, что get(name) не вызовет исключение.
        Однако это означает, что get(name) не вызовет NotFoundExceptionInterface.

        :param name: Идентификатор записи для проверки
        :return: bool
        """
        pass


class ContainerError(Exception):
    """
    Общее исключение в контейнере.
    """
    pass


class NotFoundError(ContainerError):
    """
    Запись не найдена в контейнере.
    """
    pass