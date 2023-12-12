from dataclasses import dataclass

@dataclass
class StorageDevice:
    used_storage: int
    total_storage: int
    unit_of_measurement: str

    def get_utilization_percentage(self, decimal_precision: int) -> float:
        return round(self.used_storage / self.total_storage, decimal_precision)
