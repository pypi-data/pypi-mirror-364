![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/STuermer/slice-qtc/test.yaml?style=flat-square)
![Coveralls](https://img.shields.io/coverallsCoverage/github/Stuermer/slice-qtc?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/slice-qtc?style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/slice-qtc?style=flat-square)
![GitHub issues](https://img.shields.io/github/issues-raw/Stuermer/slice-qtc?style=flat-square)
![GitHub](https://img.shields.io/github/license/Stuermer/slice-qtc?style=flat-square)

# SLICE-QTC

A python package to communicate with a VESCENT Slice-QTC temperature controller.

This package wraps the serial API of the Vescent Slice temperature
controller [Vescent Slice temperature controller](https://vescent.com/de/slice-qtc-four-channel-temperature-controller.html)
to a python class for convenient communication.

All serial commands are implemented as class properties.

**Warning**: The software currently only works with firmware version 2.22. Earlier firmware versions are not supported!

## Usage

Basic usage is to create an instance of the Slice class and access its attributes:

```python
import slice

qtc = slice.Slice()

# read current temperature of channel 1
print(qtc.ch1.Temp)

# change set point of channel 2 
qtc.ch2.SetTemp = 19.040
```

You can also read/set the values for all 4 channels simultaneously:

```python
import slice

qtc = slice.Slice()

# prints a tuple like (20.34, 20.50, 30.1, 10.0)
print(qtc.Temp)

# Sets the setpoint temperature of all 4 channels. Channel 3 will be ignored since 'None' was passed
qtc.SetTemp = (20.5, 21., None, 30.)

# If all channels should receive the identical settings, you can also do:
qtc.PGain = 5.5
```

For convenience, all channel settings can be exported to and imported from a JSON file:

```python
import slice

qtc = slice.Slice()
# save all channel settings to a JSON file
qtc.save_json('channel_settings.json')
```

This will create a JSON file containing all settings per channel.
<details>
<summary>Example JSON</summary>

```json
{
  "ch1": {
    "Beta": 3450.0,
    "Bipolar": 0,
    "Control": 0,
    "Current": 0.0,
    "Deriv": 0.0,
    "DerivEn": 0,
    "Integ": 20.0,
    "IntegEn": 1,
    "MaxCurr": 1.0,
    "MaxPwr": 4.0,
    "PGain": 5.0,
    "PGainEn": 1,
    "RefRes": 10000.0,
    "RefTemp": 25.0,
    "Slew": 0.0,
    "SlewEn": 0,
    "TCoefA": 0.000684,
    "TCoefB": 0.00029,
    "TCoefC": 0.0,
    "TempMax": 50.0,
    "TempMin": -5.0,
    "TempSet": 25.0
  },
  "ch2": {
    "Beta": 3450.0,
    "Bipolar": 0,
    "Control": 0,
    "Current": 0.0,
    "Deriv": 0.0,
    "DerivEn": 0,
    "Integ": 20.0,
    "IntegEn": 1,
    "MaxCurr": 1.0,
    "MaxPwr": 4.0,
    "PGain": 5.0,
    "PGainEn": 1,
    "RefRes": 10000.0,
    "RefTemp": 25.0,
    "Slew": 0.0,
    "SlewEn": 0,
    "TCoefA": 0.000684,
    "TCoefB": 0.00029,
    "TCoefC": 0.0,
    "TempMax": 50.0,
    "TempMin": -5.0,
    "TempSet": 26.0
  },
  "ch3": {
    "Beta": 3450.0,
    "Bipolar": 0,
    "Control": 0,
    "Current": 0.0,
    "Deriv": 0.0,
    "DerivEn": 0,
    "Integ": 20.0,
    "IntegEn": 1,
    "MaxCurr": 1.0,
    "MaxPwr": 4.0,
    "PGain": 5.0,
    "PGainEn": 1,
    "RefRes": 10000.0,
    "RefTemp": 25.0,
    "Slew": 0.0,
    "SlewEn": 0,
    "TCoefA": 0.000684,
    "TCoefB": 0.00029,
    "TCoefC": 0.0,
    "TempMax": 50.0,
    "TempMin": -5.0,
    "TempSet": 26.0
  },
  "ch4": {
    "Beta": 3450.0,
    "Bipolar": 0,
    "Control": 0,
    "Current": 0.0,
    "Deriv": 0.0,
    "DerivEn": 0,
    "Integ": 20.0,
    "IntegEn": 1,
    "MaxCurr": 1.0,
    "MaxPwr": 4.0,
    "PGain": 5.0,
    "PGainEn": 1,
    "RefRes": 10000.0,
    "RefTemp": 25.0,
    "Slew": 0.0,
    "SlewEn": 0,
    "TCoefA": 0.000684,
    "TCoefB": 0.00029,
    "TCoefC": 0.0,
    "TempMax": 50.0,
    "TempMin": -5.0,
    "TempSet": 26.0
  }
}
```

</details>

To import it back to the device, just do:

```python
import slice

qtc = slice.Slice()
# save all channel settings to a JSON file
qtc.load_json('channel_settings.json')
```

## Installation

The package can be installed via pip:

```bash
pip install slice-qtc 
```

## Disclaimer

This is NOT an official package by Vescent Photonics.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
