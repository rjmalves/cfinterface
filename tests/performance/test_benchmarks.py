import gc
import tempfile
from pathlib import Path

import pytest

from cfinterface.components.block import Block
from cfinterface.components.floatfield import FloatField
from cfinterface.components.integerfield import IntegerField
from cfinterface.components.line import Line
from cfinterface.components.literalfield import LiteralField
from cfinterface.components.register import Register
from cfinterface.components.section import Section
from cfinterface.files.blockfile import BlockFile
from cfinterface.files.registerfile import RegisterFile
from cfinterface.files.sectionfile import SectionFile
from tests.performance import BenchmarkRunner, temporary_test_directory
from tests.performance.generators import (
    STANDARD_TEST_CONFIGS,
    BlockFileGenerator,
    FileGenerationParams,
    FileGeneratorFactory,
    RegisterFileGenerator,
    SectionFileGenerator,
)


# Test Register Classes
class LiteralPerfTestRegister(Register):
    IDENTIFIER = "LIT"
    IDENTIFIER_DIGITS = 4
    LINE = Line([
        LiteralField(size=5, starting_position=4),
        LiteralField(size=5, starting_position=10),
        LiteralField(size=5, starting_position=16),
    ])


class IntegerLiteralPerfTestRegister(Register):
    IDENTIFIER = "INT"
    IDENTIFIER_DIGITS = 4
    LINE = Line([
        IntegerField(size=5, starting_position=4),
        IntegerField(size=5, starting_position=10),
        IntegerField(size=5, starting_position=16),
    ])


class FloatLiteralPerfTestRegister(Register):
    IDENTIFIER = "FLO"
    IDENTIFIER_DIGITS = 4
    LINE = Line([
        FloatField(size=5, decimal_digits=2, starting_position=4),
        FloatField(size=5, decimal_digits=2, starting_position=10),
        FloatField(size=5, decimal_digits=2, starting_position=16),
    ])


class PerfTestRegisterFile(RegisterFile):
    REGISTERS = [
        LiteralPerfTestRegister,
        IntegerLiteralPerfTestRegister,
        FloatLiteralPerfTestRegister,
    ]


class PerfTestBlock(Block):
    BEGIN_PATTERN = "BEGIN_DATA"
    END_PATTERN = "END_DATA"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.data == other.data

    def read(self, file):
        self.data = []
        while True:
            line = file.readline()
            if not line:
                break
            line = line.strip()
            if self.ends(line):
                break
            self.data.append(line)
        return True

    def write(self, file):
        if hasattr(self, "data") and self.data:
            for line in self.data:
                file.write(f"{line}\n")
        return True


class PerfTestBlockFile(BlockFile):
    BLOCKS = [PerfTestBlock]


class PerfTestSection(Section):
    BEGIN_PATTERN = "[DATA]"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.data == other.data

    def read(self, file):
        self.data = []
        while True:
            line = file.readline()
            if not line:
                break
            line = line.strip()
            if (
                line.startswith("[")
                and line.endswith("]")
                and line != self.BEGIN_PATTERN
            ):
                file.seek(file.tell() - len(line) - 1)
                break
            if line and line != self.BEGIN_PATTERN:
                self.data.append(line)
        return True

    def write(self, file):
        if hasattr(self, "data") and self.data:
            for line in self.data:
                file.write(f"{line}\n")
        return True


class PerfTestSectionFile(SectionFile):
    SECTIONS = [PerfTestSection]


