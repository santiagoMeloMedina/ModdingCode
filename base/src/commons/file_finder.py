from typing import Any, Dict, List, Set
import os
import ast


class FileFinder:
    def __init__(self, file_path: str, root_folder: str, env_folder: str = str()):
        self.root = root_folder
        self.file_path = f"{root_folder}/{file_path}"

        self.all_files = self.__find_files(self.root)

        self.included_modules = set([self.file_path])

        self.node_iter = ast.NodeVisitor()
        self.node_iter.visit_Import = self.__visit_Import
        self.node_iter.visit_ImportFrom = self.__visit_ImportFrom

    def __find_files(self, path: str = str()) -> List[str]:
        files, dirs = [], []
        potential_files = os.listdir(path) if len(path) else os.listdir()

        for p_file in potential_files:
            file_path = os.path.join(path, p_file)
            if os.path.isfile(file_path):
                files.append(file_path.replace(".py", "").replace("/", "."))
            else:
                dirs.append(file_path)

        for dir_path in dirs:
            files = files + self.__find_files(dir_path)

        return files

    def __get_excludable_files(self, imported_files: Set[str]) -> List[str]:
        excludable = []
        slash_all_files = [f"{file.replace('.', '/')}.py" for file in self.all_files]
        files_included_state = [
            (file, (file in imported_files or file.endswith("__init__.py")))
            for file in slash_all_files
        ]

        for file, state in files_included_state:
            if not state:
                excludable.append(file)

        return excludable

    def __visit(self, dotted_path: str) -> None:
        full_dotted_path = f"{self.root.replace('/', '.')}.{dotted_path}"

        if full_dotted_path in self.all_files:
            path = f"{full_dotted_path.replace('.', '/')}.py"

            if path not in self.included_modules:
                try:
                    file = open(path, "r")
                    file_data = file.read()
                    file.close()
                    self.included_modules.add(path)
                    self.node_iter.visit(ast.parse(file_data))
                except:
                    raise Exception(
                        "Error importing path, maybe importing folder instead of file"
                    )

    def __visit_Import(self, node: ast.Import) -> None:
        for name in node.names:
            self.__visit(name.name)

    def __visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for name in node.names:
            self.__visit(f"{node.module}.{name.name}")

    def get_excluded_from_file(self) -> List[str]:
        with open(self.file_path) as file:
            self.node_iter.visit(ast.parse(file.read()))

        return self.__get_excludable_files(self.included_modules)
