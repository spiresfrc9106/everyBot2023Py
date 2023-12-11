# everyBot2023Py

Spires are building a 2023 everybot to learn about robot construction.

This project is to down-convert a Robot Casserole firstRoboPy swerve drive
code base to a 2023 everybot tank drive code base.

See:

1. https://github.com/RobotCasserole1736/firstRoboPy
2. https://github.com/spiresfrc9106/firstRoboPy
3. https://www.118everybot.org/2023-resources
4. https://gitlab.com/robonautseverybot/everybot-2023

The first steps will be to remove the closed loop complexity of the swerve drive system and drive the
4 tank drive brushed motors open loop from the joy sticks.

On the autonomous side this everybot robot will have difficulties doing autonomous the firstRoboPy way
because it:

1. does not have brushed motors on the drive train to provide relative position/velocity
2. does not have absolute encoders on the drive train to provide absolute position/velocity
3. does not have a gyro to steer closed loop to heading

Suggest that we don't have time to work on any autonomous for this robot.

Looking at https://gitlab.com/robonautseverybot/everybot-2023 in Java, the best steps would be to delete
lots of the firstRoboPy code and add in the simple everybot open loop control system.

## Installation

Note that Spires are using:
```cmd
python --version
Python 3.11.6
```

Before developing code on a new computer, perform the following:

1. [Download and install wpilib](https://github.com/wpilibsuite/allwpilib/releases)
2. [Download and install python](https://www.python.org/downloads/)
3. Run these commands:

```cmd
    cd TO_THE_DIRECTORY_THAT_WAS_CLONED
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
```

```cmd
python -m robotpy_installer download-python
python -m robotpy_installer download -r roborio_requirements.txt
```

4. Power-up the robot
5. Make sure that you're on the same network as the robot
5.1 One way is to leave your computer connected to WiFi internet and make a wired Ethernet connection to the robot
5.2 Another way is to connect your computer to the robot over WiFi
6. Optionally reflash your roboRIO like this to get a clean install: https://docs.wpilib.org/en/stable/docs/zero-to-robot/step-3/index.html
7. Install needed python and libraries on the RoboRIO see: https://robotpy.readthedocs.io/en/stable/install/robot.html#install-robotpy

```cmd
python -m robotpy_installer install-python
python -m robotpy_installer install robotpy
python -m robotpy_installer install debugpy
python -m robotpy_installer install robotpy[ctre]
python -m robotpy_installer install robotpy[rev]
python -m robotpy_installer install robotpy[navx]
python -m robotpy_installer install robotpy[pathplannerlib]
```

## Docs

[Click here to see documentation for common libraries](docs/UserAPI).

## The robot website

On a simulator: http://localhost:5805/

On a RoboRIO:

* RobotCasserole: http://10.17.36.2:5805/
* Spires: http://10.91.6.2:5805/

# Interesting commands

## options for pytest


Add a space '--' space and then pytest options: https://docs.pytest.org/en/6.2.x/usage.html

```cmd
python .\robot.py test -- -xvv
python .\robot.py test -- -xvvvv
python .\robot.py test -- -xlsvvvv
```

`-xvv` is the same as `-x -vv`

`-xlsvvvv` is the same as `-x -l -s -vvvv`
```

Details

```cmd
python .\robot.py test -- --tb=auto    # (default) 'long' tracebacks for the first and last
                                       # entry, but 'short' style for the other entries
python .\robot.py test -- --tb=long    # exhaustive, informative traceback formatting
python .\robot.py test -- --full-trace # long traces to be printed on error (longer than --tb=long). It also ensures 
                                       # that a stack trace is printed on KeyboardInterrupt (Ctrl+C). This is very 
                                       # useful if the tests are taking too long and you interrupt them with Ctrl+C to 
                                       # find out where the tests are hanging. By default no output will be shown 
                                       # (because KeyboardInterrupt is caught by pytest). By using this option you make
                                       # sure a trace is shown.
python .\robot.py test -- -l           # pytest lets the stderr/stdout flow through to the console
python .\robot.py test -- -s           # pytest lets the stderr/stdout flow through to the console
python .\robot.py test -- -v           # show each individual test step
python .\robot.py test -- -vv          # pytest shows more details of what faild
python .\robot.py test -- -vvv         # some plugins might make use of -vvv verbosity.
python .\robot.py test -- -vvvv        # some plugins might make use of -vvvv verbosity.
python .\robot.py test -- -x           # stop after first failure
```

# Interesting links

https://github.com/robotpy/mostrobotpy

https://docs.pytest.org/en/7.4.x/

https://pytest.org/en/7.4.x/example/index.html


# TODO Fix these up.

## Deploying to the Robot

`deploy.bat` will deploy all code to the robot. Be sure to be on the same network as the robot.

`.deploy_cfg` contains specific configuration about the deploy process.

## Linting

"Linting" is the process of checking our code format and style to keep it looking nice

`lint.bat` will execute the linter.

`.pylintrc` contains configuration about what checks the linter runs, and what formatting it enforces

## Testing

Run the `Test` configuration in the debugger in vsCode.

## Simulating

Run the `Simulate` configuration in the debugger in vsCode.

## Continuous Integration

Github runs our code on its servers on every commit to ensure our code stays high quality. This is called "Continuous Integration".

`.github/workflows/ci.yml` contains configuration for all the commands that our continuous integration environment.

To minimize frustration and rework, before committing, be sure to:

1. Run the test suite
2. Run `lint.bat` and fix any formatting errors
