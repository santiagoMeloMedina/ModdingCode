import enum
from typing import List, Optional, Tuple
import paramiko
from io import StringIO
from modding.problem import models
from modding.common import settings


class LanguageTypes(enum.Enum):
    PYTHON3 = "PYTHON3"


class Language:
    TYPE_MAPPING = {LanguageTypes.PYTHON3: ("py", "python3")}

    def __init__(self, ext: str, command: str):
        self.ext = ext
        self.command = command

    @classmethod
    def get_by_type(cls, _type: str):
        language_type = LanguageTypes(_type.upper())
        ext, command = cls.TYPE_MAPPING.get(language_type)
        return cls(ext, command)


class Analizer:
    class _Settings(settings.Settings):
        instance_public_dns: str
        instance_username: str
        instance_private_key: str

    def __init__(self):
        self._settings = self._Settings()
        self.ssh_client = paramiko.SSHClient()
        self.private_key = self.__set_private_key()
        self.__connect_ssh()

    def __set_private_key(self):
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.RSAKey.from_private_key(
            StringIO(self._settings.instance_private_key)
        )
        return private_key

    def __connect_ssh(self):
        self.ssh_client.connect(
            self._settings.instance_public_dns,
            username=self._settings.instance_username,
            pkey=self.private_key,
        )

    def _store_file(self, folder: str, file_name: str, file_value: str) -> None:
        self.sftp_client = self.ssh_client.open_sftp()
        try:
            self.sftp_client.chdir(folder)
        except:
            self.sftp_client.mkdir(folder)
            self.sftp_client.chdir(folder)
        finally:
            file = self.sftp_client.file(file_name, "a", -1)
            file.write(file_value)
            file.flush()

        self.sftp_client.close()

    def _exec_command(
        self, command: str, case_id: str = str()
    ) -> Optional[Tuple[str, str]]:
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        stdin.flush()
        if case_id:
            return (case_id, stdout.read().decode())

    def _run(
        self, id: str, lang: Language, code: str, files: List[models.ProblemInputFile]
    ) -> List[Tuple[str, str]]:
        results = []

        wrap_folder = lambda name: f"{id}/{name}"

        code_name = "code.%s" % (lang.ext)
        self._store_file(id, code_name, code)

        output_name = lambda i: wrap_folder("%s_code.out" % (i))
        in_name = lambda i: "%s.in" % (i)
        out_name = lambda i: "%s.out" % (i)

        for i in range(len(files)):
            file = files[i]
            if file.input_data and file.output_data:
                self._store_file(id, in_name(i), file.input_data)
                self._store_file(id, out_name(i), file.output_data)

        for i in range(len(files)):
            file = files[i]
            running = "%s %s < %s > %s" % (
                lang.command,
                wrap_folder(code_name),
                wrap_folder(in_name(i)),
                output_name(i),
            )
            comparing = "diff %s %s" % (output_name(i), wrap_folder(out_name(i)))
            self._exec_command(running)
            results.append(self._exec_command(comparing, file.id))

        self._exec_command("rm -r %s" % (id))

        return results

    def _decide_veredict(
        self, results: List[Tuple[str, str]], evaluation: models.ProblemEvaluation
    ) -> None:
        inputs_veredict: List[models.InputVeredict] = []
        for result in results:
            case_id, diffs = result
            inputs_veredict.append(
                models.InputVeredict(
                    id=case_id,
                    veredict=models.ProblemVeredict.SOLVED
                    if not diffs
                    else models.ProblemVeredict.FAILED,
                )
            )

        evaluation.inputs_veredict = inputs_veredict
        evaluation.veredict = (
            models.ProblemVeredict.SOLVED
            if all(
                [
                    veredict.veredict == models.ProblemVeredict.SOLVED.value
                    for veredict in inputs_veredict
                ]
            )
            else models.ProblemVeredict.FAILED
        )

        if evaluation.veredict == models.ProblemVeredict.FAILED.value:
            evaluation.veredict_reason = [
                veredict.id
                for veredict in evaluation.inputs_veredict
                if veredict.veredict == models.ProblemVeredict.FAILED.value
            ]

    def analyze(
        self,
        evaluation: models.ProblemEvaluation,
        file_input: str,
        file_type: str,
        files: List[models.ProblemInputFile],
    ):
        language = Language.get_by_type(file_type)
        kwargs = {
            "id": evaluation.id,
            "code": file_input,
            "lang": language,
            "files": files,
        }

        results = self._run(**kwargs)

        self.ssh_client.close()

        self._decide_veredict(results, evaluation)
