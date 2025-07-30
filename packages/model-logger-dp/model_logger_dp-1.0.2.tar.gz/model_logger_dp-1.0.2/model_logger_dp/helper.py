help_text = """
====================================================================
              Guide to Using the Model Logger
====================================================================
eg.
import os
import model_logger_dp

os.environ['LOG_PATH'] = './output/log'  # Set the directory for logs

# If you want to save the log with a specific file name, you should set the filename parameter.
# If you do not set the filename parameter, the log will be saved with a datatime name.
logger  = model_logger_dp.ModelLogger(filename='train.log')

# Use the print method to log the message.
print('Hellow World!')

model_logger_dp.log_help()  # Print the help text
model_logger_dp.log_update()  # Print the update message

====================================================================
              Guide to Using the Logger Decorator
====================================================================

This file explains the purpose of each function and provides a guideline
on when to use it for clear and effective console output.


--- FUNCTION: log() ---
Use for general, procedural information that marks the flow of the program.
It's the standard, "everyday" logger.

- When to use:
  - "Loading dataset..."
  - "Saving checkpoint to file..."
  - "Data point 5 of 100 processed."


--- FUNCTION: info() ---
Use for high-level, important milestones or summary information that the
user should definitely see. It's more significant than a standard `log`.

- When to use:
  - "Configuration loaded successfully."
  - "Model training finished. Final accuracy: 95.8%"
  - "Application started."


--- FUNCTION: debug() ---
Use for highly detailed, verbose information that is only useful for developers
when troubleshooting a problem. This output is typically hidden unless a
debug mode is enabled.

- When to use:
  - "Loop iteration 5: current_value = 0.987"
  - "Variable 'x' has shape (256, 512)"
  - "Calling internal function _calculate_metrics()"


--- FUNCTION: warning() ---
Use for issues that are not critical and do not stop the program, but that
the user should be aware of.

- When to use:
  - "The parameter 'learning_rate_decay' is deprecated. Please use 'scheduler' instead."
  - "Optional dependency 'matplotlib' not found. Plotting will be disabled."
  - "Configuration file not found. Using default settings."


--- FUNCTION: error() ---
Use for fatal, unrecoverable errors. This function should print the error
details and then immediately terminate the program.

- When to use:
  - "Could not connect to the database. Exiting."
  - "Required input file 'data.csv' not found."
  - "Critical configuration 'api_key' is missing."


--- FUNCTION: ignore_exception_with_warning() ---
Use this inside a `try...except` block when you catch an exception that you
expect might happen and that you can recover from, but you still want to
log the full error traceback for later inspection. It formats the error as
a warning to distinguish it from a fatal error.

- When to use:
  - A single data point in a large batch is corrupted and fails to process. You want to log the error, skip the point, and continue.
  - A network request to an optional service fails, and you can proceed with a default value.


--- FUNCTION: color_text() ---
A simple utility function to wrap a piece of text in color codes to make
it stand out. Mainly used internally by other logging functions.

- When to use:
  - To highlight a specific word or value within a larger log message.


--- FORMATTING FUNCTIONS ---
(`log_header_double_line`, `log_header_single_line`, `log_header`, `double_line`, `singe_line`)

These are purely for visual formatting. Use them to structure the console
output and make it easier to read.

- When to use:
  - `log_header_double_line`: At the very beginning and end of a major process (e.g., "STARTING TRAINING PIPELINE").
  - `log_header_single_line` / `log_header`: To mark the beginning of a smaller sub-section (e.g., "Data Preprocessing", "Model Evaluation").
  - `double_line` / `singe_line`: To visually separate distinct blocks of log output.
"""

update_text = """
`1.0.2` - Add showing the caller method.
`1.0.1` - Add the logger decorator, improve the logger instance and implement help and update log method.
`1.0.0` - Initial release with basic logging functionality.
"""

def log_help() -> None:
    """
    Print the help text to the console.
    """
    print(help_text)


def log_update() -> None:
    """
    Print the update message of the package to the console.
    """
    print(update_text)


if __name__ == '__main__':
    print(help_text)