class TestPerformanceBenchmarks:
    @pytest.fixture(scope="class")
    def benchmark_runner(self, results_dir: Path):
        runner = BenchmarkRunner(results_dir=results_dir)
        yield runner

    @pytest.fixture(scope="class")
    def test_files(self):
        with temporary_test_directory() as temp_dir:
            files = FileGeneratorFactory.generate_test_files(
                temp_dir, STANDARD_TEST_CONFIGS
            )
            yield files

    @pytest.mark.performance
    def test_registerfile_read_small(self, benchmark_runner, test_files):
        @benchmark_runner.benchmark(
            "RegisterFile.read_small", iterations=10, file_size="10KB"
        )
        def read_small_register():
            file_path = test_files["small_register"]
            result = PerfTestRegisterFile.read(str(file_path))
            return len(result.data)

        read_small_register()

    @pytest.mark.performance
    def test_registerfile_read_medium(self, benchmark_runner, test_files):
        @benchmark_runner.benchmark(
            "RegisterFile.read_medium", iterations=5, file_size="100KB"
        )
        def read_medium_register():
            file_path = test_files["medium_register"]
            result = PerfTestRegisterFile.read(str(file_path))
            return len(result.data)

        read_medium_register()

    @pytest.mark.performance
    @pytest.mark.slow
    def test_registerfile_read_large(self, benchmark_runner, test_files):
        @benchmark_runner.benchmark(
            "RegisterFile.read_large", iterations=3, file_size="1MB"
        )
        def read_large_register():
            file_path = test_files["large_register"]
            result = PerfTestRegisterFile.read(str(file_path))
            return len(result.data)

        read_large_register()

    @pytest.mark.performance
    @pytest.mark.slow
    def test_registerfile_read_xlarge(self, benchmark_runner, test_files):
        @benchmark_runner.benchmark(
            "RegisterFile.read_xlarge", iterations=1, file_size="10MB"
        )
        def read_xlarge_register():
            file_path = test_files["xlarge_register"]
            result = PerfTestRegisterFile.read(str(file_path))
            return len(result.data)

        read_xlarge_register()

    @pytest.mark.performance
    def test_registerfile_write_medium(self, benchmark_runner):
        @benchmark_runner.benchmark(
            "RegisterFile.write_medium", iterations=5, file_size="100KB"
        )
        def write_medium_register():
            temp_path = Path(tempfile.mkdtemp()) / "register_write_medium.txt"

            generator = RegisterFileGenerator(
                FileGenerationParams(file_size_kb=100, register_count=1000)
            )

            generated_file = generator.generate(temp_path)
            return generated_file.stat().st_size

        write_medium_register()

    @pytest.mark.performance
    def test_blockfile_read_small(self, benchmark_runner, test_files):
        @benchmark_runner.benchmark(
            "BlockFile.read_small", iterations=10, file_size="10KB"
        )
        def read_small_block():
            file_path = test_files["small_block"]
            result = PerfTestBlockFile.read(str(file_path))
            return len(result.data)

        read_small_block()

    @pytest.mark.performance
    def test_blockfile_read_medium(self, benchmark_runner, test_files):
        @benchmark_runner.benchmark(
            "BlockFile.read_medium", iterations=5, file_size="100KB"
        )
        def read_medium_block():
            file_path = test_files["medium_block"]
            result = PerfTestBlockFile.read(str(file_path))
            return len(result.data)

        read_medium_block()

    @pytest.mark.performance
    @pytest.mark.slow
    def test_blockfile_read_large(self, benchmark_runner, test_files):
        @benchmark_runner.benchmark(
            "BlockFile.read_large", iterations=3, file_size="1MB"
        )
        def read_large_block():
            file_path = test_files["large_block"]
            result = PerfTestBlockFile.read(str(file_path))
            return len(result.data)

        read_large_block()

    @pytest.mark.performance
    def test_blockfile_write_medium(self, benchmark_runner):
        @benchmark_runner.benchmark(
            "BlockFile.write_medium", iterations=5, file_size="100KB"
        )
        def write_medium_block():
            temp_path = Path(tempfile.mkdtemp()) / "block_write_medium.txt"

            generator = BlockFileGenerator(
                FileGenerationParams(file_size_kb=100, block_count=50)
            )

            generated_file = generator.generate(temp_path)
            return generated_file.stat().st_size

        write_medium_block()

    @pytest.mark.performance
    def test_sectionfile_read_small(self, benchmark_runner, test_files):
        @benchmark_runner.benchmark(
            "SectionFile.read_small", iterations=10, file_size="10KB"
        )
        def read_small_section():
            file_path = test_files["small_section"]
            result = PerfTestSectionFile.read(str(file_path))
            return len(result.data)

        read_small_section()

    @pytest.mark.performance
    def test_sectionfile_read_medium(self, benchmark_runner, test_files):
        @benchmark_runner.benchmark(
            "SectionFile.read_medium", iterations=5, file_size="100KB"
        )
        def read_medium_section():
            file_path = test_files["medium_section"]
            result = PerfTestSectionFile.read(str(file_path))
            return len(result.data)

        read_medium_section()

    @pytest.mark.performance
    @pytest.mark.slow
    def test_sectionfile_read_large(self, benchmark_runner, test_files):
        @benchmark_runner.benchmark(
            "SectionFile.read_large", iterations=3, file_size="1MB"
        )
        def read_large_section():
            file_path = test_files["large_section"]
            result = PerfTestSectionFile.read(str(file_path))
            return len(result.data)

        read_large_section()

    @pytest.mark.performance
    def test_sectionfile_write_medium(self, benchmark_runner):
        @benchmark_runner.benchmark(
            "SectionFile.write_medium", iterations=5, file_size="100KB"
        )
        def write_medium_section():
            temp_path = Path(tempfile.mkdtemp()) / "section_write_medium.txt"

            generator = SectionFileGenerator(
                FileGenerationParams(file_size_kb=100, section_count=20)
            )

            generated_file = generator.generate(temp_path)
            return generated_file.stat().st_size

        write_medium_section()

    def teardown_method(self, method):
        gc.collect()
