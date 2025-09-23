import random
import string
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class FileGenerationParams:
    file_size_kb: int
    line_count: Optional[int] = None
    block_count: Optional[int] = None
    section_count: Optional[int] = None
    register_count: Optional[int] = None
    encoding: str = "utf-8"


class BaseFileGenerator:
    def __init__(self, params: FileGenerationParams):
        self.params = params
        self.random = random.Random(0)

    def _generate_random_string(self, length: int) -> str:
        return "".join(
            self.random.choices(string.ascii_letters + string.digits, k=length)
        )

    def _generate_random_integer(
        self, min_val: int = 0, max_val: int = 1000
    ) -> int:
        return self.random.randint(min_val, max_val)

    def _generate_random_float(
        self, min_val: float = 0, max_val: float = 100
    ) -> float:
        return round(self.random.uniform(min_val, max_val), 1)

    def _generate_random_date(self) -> str:
        start_date = datetime(1970, 1, 1)
        end_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = self.random.randrange(days_between)
        random_date = start_date + timedelta(days=random_days)
        return random_date.strftime("%Y-%m-%d")


class RegisterFileGenerator(BaseFileGenerator):
    def __init__(self, params: FileGenerationParams):
        super().__init__(params)
        self.register_types = [
            ("LIT", self._generate_random_string),
            ("INT", self._generate_random_integer),
            ("FLO", self._generate_random_float),
        ]

    def generate(self, output_path: Path) -> Path:
        lines = []
        target_size_bytes = self.params.file_size_kb * 1024
        current_size = 0

        register_count = self.params.register_count or max(
            1, self.params.file_size_kb // 10
        )

        for _ in range(register_count):
            prefix, generator = self.random.choice(self.register_types)

            fields = self._generate_register_fields(generator)
            line = f"{prefix} {' '.join(fields)}"

            lines.append(line)
            current_size += len(line.encode(self.params.encoding))

            if current_size >= target_size_bytes:
                break

        # Write to file
        with open(output_path, "w", encoding=self.params.encoding) as f:
            f.write("\n".join(lines))

        return output_path

    def _generate_register_fields(self, generator: Callable) -> List[str]:
        fields = []

        for i in range(3):
            fields.append(str(generator(5)).rjust(5))

        return fields


class BlockFileGenerator(BaseFileGenerator):
    BEGIN_PATTERN = "BEGIN_DATA"
    END_PATTERN = "END_DATA"

    def __init__(self, params: FileGenerationParams):
        super().__init__(params)

    def generate(self, output_path: Path) -> Path:
        lines = []
        target_size_bytes = self.params.file_size_kb * 1024
        current_size = 0

        block_count = self.params.block_count or max(
            1, self.params.file_size_kb // 50
        )

        for _ in range(block_count):
            lines.append(self.BEGIN_PATTERN)
            current_size += len(self.BEGIN_PATTERN.encode(self.params.encoding))

            block_lines = self._generate_block_content()
            lines.extend(block_lines)

            for line in block_lines:
                current_size += len(line.encode(self.params.encoding))

            lines.append(self.END_PATTERN)
            current_size += len(self.END_PATTERN.encode(self.params.encoding))

            if current_size >= target_size_bytes:
                break

        with open(output_path, "w", encoding=self.params.encoding) as f:
            f.write("\n".join(lines))

        return output_path

    def _generate_block_content(self) -> List[str]:
        lines = []
        line_count = self.random.randint(5, 50)

        for _ in range(line_count):
            values = [f"{self._generate_random_float():.2f}" for _ in range(4)]
            lines.append(" ".join(values))

        return lines


class SectionFileGenerator(BaseFileGenerator):
    SECTION_HEADER = "[DATA]"

    def __init__(self, params: FileGenerationParams):
        super().__init__(params)

    def generate(self, output_path: Path) -> Path:
        lines = []
        target_size_bytes = self.params.file_size_kb * 1024
        current_size = 0

        section_count = self.params.section_count or max(
            1, self.params.file_size_kb // 30
        )

        for _ in range(section_count):
            lines.append(self.SECTION_HEADER)
            current_size += len(
                self.SECTION_HEADER.encode(self.params.encoding)
            )

            section_lines = self._generate_section_content()
            lines.extend(section_lines)

            for line in section_lines:
                current_size += len(line.encode(self.params.encoding))

            lines.append("")
            current_size += 1

            if current_size >= target_size_bytes:
                break

        with open(output_path, "w", encoding=self.params.encoding) as f:
            f.write("\n".join(lines))

        return output_path

    def _generate_section_content(self) -> List[str]:
        lines = []
        line_count = self.random.randint(10, 100)

        for i in range(line_count):
            row = [f"{self._generate_random_float():.3f}" for _ in range(5)]
            lines.append("\t".join(row))

        return lines


class FileGeneratorFactory:
    @staticmethod
    def create_generator(
        file_type: str, params: FileGenerationParams
    ) -> BaseFileGenerator:
        generators = {
            "register": RegisterFileGenerator,
            "block": BlockFileGenerator,
            "section": SectionFileGenerator,
        }

        if file_type not in generators:
            raise ValueError(f"Unknown file type: {file_type}")

        return generators[file_type](params)

    @staticmethod
    def generate_test_files(
        temp_dir: Path, file_configs: List[Dict[str, Any]]
    ) -> Dict[str, Path]:
        generated_files = {}

        for config in file_configs:
            file_type = config["type"]
            name = config["name"]

            params = FileGenerationParams(**{
                k: v for k, v in config.items() if k not in ["type", "name"]
            })

            generator = FileGeneratorFactory.create_generator(file_type, params)
            output_path = (
                temp_dir / f"{name}.{'bin' if file_type == 'binary' else 'txt'}"
            )

            generated_files[name] = generator.generate(output_path)

        return generated_files


STANDARD_TEST_CONFIGS = [
    {
        "name": "small_register",
        "type": "register",
        "file_size_kb": 10,
    },
    {
        "name": "small_block",
        "type": "block",
        "file_size_kb": 10,
    },
    {
        "name": "small_section",
        "type": "section",
        "file_size_kb": 10,
    },
    {
        "name": "medium_register",
        "type": "register",
        "file_size_kb": 100,
    },
    {
        "name": "medium_block",
        "type": "block",
        "file_size_kb": 100,
    },
    {
        "name": "medium_section",
        "type": "section",
        "file_size_kb": 100,
    },
    {
        "name": "large_register",
        "type": "register",
        "file_size_kb": 1000,
    },
    {
        "name": "large_block",
        "type": "block",
        "file_size_kb": 1000,
    },
    {
        "name": "large_section",
        "type": "section",
        "file_size_kb": 1000,
    },
    {
        "name": "xlarge_register",
        "type": "register",
        "file_size_kb": 10000,
    },
]
