from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

import serial
from serial import Serial

logger = logging.getLogger(__name__)


def send_command(ser: Serial | None, command: str, expected_result_type=None):
    logger.info(f"{' COMMAND START ' :*^40}")
    command = (command + "\r\n").encode("ascii")
    logger.info(f"write: {command}")
    if ser is None:
        reply = None
    else:
        ser.write(command)
        reply = ser.readline()
        logger.info(f"reply: {reply}")
        # next 4 lines are due to a bug in QTCs firmware. Some commands return 'on/off' instead of '1/0'
        if reply == b"On\r\n":
            reply = "1"
        if reply == b"Off\r\n":
            reply = "0"
        if expected_result_type is not None:
            try:
                reply = expected_result_type(reply)
            except ValueError:
                logger.info(f"Couldn't convert {reply} to {expected_result_type}")
    logger.info(f"{' COMMAND END ' :*^40}\n")
    return reply


class Channel:
    def __init__(self, number, ser=None):
        self.number = number
        self.ser = ser

    def _send_command(self, command, arg=None, expected_result_type=float):
        command = f"{command} {self.number} {'' if arg is None else arg}"
        return send_command(self.ser, command, expected_result_type)

    @property
    def TempSet(self) -> float:
        return self._send_command(f"TempSet?")

    @TempSet.setter
    def TempSet(self, value: float):
        self._send_command(f"TempSet", value)

    @property
    def Temp(self) -> float:
        return self._send_command(f"Temp?")

    @property
    def TError(self):
        return self._send_command(f"TError?")

    @property
    def TempMin(self) -> float:
        return self._send_command("TempMin?")

    @TempMin.setter
    def TempMin(self, value: float):
        self._send_command("TempMin", value)

    @property
    def TempMax(self) -> float:
        return self._send_command("TempMax?")

    @TempMax.setter
    def TempMax(self, value: float):
        self._send_command("TempMax", value)

    @property
    def Bipolar(self) -> int:
        return self._send_command("Bipolar?", expected_result_type=int)

    @Bipolar.setter
    def Bipolar(self, value: int):
        self._send_command("Bipolar", value, expected_result_type=int)

    @property
    def MaxCurr(self) -> float:
        return self._send_command("MaxCurr?")

    @MaxCurr.setter
    def MaxCurr(self, value: float):
        self._send_command("MaxCurr", value)

    @property
    def Current(self) -> float:
        return self._send_command("Current?")

    @Current.setter
    def Current(self, value: float):
        self._send_command("Currset", value)

    @property
    def MaxPwr(self) -> float:
        return self._send_command("MaxPwr?")

    @MaxPwr.setter
    def MaxPwr(self, value: float):
        self._send_command("MaxPwr", value)

    @property
    def Power(self) -> float:
        return self._send_command("Power?")

    @property
    def CVolt(self):
        return self._send_command("CVolt?")

    @property
    def Beta(self) -> float:
        return self._send_command("Beta?")

    @Beta.setter
    def Beta(self, value: float):
        self._send_command("Beta", value)

    @property
    def RefTemp(self) -> float:
        return self._send_command("RefTemp?")

    @RefTemp.setter
    def RefTemp(self, value: float):
        self._send_command("RefTemp", value)

    @property
    def RefRes(self) -> float:
        return self._send_command("RefRes?")

    @RefRes.setter
    def RefRes(self, value: float):
        self._send_command("RefRes", value)

    @property
    def TCoefA(self) -> float:
        return self._send_command("TCoefA?")

    @TCoefA.setter
    def TCoefA(self, value: float):
        self._send_command("TCoefA", value)

    @property
    def TCoefB(self) -> float:
        return self._send_command("TCoefB?")

    @TCoefB.setter
    def TCoefB(self, value: float):
        self._send_command("TCoefB", value)

    @property
    def TCoefC(self) -> float:
        return self._send_command("TCoefC?")

    @TCoefC.setter
    def TCoefC(self, value: float):
        self._send_command("TCoefC", value)

    def TEMPLUT(self):
        self._send_command("TEMPLUT")

    @property
    def Control(self) -> int:
        return self._send_command("Control?", expected_result_type=int)

    @Control.setter
    def Control(self, value: int):
        self._send_command("Control", arg=value, expected_result_type=int)

    @property
    def PGain(self) -> float:
        return self._send_command("PGain?")

    @PGain.setter
    def PGain(self, value: float):
        self._send_command("PGain", value)

    @property
    def Integ(self) -> float:
        return self._send_command("Integ?")

    @Integ.setter
    def Integ(self, value: float):
        self._send_command("Integ", value)

    @property
    def Deriv(self) -> float:
        return self._send_command("Deriv?")

    @Deriv.setter
    def Deriv(self, value: float):
        self._send_command("Deriv", value)

    @property
    def Slew(self) -> float:
        return self._send_command("Slew?")

    @Slew.setter
    def Slew(self, value: float):
        self._send_command("Slew", value)

    @property
    def DerivEn(self) -> int:
        return self._send_command("DerivEn?", expected_result_type=int)

    @DerivEn.setter
    def DerivEn(self, value: int):
        self._send_command("DerivEn", value, expected_result_type=int)

    @property
    def PGainEn(self) -> int:
        return self._send_command("PGainEn?", expected_result_type=int)

    @PGainEn.setter
    def PGainEn(self, value: int):
        self._send_command("PGainEn", value, expected_result_type=int)

    @property
    def IntegEn(self) -> int:
        return self._send_command("IntegEn?", expected_result_type=int)

    @IntegEn.setter
    def IntegEn(self, value: int):
        self._send_command("IntegEn", value, expected_result_type=int)

    @property
    def SlewEn(self) -> int:
        return self._send_command("SlewEn?", expected_result_type=int)

    @SlewEn.setter
    def SlewEn(self, value: int):
        self._send_command("SlewEn", value, expected_result_type=int)


