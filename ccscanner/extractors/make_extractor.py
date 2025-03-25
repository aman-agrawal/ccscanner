import logging
from ccscanner.extractors.extractor import Extractor
from ccscanner.extractors.dependency import Dependency
from ccscanner.utils.utils import read_lines, read_txt, remove_lstrip
from ccscanner.parser.mkparse import Parser
from ccscanner.parser.libparse import extract_libraries
from pathlib import Path

logging.basicConfig()
logger = logging.getLogger(__name__)
    
class MakeExtractor(Extractor):
    def __init__(self, target) -> None:
        super().__init__()
        self.type = 'make'
        self.target = target

    def run_extractor(self):
        self.parse_make_lib()

    def extract_all_libs(self, result):
        # Extracting from 'libraries'
        all_libraries = [lib for lib in result.get("libraries", []) if lib.startswith("-l")]

        # Extracting from 'direct_library_usage'
        for target, libs in result.get("direct_library_usage", {}).items():
            all_libraries.extend([lib for lib in libs if lib.startswith("-l")])

        # Remove duplicates if needed
        all_libraries = list(set(all_libraries))
        print("\nAll LIBS : ", all_libraries)
        return all_libraries

    def parse_make_lib(self):
        makefile_path = str(Path(self.target).resolve().parent)
        makefile_name = Path(self.target).name
        makefile_parser = Parser(makefile_name, makefile_path)
        targets, variables, comments = makefile_parser.parse_makefile(makefile_name, makefile_path)
        print("\nVariables : ", variables)
        print("\nTargets : ", targets)
        result = extract_libraries(variables, targets)
        print("\nParsed Output : ", result)

        all_libraries = self.extract_all_libs(result)
        for lib in all_libraries:
            if lib.startswith('-l'):
                dep_name = remove_lstrip(lib, '-l')
                new_dep_name = "lib" + dep_name + ".so"
                dep = Dependency(new_dep_name, None)
                dep.add_evidence(self.type, self.target, 'High')
                self.add_dependency(dep)

    # def process_make(self):
    #     lines = read_lines(self.target)
    #     for line in lines:
    #         line = line.strip()
    #         if line.startswith('LDLIBS'):
    #             if '=' not in line:
    #                 continue
    #             libs = line.split('=')[1].split(' ')
    #             for lib in libs:
    #                 if lib.startswith('-l'):
    #                     dep_name = remove_lstrip(lib, '-l')
    #                     dep = Dependency(dep_name, None)
    #                     dep.add_evidence(self.type, self.target+':'+line, 'High')
    #                     self.add_dependency(dep)

    # def process_make_lib(self):
        # makefile_path = "/home/aman/opsmx/cc-scanner/ccscanner/ccscanner/"
        # makefile_name = "Makefile"
        # makefile_parser = Parser(makefile_name, makefile_path)
        # targets, variables, comments = makefile_parser.parse_makefile(makefile_name, makefile_path)
        #
        # print("Targets: {}".format(targets))
        # print("Variables: {}".format(variables))
        # print("Comments: {}".format(comments))

        # lines = read_lines(self.target)
        # for line in lines:
        #     line = line.strip()
        #     if line.startswith('$(CC'):
        #         libs = line.split(' ')
        #         for lib in libs:
        #             if lib.startswith('-l'):
        #                 dep_name = remove_lstrip(lib, '-l')
        #                 new_dep_name = "lib" + dep_name + ".so"
        #                 print(new_dep_name)
        #                 dep = Dependency(new_dep_name, None)
        #                 dep.add_evidence(self.type, self.target+':'+line, 'High')
        #                 self.add_dependency(dep)


