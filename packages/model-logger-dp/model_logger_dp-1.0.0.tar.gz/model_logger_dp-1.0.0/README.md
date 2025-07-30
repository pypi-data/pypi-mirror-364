# Model Logger

[![Python >= 3.8](https://img.shields.io/badge/python->=3.8-blue.svg)](https://www.python.org/downloads/release/)

A package that contains method to log the model training log.

The package is an uncompleted package in the version 1.x. Its functions will be gradually improved in subsequent versions.

## How to use


```python
import os
import model_logger_dp

os.environ['LOG_PATH'] = './output/log'  # Set the directory for logs

# If you want to save the log with a specific file name, you should set the filename parameter.
# If you do not set the filename parameter, the log will be saved with a datatime name.
logger  = model_logger_dp.ModelLogger(filename='train.log')

# Use the print method to log the message.
print('Hellow World!')
```

## Update
    `1.0.0` - Initial release with basic logging functionality.

## License

model_logger is MIT licensed. See the [LICENSE](LICENSE) for details.