class Slice:
    def __init__(self, port="/dev/vescent", debug=False):
        """
        Creates Slice object

        Args:
            port (str): serial port for connection
            debug (bool): if True, debug mode is on. No commands are send via serial port.
        """
        self.debug = debug
        self.port = port

        self.ser = None
        self._connect()

        self.ch1 = Channel(1, self.ser)
        self.ch2 = Channel(2, self.ser)
        self.ch3 = Channel(3, self.ser)
        self.ch4 = Channel(4, self.ser)

    def _connect(self):
        if not self.debug:
            self.ser = serial.Serial(self.port, timeout = 1)
        else:
            logger.info("DEBUG MODE  -  no commands send to device")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ser is not None:
            try:
                self.ser.close()
            except serial.SerialException:
                pass

    def __del__(self):
        if self.ser is not None:
            try:
                self.ser.close()
            except serial.SerialException:
                pass

    def _send_command(self, command, expected_result_type):
        return send_command(self.ser, command, expected_result_type)

    def _loop_over_channels(
        self, attribute_name: str, values: Any | Sequence[Any, Any, Any, Any]
    ):
        values_iter = values if isinstance(values, Iterable) else [values] * 4
        assert len(values_iter) == 4
        for channel, val in enumerate(values_iter, start=1):
            if val is not None:
                setattr(getattr(self, f"ch{channel}"), attribute_name, val)

    @property
    def Temp(self) -> (float, float, float, float):
        return self.ch1.Temp, self.ch2.Temp, self.ch3.Temp, self.ch4.Temp

    @property
    def TempSet(self) -> (float, float, float, float):
        return self.ch1.TempSet, self.ch2.TempSet, self.ch3.TempSet, self.ch4.TempSet

    @TempSet.setter
    def TempSet(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("TempSet", values)

    @property
    def TError(self) -> (float, float, float, float):
        return self.ch1.TError, self.ch2.TError, self.ch3.TError, self.ch4.TError

    @property
    def Bipolar(self) -> (int, int, int, int):
        return self.ch1.Bipolar, self.ch2.Bipolar, self.ch3.Bipolar, self.ch4.Bipolar

    @Bipolar.setter
    def Bipolar(self, values: int | Sequence[int, int, int, int]):
        self._loop_over_channels("Bipolar", values)

    @property
    def MaxPwr(self) -> (float, float, float, float):
        return self.ch1.MaxPwr, self.ch2.MaxPwr, self.ch3.MaxPwr, self.ch4.MaxPwr

    @MaxPwr.setter
    def MaxPwr(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("MaxPwr", values)

    @property
    def Power(self) -> (float, float, float, float):
        return self.ch1.Power, self.ch2.Power, self.ch3.Power, self.ch4.Power

    @property
    def CVolt(self) -> (float, float, float, float):
        return self.ch1.CVolt, self.ch2.CVolt, self.ch3.CVolt, self.ch4.CVolt

    @property
    def Beta(self) -> (float, float, float, float):
        return self.ch1.Beta, self.ch2.Beta, self.ch3.Beta, self.ch4.Beta

    @Beta.setter
    def Beta(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("Beta", values)

    @property
    def RefTemp(self) -> (float, float, float, float):
        return self.ch1.RefTemp, self.ch2.RefTemp, self.ch3.RefTemp, self.ch4.RefTemp

    @RefTemp.setter
    def RefTemp(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("RefTemp", values)

    @property
    def RefRes(self) -> (float, float, float, float):
        return self.ch1.RefRes, self.ch2.RefRes, self.ch3.RefRes, self.ch4.RefRes

    @RefRes.setter
    def RefRes(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("RefRes", values)

    @property
    def TCoefA(self) -> (float, float, float, float):
        return self.ch1.TCoefA, self.ch2.TCoefA, self.ch3.TCoefA, self.ch4.TCoefA

    @TCoefA.setter
    def TCoefA(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("TCoefA", values)

    @property
    def TCoefB(self) -> (float, float, float, float):
        return self.ch1.TCoefB, self.ch2.TCoefB, self.ch3.TCoefB, self.ch4.TCoefB

    @TCoefB.setter
    def TCoefB(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("TCoefB", values)

    @property
    def TCoefC(self) -> (float, float, float, float):
        return self.ch1.TCoefC, self.ch2.TCoefC, self.ch3.TCoefC, self.ch4.TCoefC

    @TCoefC.setter
    def TCoefC(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("TCoefC", values)

    @property
    def TempMin(self) -> (float, float, float, float):
        return self.ch1.TempMin, self.ch2.TempMin, self.ch3.TempMin, self.ch4.TempMin

    @TempMin.setter
    def TempMin(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("TempMin", values)

    @property
    def TempMax(self) -> (float, float, float, float):
        return self.ch1.TempMax, self.ch2.TempMax, self.ch3.TempMax, self.ch4.TempMax

    @TempMax.setter
    def TempMax(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("TempMax", values)

    def TEMPLUT(self):
        self.ch1.TEMPLUT()
        self.ch2.TEMPLUT()
        self.ch3.TEMPLUT()
        self.ch4.TEMPLUT()

    @property
    def Control(self) -> (str, str, str, str):
        return self.ch1.Control, self.ch2.Control, self.ch3.Control, self.ch4.Control

    @Control.setter
    def Control(self, values: Sequence[str, str, str, str]):
        self._loop_over_channels("Control", values)

    @property
    def PGain(self) -> (float, float, float, float):
        return self.ch1.PGain, self.ch2.PGain, self.ch3.PGain, self.ch4.PGain

    @PGain.setter
    def PGain(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("PGain", values)

    @property
    def Integ(self) -> (float, float, float, float):
        return self.ch1.Integ, self.ch2.Integ, self.ch3.Integ, self.ch4.Integ

    @Integ.setter
    def Integ(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("Integ", values)

    @property
    def Deriv(self) -> (float, float, float, float):
        return self.ch1.Deriv, self.ch2.Deriv, self.ch3.Deriv, self.ch4.Deriv

    @Deriv.setter
    def Deriv(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("Deriv", values)

    @property
    def Slew(self) -> (float, float, float, float):
        return self.ch1.Slew, self.ch2.Slew, self.ch3.Slew, self.ch4.Slew

    @Slew.setter
    def Slew(self, values: float | Sequence[float, float, float, float]):
        self._loop_over_channels("Slew", values)

    @property
    def DerivEn(self) -> (int, int, int, int):
        return self.ch1.DerivEn, self.ch2.DerivEn, self.ch3.DerivEn, self.ch4.DerivEn

    @DerivEn.setter
    def DerivEn(self, values: int | Sequence[int, int, int, int]):
        self._loop_over_channels("DerivEn", values)

    @property
    def PGainEn(self) -> (int, int, int, int):
        return self.ch1.PGainEn, self.ch2.PGainEn, self.ch3.PGainEn, self.ch4.PGainEn

    @PGainEn.setter
    def PGainEn(self, values: int | Sequence[int, int, int, int]):
        self._loop_over_channels("PGainEn", values)

    @property
    def IntegEn(self) -> (int, int, int, int):
        return self.ch1.IntegEn, self.ch2.IntegEn, self.ch3.IntegEn, self.ch4.IntegEn

    @IntegEn.setter
    def IntegEn(self, values: int | Sequence[int, int, int, int]):
        self._loop_over_channels("IntegEn", values)

    @property
    def SlewEn(self) -> (int, int, int, int):
        return self.ch1.SlewEn, self.ch2.SlewEn, self.ch3.SlewEn, self.ch4.SlewEn

    @SlewEn.setter
    def SlewEn(self, values: int | Sequence[int, int, int, int]):
        self._loop_over_channels("SlewEn", values)

    @property
    def IDN(self) -> str:
        return self._send_command("*IDN?", str)

    @property
    def serial(self) -> int:
        idn = self.IDN
        return int(idn.split(",")[2]) if idn is not None else None

    @property
    def version(self) -> float:
        return self._send_command("#VERSION", float)

    def save(self):
        return self._send_command("Save", str)

    @property
    def Output1(self) -> str:
        return self._send_command("Output1?", str)

    @Output1.setter
    def Output1(self, value: str):
        self._send_command(f"Output1 {value}", str)

    @property
    def Output2(self) -> str:
        return self._send_command("Output1?", str)

    @Output2.setter
    def Output2(self, value: str):
        self._send_command(f"Output2 {value}", str)

    @property
    def InputA(self) -> str:
        return self._send_command("InputA?", str)

    @InputA.setter
    def InputA(self, value: str):
        self._send_command(f"InputA {value}", str)

    @property
    def InputB(self) -> str:
        return self._send_command("InputB?", str)

    @InputB.setter
    def InputB(self, value: str):
        self._send_command(f"InputB {value}", str)

    def save_json(self, path: str | Path):
        qtc_settings = {}
        # setting keys for properties that can be set. The same for all channels.
        setting_keys = [
            attr
            for attr, value in vars(Channel).items()
            if isinstance(value, property) and value.fset is not None
        ]
        for channel in ["ch1", "ch2", "ch3", "ch4"]:
            # read in current setting values for each channel
            setting_values = [getattr(getattr(self, channel), s) for s in setting_keys]
            settings_dict = dict(zip(setting_keys, setting_values))
            qtc_settings.update({channel: settings_dict})

        with open(path, "w") as fp:
            json.dump(qtc_settings, fp, indent=4, sort_keys=True)

    def load_json(self, path: str | Path, autosave: bool = True):
        with open(path, "r") as json_data:
            qtc_settings = json.load(json_data)
            for channel in qtc_settings:
                for setting_key, setting_value in qtc_settings[channel].items():
                    setattr(getattr(self, channel), setting_key, setting_value)
        if autosave:
            self.save()

    def print_status(
        self,
        temperatures: bool = True,
        pid: bool = False,
        channels: Sequence = (1, 2, 3, 4),
    ):
        print(f'{"":=<62}')
        print(f"         ", end="")
        for c in channels:
            print(f"| Channel {c}".ljust(13), end="")
        print("|")

        def print_row(attribute):
            print(f"{attribute}|".rjust(10), end="")
            for ch_nr in channels:
                channel = getattr(self, f"ch{ch_nr}")
                val = getattr(channel, attribute)
                if val is not None:
                    print(f"{val:.4f}|".rjust(13), end="")
                else:
                    print(f"---.----|".rjust(13), end="")
            print("")

        print(f'{"":=<{13 * len(channels) + 10}}')
        if temperatures:
            print_row("Temp")
            print_row("TempSet")
            print_row("TError")
        if pid:
            print(f'{"":=<{13 * len(channels) + 10}}')
            print_row("PGain")
            print_row("PGainEn")
            print(f'{"":-<{13 * len(channels) + 10}}')
            print_row("Integ")
            print_row("IntegEn")
            print(f'{"":-<{13 * len(channels) + 10}}')
            print_row("Deriv")
            print_row("DerivEn")
            print(f'{"":-<{13 * len(channels) + 10}}')
            print_row("Slew")
            print_row("SlewEn")
            print(f'{"":-<{13 * len(channels) + 10}}')
            print_row("Control")
        print(f'{"":=<{13 * len(channels) + 10}}')


def generate_parser():
    parser = argparse.ArgumentParser(
        prog="Slice-QTC",
        description="Interactive communication with Vescent Slice QTC Temperature controller",
    )

    parser.add_argument("path", help="device path, e.g. /dev/ttyACM0 ")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        required=False,
        help="Debug mode. When set, no commands are sent to serial port",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        required=False,
        help="Verbose mode. When set, all raw responses will be print to the console ",
    )
    return parser


def interactive_mode(args=None):
    if not args:
        args = sys.argv[1:]
    parser = generate_parser()
    args = parser.parse_args(args)

    from IPython import embed

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

    qtc = Slice(args.path, args.debug)

    print(
        f"{'':*<70}\nWelcome to the interactive mode of slice-qtc.\n"
        f"Use the qtc object to interact with the Slice. e.g. write \n\nqtc.ch1.Temp \n\nto print the "
        f"current temperature of channel 1 \n"
        f"{'':*<70}\n"
    )
    embed()


if __name__ == "__main__":
    interactive_mode()
