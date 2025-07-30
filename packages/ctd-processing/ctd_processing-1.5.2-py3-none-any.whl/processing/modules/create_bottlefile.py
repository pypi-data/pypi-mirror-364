from pathlib import Path
from datetime import datetime, timezone
import importlib
import numpy as np
from seabirdfilehandler import CnvFile, BottleLogFile, DataFile


class InvalidArgumentCombination(Exception):
    """Exception raised when an invalid combination of arguments is provided."""

    pass


class OwnBtlFile(DataFile):
    def __init__(
        self,
        cnv: CnvFile | None = None,
        blf: BottleLogFile | None = None,
        path_to_file: Path | str = "",
    ):
        if cnv and blf:
            self.cnv = cnv
            self.blf = blf
            self.data = self.create_btl()
        elif path_to_file:
            # TODO: use DataFile variables and methods to read an existing file
            pass
        else:
            raise InvalidArgumentCombination

    def create_btl(self) -> str:
        req_parameters = [
            "prDM",
            "t090C",
            "t190C",
            "c0mS/cm",
            "c1mS/cm",
            "sbox0Mm/Kg",
            "sbox1Mm/Kg",
            "sal00",
            "sal11",
            "par",
            "spar",
            "flECO-AFL",
            "turbWETntu0",
        ]

        data_averages = self._get_averages()
        btl_file = ""

        names_and_spans = True

        for line in self.cnv.header:
            if line[0] == "#" and names_and_spans:
                if "Sensors" in line:
                    names_and_spans = False
                    btl_file += str(line)
                continue
            if "ascii" in line:
                timestamp = datetime.now(timezone.utc).strftime(
                    "%Y.%m.%d %H:%M:%S"
                )
                btl_file += f"# create_bottlefile_metainfo = {timestamp}, ctd-processing python package, v{importlib.metadata.version('ctd-processing')}\n"

            btl_file += str(line)

        btl_base_id = int(self.cnv.metadata["WsStartID"]) - 1

        line = add_whitespace("Btl_Posn")
        line += add_whitespace("Btl_ID")
        line += add_whitespace("Datetime", 22)
        for i in range(len(req_parameters)):
            line += add_whitespace(req_parameters[i])
        btl_file += line + "\n"

        for i in range(len(self.blf.data_list)):
            line = ""

            line += add_whitespace(self.blf.data_list[i][0][1])
            line += add_whitespace(self.blf.data_list[i][0][1] + btl_base_id)
            line += add_whitespace(self.blf.data_list[i][1], 22)

            for j in range(len(data_averages[0])):
                line += add_whitespace(data_averages[i, j])

            if i == len(self.blf.data_list) - 1:
                btl_file += line
                continue

            btl_file += line + "\n"

        return btl_file

    def _get_averages(self) -> np.ndarray:
        cnv_data = self.cnv.parameters.full_data_array.astype(float)
        par_index_list = self._get_parameters()
        averages = np.array(
            [
                [None for x in range(len(par_index_list))]
                for y in range(len(self.blf.data_list))
            ]
        )

        for i in range(len(self.blf.data_list)):
            for j in range(len(par_index_list)):
                start_index = self.blf.data_list[i][2][0]
                end_index = self.blf.data_list[i][2][1]
                averages[i, j] = np.average(
                    cnv_data[start_index:end_index, j]
                ).round(4)

        return averages

    def _get_parameters(self) -> list:
        """gets the Indices of the required parameterts from the cnv

        Parameters
        ----------
        List of Parameters of the cnv

        Returns
        -------
        list of corresponding indices

        """
        req_parameters = [
            "prDM",
            "t090C",
            "t190C",
            "c0mS/cm",
            "c1mS/cm",
            "sbox0Mm/Kg",
            "sbox1Mm/Kg",
            "sal00",
            "sal11",
            "par",
            "spar",
            "flECO-AFL",
            "turbWETntu0",
        ]
        parameter_list = self.cnv.parameters.get_parameter_list()
        par_shortname_list = [x.name for x in parameter_list]
        par_index_list = []
        for i in range(len(req_parameters)):
            par_index_list.append(par_shortname_list.index(req_parameters[i]))
        return par_index_list


def _check_input(input, type):
    if isinstance(input, CnvFile | BottleLogFile):
        return input
    elif isinstance(input, str):
        if input:
            return type(input)
        else:
            return ""
    elif isinstance(input, Path):
        if input is not Path("."):
            return type(input)
        else:
            return ""
    else:
        raise ValueError(
            f"Argument of {type(input)} cannot be used for {type}"
        )


def create_bottle_file(
    cnv: CnvFile | Path | str = "",
    blf: BottleLogFile | Path | str = "",
    output_path: Path | str = "",
    save=True,
) -> OwnBtlFile:
    cnv = _check_input(cnv, CnvFile)
    blf = _check_input(blf, BottleLogFile)

    if cnv:
        if not blf:
            try:
                blf = BottleLogFile(cnv.path_to_file.with_suffix(".bl"))
            except (FileNotFoundError, ValueError, TypeError):
                raise ValueError(
                    f"Could not find a corresponding .bl file to the cnv {cnv}"
                )
    else:
        if blf:
            try:
                cnv = CnvFile(blf.path_to_file.with_suffix(".cnv"))
            except (FileNotFoundError, ValueError, TypeError):
                raise ValueError(
                    f"Could not find a corresponding .cnv file to the bl {blf}"
                )
        else:
            raise InvalidArgumentCombination

    btl = OwnBtlFile(cnv, blf)

    if save:
        if not output_path:
            output_path = cnv.path_to_file.with_suffix(".obtl")
        with open(output_path, "w") as file:
            file.write(btl.data)

    return btl


def add_whitespace(data, space: int = 11):
    return (space - len(str(data))) * " " + str(data)
