from dataclasses import dataclass

@dataclass
class StorageDevice:
    used_storage: float
    total_storage: float
    unit_of_measurement: str
    free_storage   : float

    def get_utilization_percentage(self, decimal_precision: int) -> float:
        return round(self.used_storage / self.total_storage, decimal_precision)

    